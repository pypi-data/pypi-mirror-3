# Copyright 2011 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

"""Things to help package binary tarballs.

HIGHLY EXPERIMENTAL. USE AT YOUR OWN PERIL.

At the moment, we are assuming a great many things about these binary
tarballs.

* That they represent some sort of application to be run from an Ubuntu
  desktop

* Specifically, that although they might have many executables, only one is
  the "main executable" mentioned in the 'desktop' file

* They are written in C or C++ and that all dependencies can be determined
  by inspecting the included object files

* That the entire contents of the tarball can be copied into
  /opt/<package-name> and run from there

* That we have a metadata file, called 'devportal-metadata.json', in JSON.
  See ``MetadataBackend``.

The expectation is that this metadata file is generated from the developer
portal.
"""

__all__ = [
    'BinaryBackend',
    'guess_executable',
    'iter_executables',
   ]


import os
import subprocess

from pkgme.errors import PkgmeError
from pkgme.run_script import run_subprocess
from pkgme import trace

from devportalbinary.configuration import load_configuration
from devportalbinary.database import PackageDatabase
from devportalbinary.metadata import MetadataBackend


OVERRIDE_DH_STRIP_TEMPLATE = """
override_dh_strip:
\t# pkgme-binary does not call dh_strip as this may break binary-only apps
"""

# the overrides template for a dh_shlibdeps
OVERRIDE_DH_SHLIBDEPS_TEMPLATE = """
override_dh_shlibdeps:
\tdh_shlibdeps -l%s
"""


# the default extra debian/rules targets
DEFAULT_EXTRA_RULES_TARGETS = OVERRIDE_DH_STRIP_TEMPLATE


class NoBinariesFound(PkgmeError):
    """Raised when we cannot find any binaries to examine for dependencies.
    """


class UnknownDependency(PkgmeError):
    """Raised when we do not know which dependency to add."""


class UnsupportedArchitecture(PkgmeError):
    """Raised when we find a unsupported architecture."""


# This code is taken from:
#   http://code.activestate.com/recipes/576874-levenshtein-distance/
# (MIT licensed)
def levenshtein(s1, s2):
    """Calculate the Levenshtein distance from s1 to s2.

    The Levenshtein distance is the minimum number of edits needed to
    transform one string into the other, with the allowable edit operations
    being insertion, deletion, or substitution of a single character.

    The smaller the distance, the more "similar" the strings are.
    """
    l1 = len(s1)
    l2 = len(s2)

    matrix = [range(l1 + 1)] * (l2 + 1)
    for zz in range(l2 + 1):
        matrix[zz] = range(zz,zz + l1 + 1)
    for zz in range(0,l2):
        for sz in range(0,l1):
            if s1[sz] == s2[zz]:
                matrix[zz+1][sz+1] = min(matrix[zz+1][sz] + 1,
                                         matrix[zz][sz+1] + 1,
                                         matrix[zz][sz])
            else:
                matrix[zz+1][sz+1] = min(matrix[zz+1][sz] + 1,
                                         matrix[zz][sz+1] + 1,
                                         matrix[zz][sz] + 1)
    return matrix[l2][l1]


def _rank_executable(package_name, executable):
    """Rank ``executable`` as the main executable for ``package_name``.

    :return: Something, anything, that can be used as a sort key.  Lower means
        more likely to be the main executable.
    """

    def score_levenshtein(name):
        return levenshtein(package_name.lower(), name.lower())

    def score_path(executable):
        # The deeper the path, the less likely it is to be the one.
        return executable.count('/')

    name = os.path.basename(executable)
    # The alpha-sorting of the base name is a tie-breaker.
    return (
        score_levenshtein(name),
        score_path(executable),
        name,
        )


def guess_executable(package_name, executables):
    """
    From a list of executables, guess which one is likely to be the main
    executable.
    """

    def rank(executable):
        # Currying _rank_executable.
        return _rank_executable(package_name, executable)

    try:
        return sorted(executables, key=rank)[0]
    except IndexError:
        return None


def iter_executables(path):
    """Iterate through all executable files under 'path'.

    Paths yielded will be relative to 'path'. Directories will *not* be
    yielded. "Executable" is determined by filesystem permissions.
    """
    for root, dirs, files in os.walk(path):
        for filename in files:
            file_path = os.path.join(root, filename)
            if os.access(file_path, os.X_OK):
                yield os.path.relpath(file_path, path)


def get_file_type(path):
    return get_file_types([path])[0]


def get_file_types(paths):
    paths = list(paths)
    if not paths:
        return []
    cmd = ['file', '-b'] + paths
    return subprocess.Popen(
        cmd, stdout=subprocess.PIPE).communicate()[0].splitlines()


OBJDUMP = '/usr/bin/objdump'

def needed_libraries_from_objdump(binary_paths):
    binary_paths = list(binary_paths)
    if not binary_paths:
        raise NoBinariesFound()
    conf = load_configuration()
    cmd = [OBJDUMP, '-f', '-p'] + binary_paths
    output = run_subprocess(cmd)
    libraries = {}
    last_line_was_blank = True
    for line in output:
        this_line_blank = (line.strip() == '')
        if last_line_was_blank and this_line_blank:
            try:
                current_binary = binary_paths.pop(0)
            except IndexError:
                break
            libraries[current_binary] = []
        if line.startswith('  NEEDED'):
            libraries[current_binary].append(line.split()[1])
        elif line.startswith('architecture: '):
            # so... i386 is reported as "i386"
            # *but* amd64 as "i386:x86-64"
            architecture = line.partition(":")[2].partition(",")[0].strip()
            if architecture not in conf.options.architectures_supported:
                raise UnsupportedArchitecture(
                    "Can not handle '%s'" % architecture)
        last_line_was_blank = this_line_blank
    return libraries


def get_shared_library_dependencies(paths):
    """Find all of the shared libraries depended on the ELF binaries in 'paths'.
    """
    so_names = set()
    libraries = needed_libraries_from_objdump(paths)
    for libs in libraries.values():
        for name in libs:
            so_names.add(name)
    return so_names


def iter_binaries(path):
    """Find all of the ELF binaries underneath 'path'."""

    def is_binary(file_type):
        return file_type.startswith('ELF')

    for root, dirs, files in os.walk(path):
        paths = [os.path.join(root, filename) for filename in files]
        types = get_file_types(paths)
        for file_path, file_type in zip(paths, types):
            if is_binary(file_type):
                yield file_path


def get_packages_for_libraries(library_names, arch):
    conf = load_configuration()
    lib_overrides = conf.options.libraries_overrides
    db = PackageDatabase.create()
    deps = set()
    for lib in library_names:
        # ensure that overrides always "trump" the existing set if they
        # are found
        if lib in lib_overrides:
            new_deps = set([lib_overrides[lib]])
            trace.log("found dependencies '%s' for lib '%s' via override" % (
                new_deps, lib))
        else:
            new_deps = db.get_dependencies(lib)
            trace.log("found dependencies '%s' for lib '%s'" % (
                new_deps, lib))

        if not new_deps:
            raise UnknownDependency('Can\'t find dependency for "%s".' % lib)
        deps |= new_deps
    return deps


def find_bundled_libraries(path, libraries):
    """Find the directories that contain bundled library paths

    Returns a dict that maps the library name to the relative path
    (relative to the root 'path') where the library is found.
    """
    libraries_to_path = {}
    for dirpath, dirname, filenames in os.walk(path):
        for libname in list(libraries):
            if libname in filenames:
                lib_path = os.path.relpath(dirpath, path)
                if not libname in libraries_to_path:
                    libraries_to_path[libname] = []
                libraries_to_path[libname].append(lib_path)
    return libraries_to_path


def guess_embedded_libs_search_paths(
    path,
    library_finder=needed_libraries_from_objdump,
    libraries_to_deps=get_packages_for_libraries):
    binaries = iter_binaries(path)
    libraries = get_shared_library_dependencies(binaries)
    libraries_to_paths = find_bundled_libraries(path, libraries)
    # the values are a list of lists of paths, so we need to "flatten" it
    # here
    paths = set([
        path for pathlist in libraries_to_paths.values() for path in pathlist])
    return paths


def guess_extra_debian_rules_targets(
    package_name,
    path,
    embedded_libs_finder=guess_embedded_libs_search_paths):
    embedded_paths = embedded_libs_finder(path)
    extra_targets = DEFAULT_EXTRA_RULES_TARGETS
    if embedded_paths:
        base_dir = "$(CURDIR)/debian/%(package_name)s/opt/" \
            "%(package_name)s/" % { 'package_name' : package_name }
        ld_search_path = build_ld_library_search_path(
            base_dir, embedded_paths)
        extra_targets += OVERRIDE_DH_SHLIBDEPS_TEMPLATE % ld_search_path
    return extra_targets


def guess_dependencies(
    path,
    library_finder=needed_libraries_from_objdump,
    libraries_to_deps=get_packages_for_libraries):
    binaries = iter_binaries(path)
    libraries = get_shared_library_dependencies(binaries)
    # find/filter out the embedded libs
    libraries_to_paths = find_bundled_libraries(path, libraries)
    libraries = set(libraries) - set(libraries_to_paths.keys())
    # go over the rest
    deps = libraries_to_deps(libraries, 'i386')
    return deps


def print_dependencies():
    deps = guess_dependencies('.')
    for dep in deps:
        print dep
    return 0


def print_executable():
    cwd = os.getcwd()
    print guess_executable(os.path.dirname(cwd), iter_executables(cwd))
    return 0


def build_ld_library_search_path(basedir, relative_dirs):
    """Return a string suitable for the LD_LIBRARY_PATH variable"""
    return os.pathsep.join(
        ["%s%s" % (basedir, p) for p in relative_dirs])


class BinaryBackend(MetadataBackend):
    """A backend that uses MyApps metadata to build a package for a binary."""

    # XXX: jml just doing this because iamfuzz does. Need to either experiment
    # or consult expert.
    DEPENDS = '${shlibs:Depends}, ${misc:Depends}'

    def get_architecture(self, metadata):
        # XXX: once we scan more than one architecture we need to actually
        #      pick the ones that we build for (e.g. set to "i386 amd64")
        #      But currently our database only does i386 so its ok for now
        conf = load_configuration()
        return "".join(conf.options.architectures_supported)

    def get_build_depends(self, metadata):
        return ', '.join(guess_dependencies(self.path))

    def get_depends(self, metadata):
        return self.DEPENDS

    def get_executable(self, package_name):
        executable = guess_executable(package_name, iter_executables(self.path))
        return '/opt/%s/%s' % (package_name, executable)

    def get_extra_targets(self, metadata):
        package_name = self.get_package_name(metadata)
        return guess_extra_debian_rules_targets(package_name, self.path)

    def want(self):
        if (self.has_metadata_file()
            and len(list(iter_binaries(self.path))) > 0):
            return 10
        else:
            return 0
