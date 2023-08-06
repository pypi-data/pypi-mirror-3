# Copyright 2011-2012 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

"""A pkgme backend that gets much of its data from MyApps.

The main idea behind this backend is that it looks for a file,
'devportal-metadata.json', created with data provided by users of MyApps.  It
then uses this data, along with inferences from submitted files to create a
Debian package.
"""

__all__ = [
    'MetadataBackend',
    ]

import json
import os
import tempfile

import Image

from pkgme.info_elements import (
    ApplicationName,
    Architecture,
    BuildDepends,
    Categories,
    Depends,
    Description,
    Distribution,
    Executable,
    ExtraFiles,
    ExtraFilesFromPaths,
    ExtraTargets,
    Icon,
    License,
    Maintainer,
    PackageName,
    Homepage,
    TagLine,
    Version,
    WorkingDirectory,
    )
from pkgme.package_files import (
    DEBIAN_DIR,
    Desktop,
    )
from pkgme.project_info import DictInfo

from .backend import (
    backend_script,
    convert_info,
    )
from .utils import get_latest_stable_ubuntu_distroseries


# Temporary conditional code to allow us to deploy new pkgme-devportal without
# relying on unreleased pkgme changes.  When ExplicitCopyright is in a
# releasea version of pkgme, we should bump our minimum dependency to that
# released version and delete this conditional, importing ExplicitCopyright
# directly.
try:
    from pkgme.info_elements import ExplicitCopyright as EC_pyflakes_sucks
    ExplicitCopyright = EC_pyflakes_sucks
except ImportError:
    ExplicitCopyright = None


# XXX: is this the right place?
LINTIAN_OVERRIDES_TEMPLATE = """
#Partner package contents belong in /opt
%(package_name)s: dir-or-file-in-opt

#Partner package may content embedded libs
%(package_name)s: embedded-library

#Bullet lists
%(package_name)s: extended-description-line-too-long
"""


# map devportals license understanding to the common-licenses of debian
# see also src/devportal/models.py:1324
LICENSE_MAPPING = {
    'Apache License' : 'Apache-2.0',
    'BSD License (Simplified)' : 'BSD',
    'GNU GPL v2' : 'GPL-2',
    "GNU GPL v3" : 'GPL-3',
    "GNU LGPL v2.1" : "LGPL-2.1",
    "GNU LGPL v3" :  "LGPL-3",
    "Artistic License 1.0" : "Artistic",
    "Proprietary" : "Proprietary\n All rights reserved.",
}


def get_install_basedir(package_name):
    return '/opt/%s' % package_name


def get_install_map(package_name, path, include_desktop=False, icons=None):
    if not icons:
        icons = {}
    installation = {}
    # Make it a relative path to fit with the standard for install files
    basedir = get_install_basedir(package_name).lstrip('/')
    # Sorting not actually needed for functionality, but makes the tests more
    # reliable.
    for filename in sorted(os.listdir(path)):
        if filename in (DEBIAN_DIR, MetadataBackend.METADATA_FILE):
            # We don't want to install the 'debian/' directory or the metadata
            # file.
            continue
        installation[filename] = basedir
    for resolution, path in icons.items():
        # XXX: This means that the basename of 'path' has to match the value
        # of the Icon field in the desktop file.  Seems fragile.
        installation[path] = 'usr/share/icons/hicolor/%s/apps' % (resolution,)
    if include_desktop:
        desktop = 'debian/%s.desktop' % (package_name,)
        installation[desktop] = 'usr/share/applications'
    return installation


def format_install_map(install_map):
    # Sorting not actually needed for functionality, but makes the tests more
    # reliable.
    lines = sorted('%s %s' % (src, dst) for (src, dst) in install_map.items())
    # Ending the file with a newline is basic good manners.
    lines.append('')
    return '\n'.join(lines)


def get_install_file(package_name, path, include_desktop=False, icons=None):
    """Generate the install file for 'package_name'."""
    install_map = get_install_map(
        package_name, path, include_desktop=include_desktop, icons=icons)
    return format_install_map(install_map)


def get_desktop_file(package_name, application_name, executable,
                     tagline=None, categories=None, icon=None,
                     working_directory=None):
    """Get the desktop file for the package.

    :return: A ``Desktop``.
    """
    categories_string = ""
    if categories:
        # desktop files expect a trailing ";"
        categories_string = ";".join(categories) + ";"
    info = {
        PackageName.name: package_name,
        ApplicationName.name: application_name,
        Executable.name: executable,
        TagLine.name: tagline,
        Categories.name: categories_string,
        Icon.name: icon,
        WorkingDirectory.name: working_directory,
        }
    return Desktop.from_info(DictInfo(info))


def convert_icon(icon_path, new_size):
    """Takes a icon_path and converts it to the new size

    :return: path of the newly created icon of the requested size
    """
    im = Image.open(icon_path)
    tmp_icon = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    size = get_icon_size_from_string(new_size)
    out = im.resize((size, size))
    out.save(tmp_icon.name)
    return tmp_icon.name


def get_icon_size_from_string(s):
    """Return a integer size from a string of the form 'WxH' ('48x48')

    :raise ValueError: if we're given a non-square size.

    :return: The size of the icon.
    """
    w, h = s.split("x")
    if w != h:
        raise ValueError("Got ('%s', '%s') size but only square sizes "
                         "are supported", w, h)
    return int(w)


def get_package_files(path, metadata):
    """Return a set of files under path that belong to the package.

    Only returns the top level, does not recurse.
    """
    # XXX: This implies that we're doing exact string matching on the
    # paths in the metadata and the results of os.listdir.  We actually
    # want to exclude the icons if they are the same file, not if the
    # strings happen to be equal.
    excluded_files = set([MetadataBackend.METADATA_FILE, 'debian'])
    excluded_files |= set(metadata.get(MetadataBackend.ICONS, {}).values())
    return set(os.listdir(path)) - excluded_files


def load_json(path):
    """Load JSON from `path`.

    :param path: the path to load the JSON from.
    :return: (json, err) where json is the deserialized contents of the file,
        or None if it didn't exist or didn't contain json. If json is
        None then err will be a description of why it couldn't be loaded.
    """
    if not os.path.exists(path):
        return None, 'No metadata file'
    try:
        with open(path) as f:
            metadata = json.load(f)
    except ValueError:
        # Not a JSON file.
        return None, 'Metadata file is not valid JSON'
    return metadata, None


class MetadataBackend(object):
    """A backend that is mostly powered by metadata from MyApps."""

    # Where the metadata file lives.
    METADATA_FILE = 'devportal-metadata.json'

    # Keys found in the metadata file.
    # XXX: These duplicate the schema found in pkgme-service.
    APPLICATION_NAME = 'name'
    CATEGORIES = 'categories'
    DESCRIPTION = 'description'
    ICONS = 'icons'
    LICENSE = 'license'
    MAINTAINER = 'maintainer'
    PACKAGE_NAME = 'package_name'
    SUGGESTED_PACKAGE_NAME = 'suggested_package_name'
    SUGGESTED_VERSION = 'suggested_version'
    TAGLINE = 'tagline'
    # its "Homepage" in the deb package but "website" on the devportal
    HOMEPAGE = 'website'

    # the icon size that must be present
    REQUIRED_ICON_SIZE = '48x48'

    def __init__(self, path, metadata):
        """Construct a ``MetadataBackend``."""
        self.path = path
        self.metadata = metadata

    def _calculate_info_element(self, info_element, *args, **kwargs):
        PREFIX = 'get_'
        method = getattr(self, '%s%s' % (PREFIX, info_element.name))
        return method(*args, **kwargs)

    def get_application_name(self):
        """Get the application name for the package.

        Used in the desktop file.
        """
        # XXX: Probably can assume that this is always present, since MyApps
        # requires it.  Leaving as optional for now on the hunch that it will
        # smooth out the deployment process or at least the branch size.
        try:
            return self.metadata[self.APPLICATION_NAME]
        except KeyError:
            try:
                return self._calculate_info_element(
                    PackageName).capitalize()
            except AssertionError:
                raise AssertionError("Could not determine application name")

    def get_architecture(self):
        """Get the architecture for the package.

        :return: The architecture tag, or None if no architecture is
            specified.
        """
        raise NotImplementedError(self.get_architecture)

    def get_build_depends(self):
        """Get the build dependencies of the package."""
        raise NotImplementedError(self.get_build_depends)

    def get_depends(self):
        """Get the dependencies for the package."""
        raise NotImplementedError(self.depends)

    def get_description(self):
        """Get the package description."""
        return self.metadata.get(self.DESCRIPTION, '')

    def get_distribution(self):
        return get_latest_stable_ubuntu_distroseries()

    def get_executable(self, package_name):
        """Return the path to the executable."""
        raise NotImplementedError(self.get_executable)

    def get_explicit_copyright(self):
        return None

    def get_extra_targets(self):
        """Return any extra debian/rules targets. """
        return ""

    def _get_lintian_overrides(self, package_name):
        return LINTIAN_OVERRIDES_TEMPLATE % {'package_name' : package_name,}

    def get_extra_files(self, package_name):
        """Get the extra files for the package.

        Assumes that the only extra files are a desktop file and an install
        file.  Delegates to ``get_desktop_file`` for the desktop file.
        """
        icons = {}
        icon_map = self._get_icon_map(package_name)
        for resolution in icon_map:
            dst, src = icon_map[resolution]
            icons[resolution] = dst
        install_file = get_install_file(package_name, self.path, True, icons)
        executable = self.get_executable(package_name)
        application_name = self._calculate_info_element(
            ApplicationName)
        if self.ICONS in self.metadata:
            icon = package_name
        else:
            icon = None
        desktop_file = get_desktop_file(
            package_name,
            application_name,
            executable,
            tagline=self.metadata.get(self.TAGLINE, ''),
            categories=self.metadata.get(self.CATEGORIES, ''),
            icon=icon,
            working_directory=get_install_basedir(package_name))
        lintian_override_content = self._get_lintian_overrides(package_name)
        return {
            # XXX: Hardcoded literal attack!
            'debian/install': install_file,
            'debian/%s.desktop' % (package_name,): desktop_file.get_contents(),
            'debian/%s.lintian-overrides' % (package_name,) : lintian_override_content,
            }

    def get_extra_files_from_paths(self):
        """Get extra, binary files for the package."""
        package_name = self._calculate_info_element(PackageName)
        extra_files = self._get_extra_icon_files_from_paths(package_name)
        return extra_files

    def _get_extra_icon_files_from_paths(self, package_name):
        icon_map = self._get_icon_map(package_name)
        return dict(icon_map.values())

    def _pick_closest_icon_resolution_for_size(self, icon_sizes_list, size):
        """Find the best matching resolution for the given "size"

        :return: a string with the closest icon match
        """
        size_as_int = get_icon_size_from_string(size)
        sorted_sizes = sorted(icon_sizes_list, key=get_icon_size_from_string)
        # try to find the first bigger icon than "size"
        for size_str in sorted_sizes:
            if get_icon_size_from_string(size_str) > size_as_int:
                return size_str
        # if nothing bigger is found, return the biggest we have
        return sorted_sizes[-1]

    def _ensure_required_icon_size(self, required_size):
        """ Ensure that the size "required_size" is part of the ICONS
            metadata and create a new icon if needed.

            Note that this modifies metadata[self.ICONS].
        """
        icons = self.metadata.get(self.ICONS, {})
        if not icons or required_size in icons:
            return
        best_resolution = self._pick_closest_icon_resolution_for_size(
            icons.keys(), required_size)
        new_path = convert_icon(icons[best_resolution], required_size)
        icons[required_size] = new_path
        self.metadata[self.ICONS] = icons

    def _get_icon_map(self, package_name):
        """Return a dict mapping resolutions to paths.

        Each resolution is mapped to two paths: a relative debian path, which
        is where pkgme will store the icon, and an absolute path, which is
        where the icon can be found.

        Because the icons will be installed from the relative debian path, the
        basename of that path sans extension *must* be equal to the value of
        the Icon field in the desktop file, which is set to the package name
        in the default implementation.

        :return: {resolution: (dst, src), ...}
        """
        # ensure that we have the required icon size
        self._ensure_required_icon_size(self.REQUIRED_ICON_SIZE)

        icon_map = {}
        for resolution, path in self.metadata.get(self.ICONS, {}).items():
            src = os.path.normpath(os.path.join(self.path, path))
            ext = os.path.splitext(path)[1]
            dst = 'debian/icons/%s/%s%s' % (resolution, package_name, ext)
            icon_map[resolution] = (dst, src)

        return icon_map

    def get_homepage(self):
        return self.metadata.get(self.HOMEPAGE, None)

    def get_license(self):
        devportal_license = self.metadata.get(self.LICENSE, "unknown")
        return LICENSE_MAPPING.get(devportal_license, devportal_license)

    def get_maintainer(self):
        return self.metadata.get(self.MAINTAINER, None)

    def get_package_name(self):
        """Get the package name."""
        package_name_sources = [
            self.PACKAGE_NAME,
            self.SUGGESTED_PACKAGE_NAME,
            self.APPLICATION_NAME,
            ]
        for source in package_name_sources:
            package_name = self.metadata.get(source, None)
            if package_name:
                return package_name
        raise AssertionError("Could not determine package name")

    def get_version(self):
        """Get the version of the package."""
        return self.metadata.get(self.SUGGESTED_VERSION, None)

    @classmethod
    def get_metadata_path(cls, path):
        return os.path.join(path, cls.METADATA_FILE)

    @classmethod
    def get_metadata(cls, path):
        """Get the metadata for this backend.

        Looks for the metadata in a file called ``METADATA_FILE`` in the
        directory given to the constructor.

        :return: A dict of metadata.
        """
        metadata, err = load_json(cls.get_metadata_path(path))
        if metadata is None:
            raise AssertionError(err)
        return metadata

    def get_info(self):
        """Return a dict of InfoElements given 'metadata'.

        This is the work-horse method of the backend. It takes a dict of
        metadata, as extracted from a devportal-metadata.json file, and
        converts it into a dictionary mapping InfoElements to their actual
        values.

        This dictionary will then be dumped as the JSON output of 'all_info',
        substituting the InfoElements for their names.
        """
        COMPULSORY_ELEMENTS = [
            BuildDepends,
            Depends,
            Description,
            License,
            PackageName,
            ]
        OPTIONAL_ELEMENTS = [
            Architecture,
            Distribution,
            ExtraFilesFromPaths,
            ExtraTargets,
            Maintainer,
            Version,
            Homepage,
            ]
        # Temporary conditional code to allow us to deploy new pkgme-devportal
        # without relying on unreleased pkgme changes.  When ExplicitCopyright
        # is in a releasea version of pkgme, we should bump our minimum
        # dependency to that released version and delete this conditional,
        # including ExplicitCopyright in the OPTIONAL_ELEMENTS list.
        if ExplicitCopyright:
            OPTIONAL_ELEMENTS.append(ExplicitCopyright)
        info = {}
        for element in COMPULSORY_ELEMENTS:
            info[element] = self._calculate_info_element(element)
        for element in OPTIONAL_ELEMENTS:
            value = self._calculate_info_element(element)
            if value:
                info[element] = value
        # Special-case ExtraFiles since it needs PackageName.
        info[ExtraFiles] = self._calculate_info_element(
            ExtraFiles, info[PackageName])
        return info

    @classmethod
    def want(cls, path):
        """How relevant this backend is."""
        metadata, err = load_json(cls.get_metadata_path(path))
        if err is not None:
            return {'score': 0, 'reason': err}
        return cls.want_with_metadata(path, metadata)

    @classmethod
    def want_with_metadata(self, path, metadata):
        """How relevant this backend is, after metadata has been found.

        Specific backends should override this.
        """
        raise NotImplementedError(self.want_with_metadata)


def make_want_fn(backend_cls):
    def metadata_want(path):
        return backend_cls.want(path)
    metadata_want.__name__ = '{}_want'.format(backend_cls.__name__)
    return backend_script(metadata_want)


def make_all_info_fn(backend_cls):
    def metadata_all_info(path):
        metadata = backend_cls.get_metadata(path)
        backend = backend_cls(path, metadata)
        info = backend.get_info()
        return convert_info(info)
    metadata_all_info.__name__ = '{}_all_info'.format(backend_cls.__name__)
    return backend_script(metadata_all_info)
