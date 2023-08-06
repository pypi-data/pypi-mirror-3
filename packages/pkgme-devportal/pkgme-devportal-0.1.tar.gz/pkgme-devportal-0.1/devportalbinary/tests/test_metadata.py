# Copyright 2011-2012 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

import json
from StringIO import StringIO
import os

from mock import patch

from pkgme.info_elements import (
    Architecture,
    BuildDepends,
    Description,
    Depends,
    Distribution,
    ExtraFiles,
    ExtraFilesFromPaths,
    Homepage,
    License,
    Maintainer,
    PackageName,
    Version,
    )
from pkgme.package_files import (
    DEBIAN_DIR,
    )
from pkgme.testing import (
    AreDesktopValuesFor,
    TempdirFixture,
    )
from testtools import TestCase

from devportalbinary.metadata import (
    format_install_map,
    get_desktop_file,
    get_install_basedir,
    get_install_file,
    get_install_map,
    get_metadata,
    MetadataBackend,
    )
from devportalbinary.testing import (
    BackendTests,
    MetadataFixture,
    )


class DummyBackend(MetadataBackend):
    """Dummy implementations of MetadataBackend's abstract methods."""

    def get_architecture(self, metadata):
        return None

    def get_build_depends(self, metadata):
        return 'build_depends', metadata

    def get_depends(self, metadata):
        return 'depends', metadata

    def get_description(self, metadata):
        return 'description', metadata

    def get_executable(self, package_name):
        return 'executable:' + package_name


class MetadataTests(BackendTests):

    BACKEND = DummyBackend

    def setUp(self):
        super(MetadataTests, self).setUp()
        # mock this for all tests to ensure we do not slow down because
        # of network access
        patcher = patch(
            'devportalbinary.metadata.get_latest_stable_ubuntu_distroseries')
        mock_get_latest_distroseries = patcher.start()
        mock_get_latest_distroseries.return_value = 'foo'
        self.addCleanup(patcher.stop)

    def test_metadata_file(self):
        self.assertEqual('devportal-metadata.json', MetadataBackend.METADATA_FILE)

    def test_get_metadata_field_present(self):
        # get_metadata returns the metadata value of the requested field.
        metadata = {
            'foo': self.getUniqueString(),
            'bar': self.getUniqueInteger(),
            }
        path = self.useFixture(MetadataFixture(metadata)).metadata_path
        foo = get_metadata('foo', path=path)
        self.assertEqual(metadata['foo'], foo)

    def test_get_metadata_default_file(self):
        # By default, get_metadata looks for the METADATA_FILE in the current
        # working directory.
        metadata = {
            'foo': self.getUniqueString(),
            'bar': self.getUniqueInteger(),
            }
        path = self.useFixture(MetadataFixture(metadata)).path
        self.addCleanup(os.chdir, os.getcwd())
        os.chdir(path)
        foo = get_metadata('foo')
        self.assertEqual(metadata['foo'], foo)

    def test_get_metadata_field_not_present_default_provided(self):
        # get_metadata returns the provided default value if the field is not
        # present in the metadata.
        metadata = {}
        path = self.useFixture(MetadataFixture(metadata)).metadata_path
        default = object()
        foo = get_metadata('foo', default, path=path)
        self.assertIs(default, foo)

    def test_get_metadata_field_not_present_no_default(self):
        # get_metadata raises an exception if the field isn't there and no
        # default was provided.
        metadata = {}
        field = self.getUniqueString()
        path = self.useFixture(MetadataFixture(metadata)).metadata_path
        e = self.assertRaises(KeyError, get_metadata, field, path=path)
        self.assertEqual(repr(field), str(e))

    def test_get_metadata_all_fields(self):
        # get_metadata returns the metadata value of the requested field.
        metadata = {
            'foo': self.getUniqueString(),
            'bar': self.getUniqueInteger(),
            }
        path = self.useFixture(MetadataFixture(metadata)).metadata_path
        found_metadata = get_metadata(path=path)
        self.assertEqual(metadata, found_metadata)

    def test_dump_json(self):
        # dump_json loads metadata, passes it to get_info and then dumps
        # whatever that returns.  This means that get_info(metadata) can be a
        # relatively pure function, obsessed only with figuring out the right
        # packaging information.
        metadata = {'foo': 'bar'}
        path = self.useFixture(MetadataFixture(metadata)).path
        backend = MetadataBackend(path)
        # get_info takes metadata and returns a dict mapping InfoElements to
        # values.  We're using PackageName here arbitrarily.
        backend.get_info = lambda metadata: {PackageName: metadata}
        output_buffer = StringIO()
        backend.dump_json(output_buffer)
        # The resulting JSON maps the names of the InfoElements to values.
        self.assertEqual(
            {PackageName.name: metadata},
            json.loads(output_buffer.getvalue()))

    def test_get_extra_files_install_file(self):
        # ExtraFiles includes an install file generated by get_install_file.
        package_name = self.getUniqueString()
        metadata = {MetadataBackend.PACKAGE_NAME: package_name}
        backend = self.make_backend()
        backend.get_executable = lambda x: x
        extra_files = backend.get_extra_files(metadata, package_name)
        install_file = extra_files['debian/install']
        self.assertEqual(
            get_install_file(package_name, backend.path, True),
            install_file)

    def test_extra_files_install_file_with_icons(self):
        # ExtraFiles includes an install file generated by get_install_file.
        package_name = self.getUniqueString()
        metadata = self.make_metadata()
        backend = self.make_backend()
        metadata[backend.ICONS] = {
            '48x48': 'foo/bar.png',
            '128x128': 'baz/qux.png',
            }
        backend.get_executable = lambda x: x
        extra_files = backend.get_extra_files(metadata, package_name)
        install_file = extra_files['debian/install']
        self.assertEqual(
            get_install_file(
                package_name, backend.path, True, icons={
                    '48x48': 'debian/icons/48x48/%s.png' % (package_name,),
                    '128x128': 'debian/icons/128x128/%s.png' % (package_name,),
                    }),
            install_file)

    def test_pick_closest_icon_resolution_for_size_mixed(self):
        backend = self.make_backend()
        # multiple mixed resolutions
        icons = {'128x128': 'baz/qux.png',
                 '32x32': 'baz/foo.png',
                 '64x64': 'baz/foobar.png',
                 }
        self.assertEqual(
            backend._pick_closest_icon_resolution_for_size(icons, "48x48"),
            "64x64")

    def test_pick_closest_icon_resoluton_for_size_only_smaller_sizes(self):
        backend = self.make_backend()
        # only smaller resolutions
        icons = {'32x32': 'baz/foo.png',
                 '16x16': 'baz/foo.png',
                 }
        self.assertEqual(
            backend._pick_closest_icon_resolution_for_size(icons, "48x48"),
            "32x32")
        

    @patch('devportalbinary.metadata.convert_icon')
    def test_ensure_required_icon_size(self, mock_convert_icon):
        """Test _ensure_required_icon_size adds the required icon size
           to the metadata.
        """
        metadata = self.make_metadata()
        backend = self.make_backend()
        metadata[backend.ICONS] = {
            '128x128': 'baz/qux.png',
            '32x32': 'baz/foo.png',
            '64x64': 'baz/foobar.png',
            }
        backend._ensure_required_icon_size(
            metadata, backend.REQUIRED_ICON_SIZE)
        self.assertIn(backend.REQUIRED_ICON_SIZE, metadata[backend.ICONS])
        mock_convert_icon.assert_called_with('baz/foobar.png', '48x48')

    def test_extra_files_desktop_file(self):
        # ExtraFiles includes a desktop file, named after the package, that is
        # generated using get_desktop_file on the backend.
        package_name = self.getUniqueString()
        tagline = self.getUniqueString()
        categories = self.getUniqueString()
        metadata = self.make_metadata(
            package_name=package_name,
            tagline=tagline,
            categories=categories,
            )
        backend = self.make_backend()
        backend.get_executable = lambda x: 'executable:' + x
        expected_desktop_file = get_desktop_file(
            package_name, backend.get_application_name(metadata),
            backend.get_executable(package_name),
            tagline=tagline, categories=categories,
            working_directory=get_install_basedir(package_name),
            ).get_contents()
        extra_files = backend.get_extra_files(metadata, package_name)
        desktop = extra_files['debian/%s.desktop' % (package_name,)]
        self.assertEqual(expected_desktop_file, desktop)

    def test_desktop_file_icons(self):
        # If there are icons in the metadata then the desktop file specifies
        # the name of the icon, which we have hard-coded to be the package
        # name.
        metadata = self.make_metadata(icons={'48x48': 'foo/bar.png'})
        backend = self.make_backend()
        package_name = backend.get_package_name(metadata)
        backend.get_executable = lambda x: 'executable:' + x
        expected_desktop_file = get_desktop_file(
            package_name,
            backend.get_application_name(metadata),
            backend.get_executable(package_name),
            icon=package_name,
            tagline=metadata[MetadataBackend.TAGLINE],
            working_directory=get_install_basedir(package_name),
            ).get_contents()
        extra_files = backend.get_extra_files(metadata, package_name)
        desktop = extra_files['debian/%s.desktop' % (package_name,)]
        self.assertEqual(expected_desktop_file, desktop)

    def test_get_info_with_architecture(self):
        # get_info consults various methods on the backend class and uses
        # those to figure out the info to return.
        class Backend(DummyBackend):
            def get_architecture(self, metadata):
                return 'architecture'

        package_name = self.getUniqueString('package-name')
        metadata = self.make_metadata(package_name=package_name)
        backend = Backend(self.useFixture(TempdirFixture()).path)
        info = backend.get_info(metadata)
        self.assertEqual(
            {Architecture: 'architecture',
             BuildDepends: ('build_depends', metadata),
             Depends: ('depends', metadata),
             Description: ('description', metadata),
             Distribution: 'foo',
             ExtraFiles: backend.get_extra_files(metadata, package_name),
             PackageName: package_name,
             License: "unknown",
            }, info)

    def test_get_info_without_architecture(self):
        # get_info consults various methods on the backend class and uses
        # those to figure out the info to return.  If get_architecture returns
        # None, then it is excluded from the info.
        package_name = self.getUniqueString('package-name')
        metadata = self.make_metadata(package_name=package_name)
        backend = DummyBackend(self.useFixture(TempdirFixture()).path)
        info = backend.get_info(metadata)
        self.assertEqual(
            {BuildDepends: ('build_depends', metadata),
             Depends: ('depends', metadata),
             Description: ('description', metadata),
             Distribution: 'foo',
             ExtraFiles: backend.get_extra_files(metadata, package_name),
             PackageName: package_name,
             License: "unknown",
            }, info)

    def test_maintainer(self):
        metadata = self.make_metadata()
        maintainer = 'Dude <dude@example.com>'
        metadata[MetadataBackend.MAINTAINER] = maintainer
        backend = self.make_backend()
        self.assertEqual(maintainer, backend.get_info(metadata)[Maintainer])

    def test_homepage(self):
        metadata = self.make_metadata()
        homepage = 'http://www.pkgme-rocks.com/'
        metadata[MetadataBackend.HOMEPAGE] = homepage
        backend = self.make_backend()
        self.assertEqual(homepage, backend.get_info(metadata)[Homepage])

    def test_version(self):
        metadata = self.make_metadata()
        metadata[MetadataBackend.SUGGESTED_VERSION] = '0.1'
        backend = self.make_backend()
        self.assertEqual('0.1', backend.get_version(metadata))

    def test_version_in_info(self):
        metadata = self.make_metadata()
        metadata[MetadataBackend.SUGGESTED_VERSION] = '0.1'
        backend = self.make_backend()
        self.assertEqual(
            backend.get_version(metadata),
            backend.get_info(metadata)[Version])

    def test_get_extra_files_from_paths_no_icons(self):
        metadata = self.make_metadata()
        backend = self.make_backend()
        package_name = backend.get_package_name(metadata)
        self.assertEqual(
            {},
            backend._get_extra_icon_files_from_paths(metadata, package_name))

    def test_get_extra_files_from_paths_icons(self):
        metadata = self.make_metadata()
        metadata[MetadataBackend.ICONS] = {
            '48x48': 'foo.png',
            '64x64': '/cat.svg',
            '92x92': '/icon',
            '128x128': '/bar/qux.png',
            }
        backend = self.make_backend()
        package_name = backend.get_package_name(metadata)
        foo = os.path.normpath(os.path.join(backend.path, 'foo.png'))
        self.assertEqual(
            {'debian/icons/48x48/%s.png' % (package_name,): foo,
             'debian/icons/64x64/%s.svg' % (package_name,): '/cat.svg',
             'debian/icons/92x92/%s' % (package_name,): '/icon',
             'debian/icons/128x128/%s.png' % (package_name,): '/bar/qux.png',
             },
            backend._get_extra_icon_files_from_paths(metadata, package_name))

    def test_get_extra_files_from_paths_in_info_if_icons(self):
        metadata = self.make_metadata()
        metadata[MetadataBackend.ICONS] = {
            '48x48': '/foo/bar.png',
            '128x128': '/baz/qux.png',
            }
        backend = self.make_backend()
        self.assertEqual(
            backend.get_extra_files_from_paths(metadata),
            backend.get_info(metadata)[ExtraFilesFromPaths])

    def test_get_extra_files_from_paths_lintian_override(self):
        backend = self.make_backend()
        metadata = self.make_metadata()
        package_name = backend.get_package_name(metadata)
        self.assertIn(
            'debian/%s.lintian-overrides' % package_name,
            backend.get_extra_files(metadata, package_name))

    def test_license_field_not_in_mapping(self):
        metadata = self.make_metadata()
        license = 'not-standard-license-that-is-not-mapped'
        metadata[MetadataBackend.LICENSE] = license
        backend = self.make_backend()
        self.assertEqual(license, backend.get_info(metadata)[License])

    def test_license_field_mapping(self):
        metadata = self.make_metadata()
        license = 'Apache License'
        metadata[MetadataBackend.LICENSE] = license
        backend = self.make_backend()
        self.assertEqual('Apache-2.0', backend.get_info(metadata)[License])

    def test_distribution(self):
        metadata = self.make_metadata()
        backend = self.make_backend()
        self.assertEqual('foo', backend.get_info(metadata)[Distribution])


class DesktopFileTests(TestCase):

    def test_makes_desktop_file_with_given_values(self):
        package_name = self.getUniqueString()
        executable = self.getUniqueString()
        app_name = self.getUniqueString()
        tagline = self.getUniqueString()
        categories = ['cat1', 'cat2']
        icon = self.getUniqueString()
        working_directory = self.getUniqueString()
        desktop_file = get_desktop_file(
            package_name, app_name, executable, tagline=tagline,
            categories=categories, icon=icon,
            working_directory=working_directory)
        self.assertThat(
            {'Name': app_name, 'Comment': tagline, 'Categories': 'cat1;cat2;',
             'Exec': executable, 'Icon': icon, 'Path': working_directory},
            AreDesktopValuesFor(desktop_file))


class InstallFileTests(TestCase):

    def test_format_install_map(self):
        # format_install_map takes a dict and returns the contents o a
        # correctly formatted install file.
        install = format_install_map({'foo': 'bar', 'baz': 'qux'})
        self.assertEqual('baz qux\nfoo bar\n', install)

    def test_install_map(self):
        # The install file instructs debhelper to copy everything in the
        # top-level to /opt/<package-name>.
        tempdir = self.useFixture(TempdirFixture())
        tempdir.touch('some-file')
        install_map = get_install_map('package-name', tempdir.path)
        self.assertEqual({"some-file": "opt/package-name"}, install_map)

    def test_get_install_file_returns_formatted_map(self):
        tempdir = self.useFixture(TempdirFixture())
        tempdir.touch('some-file')
        install_map = get_install_map('package-name', tempdir.path)
        install_file = get_install_file('package-name', tempdir.path)
        self.assertEqual(format_install_map(install_map), install_file)

    def test_install_map_many_files_and_directories(self):
        # The install file instructs debhelper to copy everything in the
        # top-level to /opt/<package-name>.
        tempdir = self.useFixture(TempdirFixture())
        tempdir.touch('some-file')
        tempdir.mkdir('directory')
        install_map = get_install_map('package-name', tempdir.path)
        self.assertEqual(
            {"directory": "opt/package-name",
             "some-file": "opt/package-name"}, install_map)

    def test_skip_debian(self):
        # The install file instructs debhelper to copy everything in the
        # top-level to /opt/<package-name>, except for the 'debian' directory.
        tempdir = self.useFixture(TempdirFixture())
        tempdir.touch('some-file')
        tempdir.mkdir('directory')
        tempdir.mkdir(DEBIAN_DIR)
        install_map = get_install_map('package-name', tempdir.path)
        self.assertEqual(
            {"directory": "opt/package-name",
             "some-file": "opt/package-name"}, install_map)

    def test_skip_metadata(self):
        # The install file instructs debhelper to copy everything in the
        # top-level to /opt/<package-name>, except for the 'debian' directory
        # and the metadata file.
        tempdir = self.useFixture(TempdirFixture())
        tempdir.touch('some-file')
        tempdir.mkdir('directory')
        tempdir.touch(MetadataBackend.METADATA_FILE)
        install_map = get_install_map('package-name', tempdir.path)
        self.assertEqual(
            {"directory": "opt/package-name",
             "some-file": "opt/package-name"}, install_map)

    def test_include_desktop_file(self):
        tempdir = self.useFixture(TempdirFixture())
        tempdir.touch('some-file')
        install_map = get_install_map(
            'package-name', tempdir.path, include_desktop=True)
        self.assertEqual(
            {"debian/package-name.desktop": "usr/share/applications",
             "some-file": "opt/package-name"},
            install_map)

    def test_icons(self):
        tempdir = self.useFixture(TempdirFixture())
        tempdir.touch('some-file')
        install_map = get_install_map(
            'package-name', tempdir.path,
            icons={
                '48x48': 'foo/bar.png',
                '128x128': 'baz/qux.png',
                })
        self.assertEqual(
            {'some-file': 'opt/package-name',
             'foo/bar.png': 'usr/share/icons/hicolor/48x48/apps',
             'baz/qux.png': 'usr/share/icons/hicolor/128x128/apps',
             }, install_map)

    # XXX: Maybe want to check that icons don't go into /opt.  Could also just
    # put the icons into debian/.


class PackageNameTests(TestCase):

    def test_package_name_provided(self):
        # If the package name is supplied in the metadata, then that's what we
        # use.
        backend = MetadataBackend()
        package_name = self.getUniqueString()
        metadata = {MetadataBackend.PACKAGE_NAME: package_name}
        self.assertEqual(package_name, backend.get_package_name(metadata))

    def test_application_name_not_provided(self):
        # If the application name is not provided, use the capitalized package
        # name.
        backend = MetadataBackend()
        package_name = self.getUniqueString()
        metadata = {MetadataBackend.PACKAGE_NAME: package_name}
        self.assertEqual(
            package_name.capitalize(), backend.get_application_name(metadata))

    def test_application_name_provided(self):
        # If the application name is provided, then use that.
        backend = MetadataBackend()
        app_name = self.getUniqueString('app-name')
        metadata = {MetadataBackend.APPLICATION_NAME: app_name}
        self.assertEqual(app_name, backend.get_application_name(metadata))

    def test_package_name_empty(self):
        # If the package name is supplied in the metadata, but it's empty,
        # then we use the app name instead.
        backend = MetadataBackend()
        app_name = self.getUniqueString('app-name')
        metadata = {
            MetadataBackend.APPLICATION_NAME: app_name,
            MetadataBackend.PACKAGE_NAME: ''}
        self.assertEqual(app_name, backend.get_package_name(metadata))

    def test_package_name_not_provided(self):
        backend = MetadataBackend()
        app_name = self.getUniqueString('app-name')
        metadata = {MetadataBackend.APPLICATION_NAME: app_name}
        self.assertEqual(app_name, backend.get_package_name(metadata))

    def test_package_name_both_not_provided(self):
        backend = MetadataBackend()
        metadata = {}
        e = self.assertRaises(
            AssertionError, backend.get_package_name, metadata)
        self.assertEqual("Could not determine package name", str(e))

    def test_package_name_empty_app_name_not_provided(self):
        backend = MetadataBackend()
        metadata = {MetadataBackend.PACKAGE_NAME: ''}
        e = self.assertRaises(
            AssertionError, backend.get_package_name, metadata)
        self.assertEqual("Could not determine package name", str(e))

    def test_app_name_both_not_provided(self):
        backend = MetadataBackend()
        metadata = {}
        e = self.assertRaises(
            AssertionError, backend.get_application_name, metadata)
        self.assertEqual("Could not determine application name", str(e))

    def test_unclean_app_name(self):
        # It's OK if we get an invalid package name from the backend, because
        # pkgme will clean it first.
        backend = MetadataBackend()
        metadata = {MetadataBackend.APPLICATION_NAME: 'Foo'}
        package_name = backend.get_package_name(metadata)
        self.assertEqual('Foo', package_name)

    def test_suggested_package_name(self):
        # If suggested_package_name is provided and package_name is not, then
        # we'll use the (cleaned) suggested package name as the package name.
        backend = MetadataBackend()
        metadata = {MetadataBackend.SUGGESTED_PACKAGE_NAME: 'foo'}
        package_name = backend.get_package_name(metadata)
        self.assertEqual('foo', package_name)

    def test_suggested_package_name_trumps_app_name(self):
        # If suggested_package_name is provided as well as an
        # application_name, we get the package name from the explicit
        # suggestion rather than inferring from the application name.
        backend = MetadataBackend()
        metadata = {MetadataBackend.SUGGESTED_PACKAGE_NAME: 'foo',
                    MetadataBackend.APPLICATION_NAME: 'bar'}
        package_name = backend.get_package_name(metadata)
        self.assertEqual('foo', package_name)

    def test_package_name_trumps_suggestion(self):
        # If both package_name and suggested_package_name are provided, we use
        # package_name.
        backend = MetadataBackend()
        metadata = {MetadataBackend.SUGGESTED_PACKAGE_NAME: 'foo',
                    MetadataBackend.PACKAGE_NAME: 'bar'}
        package_name = backend.get_package_name(metadata)
        self.assertEqual('bar', package_name)


class GetInstallBasedirTests(TestCase):

    def test_path(self):
        package_name = self.getUniqueString()
        self.assertEqual('/opt/%s' % package_name,
                get_install_basedir(package_name))


# XXX: Assuming icon name in desktop == package name
