# Copyright 2011-2012 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

import os
import shutil

from testtools import TestCase
from testtools.matchers import StartsWith

from pkgme.testing import (
    TempdirFixture,
    )

from devportalbinary.binary import (
    BinaryBackend,
    DEFAULT_EXTRA_RULES_TARGETS,
    find_bundled_libraries,
    get_file_type,
    get_file_types,
    get_packages_for_libraries,
    get_shared_library_dependencies,
    guess_dependencies,
    guess_embedded_libs_search_paths,
    guess_executable,
    guess_extra_debian_rules_targets,
    iter_binaries,
    iter_executables,
    needed_libraries_from_objdump,
    NoBinariesFound,
    OVERRIDE_DH_SHLIBDEPS_TEMPLATE,
    UnknownDependency,
    )
from devportalbinary.configuration import load_configuration
from devportalbinary.metadata import (
    MetadataBackend,
    )
from devportalbinary.testing import (
    BackendTests,
    BinaryFileFixture,
    DatabaseFixture,
    get_test_data_dir_path,
    get_test_data_file_path,
    LibsConfigSettings,
    MetadataFixture,
    )


class TestObjDump(TestCase):

    def test_no_binaries(self):
        self.assertRaises(NoBinariesFound, needed_libraries_from_objdump, [])


class FindExecutableTests(TestCase):

    def test_only_one_file_and_it_is_executable(self):
        # If there is only one file and it's executable, find that.
        tempdir = self.useFixture(TempdirFixture())
        tempdir.touch('some-file', mode=0755)
        executables = list(iter_executables(tempdir.path))
        self.assertEqual(['some-file'], executables)

    def test_no_files_at_all(self):
        # iter_executables finds no executables if there are no files at all.
        tempdir = self.useFixture(TempdirFixture())
        executables = list(iter_executables(tempdir.path))
        self.assertEqual([], executables)

    def test_no_executable_files(self):
        # If there are no executable files, iter_executables returns None.
        tempdir = self.useFixture(TempdirFixture())
        tempdir.touch('some-file', mode=0644)
        executables = list(iter_executables(tempdir.path))
        self.assertEqual([], executables)

    def test_directory_is_not_executable_file(self):
        # A directory does not count as an executable file.
        tempdir = self.useFixture(TempdirFixture())
        tempdir.mkdir('directory')
        executables = list(iter_executables(tempdir.path))
        self.assertEqual([], executables)

    def test_finds_executable_in_nested_directory(self):
        # Even if the file is in some nested directory, we are able to find
        # it.
        tempdir = self.useFixture(TempdirFixture())
        tempdir.mkdir('directory')
        tempdir.touch('directory/my-executable', mode=0755)
        executables = list(iter_executables(tempdir.path))
        self.assertEqual(['directory/my-executable'], executables)

    def test_multiple_executables(self):
        # If there are many executables, iter_executables finds them all.
        tempdir = self.useFixture(TempdirFixture())
        tempdir.touch('some-file', mode=0755)
        tempdir.touch('another-file', mode=0755)
        executables = sorted(list(iter_executables(tempdir.path)))
        self.assertEqual(['another-file', 'some-file'], executables)


class GuessExecutableTests(TestCase):

    def test_no_executables(self):
        # If there are no executables to select from, then return None,
        # indicating the fact.
        executable = guess_executable('package-name', iter([]))
        self.assertIs(None, executable)

    def test_only_one_executable(self):
        # If there's only one executable, then return that, since it's
        # probably the main executable for the package.
        executable = guess_executable('package-name', ['whatever'])
        self.assertEqual('whatever', executable)

    def test_exact_package_name_match(self):
        # If there are many executables, but one of them has the same name as
        # the package, then that is probably the main executable.
        executable = guess_executable(
            'package-name', ['whatever', 'package-name'])
        self.assertEqual('package-name', executable)

    def test_exact_package_name_match_in_subdir(self):
        # If there are many executables, but one of them has the same name as
        # the package, then that is probably the main executable, even if it
        # is in a sub-directory.
        executable = guess_executable(
            'package-name', ['whatever', 'subdir/package-name', 'foo'])
        self.assertEqual('subdir/package-name', executable)

    def test_multiple_exact_matches(self):
        # If there are many executables that have the same name as the
        # package, then the one that is the least nested is our best guess.
        executable = guess_executable(
            'package-name', [
                'whatever', 'a/b/c/d/e/subdir/package-name', 'foo',
                'subdir/package-name'])
        self.assertEqual('subdir/package-name', executable)

    def test_different_case_match(self):
        # If one of the executables has the same name as the package, but
        # spelled with different case, then that is our best guess.
        executable = guess_executable(
            'packagename', [
                'whatever', 'a/b/c/d/e/subdir/packagename', 'foo',
                'subdir/PackageName'])
        self.assertEqual('subdir/PackageName', executable)

    def test_many_executables(self):
        # If there are many executables, and their names have no particular
        # relationship to the package name, then just pick the top-most
        # one. If there's more than one, take the alphabetically sorted.
        executable = guess_executable(
            'package-name', ['dir/x', 'dir/sub/y', 'z', 'a'])
        self.assertEqual('a', executable)

    def test_fuzzy_mach(self):
        executable = guess_executable(
            'bittriprunner', ['install', 'bit.trip.runner/bit.trip.runner'])
        self.assertEqual('bit.trip.runner/bit.trip.runner', executable)


class GetFileTypeTests(TestCase):

    def test_plain_text(self):
        tempdir = self.useFixture(TempdirFixture())
        tempdir.create_file('foo.txt', 'boring content\n')
        file_type = get_file_type(tempdir.abspath('foo.txt'))
        self.assertEqual('ASCII text', file_type)

    def test_data(self):
        file_type = get_file_type(get_test_data_file_path('data-file', 'foo.data'))
        self.assertEqual('data', file_type)

    def test_elf_binary(self):
        binary_path = get_test_data_file_path('hello', 'hello')
        file_type = get_file_type(binary_path)
        self.assertThat(file_type, StartsWith('ELF'))

    def test_elf_library(self):
        binary_path = get_test_data_file_path('simple', 'simple.so.1')
        file_type = get_file_type(binary_path)
        self.assertThat(file_type, StartsWith('ELF'))

    def test_multiple(self):
        tempdir = self.useFixture(TempdirFixture())
        tempdir.create_file('foo.txt', 'boring content\n')
        file_types = get_file_types(
            [tempdir.abspath('foo.txt'),
             get_test_data_file_path('data-file', 'foo.data')])
        self.assertEqual(['ASCII text', 'data'], file_types)

    def test_no_files_given(self):
        self.assertEqual([], get_file_types([]))
        self.assertEqual([], get_file_types(iter([])))


class IterBinariesTests(TestCase):

    def test_no_binaries(self):
        tempdir = self.useFixture(TempdirFixture())
        self.assertEqual([], list(iter_binaries(tempdir.path)))

    def test_some_binaries(self):
        path = get_test_data_dir_path('multi-binary')
        binaries = sorted(iter_binaries(path))
        self.assertEqual(
            [os.path.join(path, 'subdir', 'hello'),
             os.path.join(path, 'subdir', 'hello-missing-deps'),
             os.path.join(path, 'subdir', 'simple.so.1')],
            binaries)


class GetSharedLibraryDependenciesTests(TestCase):

    def test_get_shared_library_dependencies(self):
        hello = get_test_data_file_path('hello', 'hello')
        deps = get_shared_library_dependencies([hello])
        self.assertEqual(set(['libc.so.6']), deps)


class FindBundledLibrariesTests(TestCase):

    def test_find_bundlded_libraries_one_found(self):
        tempdir = self.useFixture(TempdirFixture())
        # pretend we have this libraries bundled in our path
        embedded_libnames = ["libfoo.so.1", "libbar.so.2"]
        for libname in embedded_libnames:
            with open(os.path.join(tempdir.path, libname), "w"):
                pass
        # the libraries required by the mystical binary
        libraries_required = embedded_libnames + [ "libc6.so.1", "libjml.so" ]
        # ensure that its really found
        found = find_bundled_libraries(tempdir.path, libraries_required)
        self.assertEqual(
            { "libfoo.so.1" : ["."], "libbar.so.2" : ["."]}, found)

class GuessDependenciesTests(TestCase):

    def test_guess_dependencies(self):
        db = self.useFixture(DatabaseFixture()).db
        db.update_source_package('eglibc', [[('libc.so.6', 'libc6')]])
        deps = guess_dependencies(get_test_data_dir_path('hello'))
        self.assertEqual(set(['libc6']), deps)

    def test_guess_dependencies_error_on_unknown_dependency(self):
        self.useFixture(DatabaseFixture())
        e = self.assertRaises(UnknownDependency,
                guess_dependencies, get_test_data_dir_path('hello'))
        self.assertEqual('Can\'t find dependency for "libc.so.6".', str(e))


class GuessEmbeddedSearchPathsTests(TestCase):

    def test_guess_embedded_search_path(self):
        bundled_lib_test_dir = get_test_data_dir_path('bundled_library')
        paths = guess_embedded_libs_search_paths(bundled_lib_test_dir)
        self.assertEqual(set(["."]), paths)


class BinaryBackendTests(BackendTests):

    BACKEND = BinaryBackend

    def test_want_with_metadata_and_binaries(self):
        # If we detect a binary, then we score 10. The way we determine if
        # something is a binary is if it has a devportal-metadata.json in its
        # top-level.
        path = self.useFixture(MetadataFixture({})).path
        self.useFixture(BinaryFileFixture(path))
        backend = self.make_backend(path)
        self.assertEqual(10, backend.want())

    def test_want_with_just_metadata(self):
        # If something just has a metadata file but no binaries it is
        # not wanted
        path = self.useFixture(MetadataFixture({})).path
        backend = self.make_backend(path)
        self.assertEqual(0, backend.want())

    def test_want_without_metadata(self):
        # If there is no metadata file then we score 0 as we don't want
        # to act on it.
        path = self.useFixture(TempdirFixture()).path
        self.useFixture(BinaryFileFixture(path))
        backend = self.make_backend(path)
        self.assertEqual(0, backend.want())

    def test_description(self):
        # The binary backend uses the package description that's in the
        # metadata.
        expected_description = self.getUniqueString()
        backend = self.make_backend()
        description = backend.get_description(
            {MetadataBackend.DESCRIPTION: expected_description})
        self.assertEqual(expected_description, description)

    def test_no_description(self):
        # If no description is provided in the metadata then the description
        # in the package info is just an empty string.
        backend = self.make_backend()
        description = backend.get_description({})
        self.assertEqual('', description)

    def test_build_depends(self):
        # Make sure there's a database.
        backend = self.make_backend()
        shutil.copy(
            get_test_data_file_path('hello', 'hello'), backend.path)
        db = self.useFixture(DatabaseFixture()).db
        db.update_source_package('eglibc', [[('libc.so.6', 'libc6')]])
        expected_deps = ', '.join(guess_dependencies(backend.path))
        build_deps = backend.get_build_depends(None)
        self.assertEqual(expected_deps, build_deps)

    def test_depends(self):
        backend = self.make_backend()
        depends = backend.get_depends(None)
        self.assertEqual('${shlibs:Depends}, ${misc:Depends}', depends)

    def test_executable_is_best_guess(self):
        package_name = self.getUniqueString()
        tempdir = self.useFixture(TempdirFixture())
        tempdir.mkdir('whatever')
        executables = [
            'whatever/not-the-best',
            'this-one-is-best',
            ]
        for executable in executables:
            tempdir.touch(executable, 0755)
        best = guess_executable(package_name, executables)
        backend = self.make_backend(tempdir.path)
        self.assertEqual(
            '/opt/%s/%s' % (package_name, best),
            backend.get_executable(package_name))

    def test_config_glue_lib_overrides(self):
        test_libs = {
            'libasound.so.2': 'libasound2',
            'libGL.so.1': 'libgl1-mesa-glx',
            'libfoo.so.2': 'libfoo',
            }
        self.useFixture(LibsConfigSettings(test_libs))
        conf = load_configuration()
        self.assertEqual(conf.options.libraries_overrides, test_libs)

    def test_get_lib_overrides_for_packages_for_libraries(self):
        # The configuration file overrides the found library dependencies.
        db = self.useFixture(DatabaseFixture()).db
        db.update_source_package('foo', [
                [('libasound.so.2', 'libfoo')],
                [('libasound.so.2', 'libbar')],
                ])
        self.assertEqual(
            get_packages_for_libraries(["libasound.so.2"], "i386"),
            set(["libasound2"]))

    def test_architecture(self):
        backend = self.make_backend()
        conf = load_configuration()
        self.assertEqual(
            backend.get_architecture(metadata={}), 
            "".join(conf.options.architectures_supported))

    def test_get_extra_targets_no_bundled_libs(self):
        package_name = self.getUniqueString()
        path = self.getUniqueString()
        self.assertEqual(
            guess_extra_debian_rules_targets(package_name, path, lambda l: []),
            DEFAULT_EXTRA_RULES_TARGETS)

    def test_get_extra_targets_bundled_libs(self):
        package_name = "a-pkgname"
        path = self.getUniqueString()
        ld_search_path = ["x86/lib"]
        self.assertEqual(
            DEFAULT_EXTRA_RULES_TARGETS+OVERRIDE_DH_SHLIBDEPS_TEMPLATE % (
                "$(CURDIR)/debian/%s/opt/%s/%s" % (
                    package_name, package_name, ld_search_path[0])),
            guess_extra_debian_rules_targets(
                package_name, path, lambda l: ld_search_path))
