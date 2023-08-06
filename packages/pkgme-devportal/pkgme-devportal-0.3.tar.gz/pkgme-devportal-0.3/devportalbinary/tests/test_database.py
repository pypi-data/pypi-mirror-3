from collections import namedtuple
import gzip
import os

from fixtures import (
    TempDir,
    )
from storm.databases.postgres import psycopg2
from storm.exceptions import ClosedError
from testresources import ResourcedTestCase
from testtools import TestCase
from testtools.matchers import (
    Equals,
    Matcher,
    )
from mock import patch

from devportalbinary.database import (
    AptFilePackageDatabase,
    BinaryPackage,
    build_symbol_list,
    load_configuration,
    PackageDatabase,
    )
from devportalbinary.testing import (
    ConfigFileFixture,
    ConfigSettings,
    postgres_db_resource,
    )


class ResultsIn(Matcher):

    def __init__(self, db, rows):
        self._db = db
        self._rows = rows

    def match(self, query):
        # XXX: Abstraction violation
        results = self._db._store.execute(query)
        return Equals(self._rows).match(list(results))


class TestDatabase(TestCase, ResourcedTestCase):

    resources = [
            ('db_fixture', postgres_db_resource),
            ]

    def get_package_db(self):
        db = PackageDatabase(self.db_fixture.conn)
        self.addCleanup(db.close)
        return db

    def test_insert_new_library(self):
        db = self.get_package_db()
        db.insert_new_library('foo-src', 'libfoo.so.0', 'foo', 'i386')
        self.assertThat(
            "SELECT source_package_name, library, dependency, architecture FROM libdep",
            ResultsIn(db, [('foo-src', 'libfoo.so.0', 'foo', 'i386')]))

    def test_double_insert(self):
        db = self.get_package_db()
        db.insert_new_library('foo-src', 'libfoo.so.0', 'foo', 'i386')
        self.assertRaises(
            psycopg2.IntegrityError,
            db.insert_new_library, 'foo-src', 'libfoo.so.0', 'foo', 'i386')

    def test_differing_dependencies(self):
        db = self.get_package_db()
        db.insert_new_library('foo-src', 'libfoo.so.0', 'foo', 'i386')
        db.insert_new_library('foo-src', 'libfoo.so.0', 'bar', 'i386')
        deps = db.get_dependencies('libfoo.so.0')
        self.assertEqual(deps, set(['foo', 'bar']))

    def test_get_dependencies(self):
        db = self.get_package_db()
        db.insert_new_library('foo-src', 'libfoo.so.0', 'foo', 'i386')
        deps = db.get_dependencies('libfoo.so.0')
        self.assertEqual(deps, set(['foo']))

    def test_respects_architecture(self):
        db = self.get_package_db()
        db.insert_new_library('foo-src', 'libfoo.so.0', 'foo', 'i386')
        db.insert_new_library('foo-src', 'libfoo.so.0', 'foo-amd64', 'amd64')
        deps = db.get_dependencies('libfoo.so.0', arch='amd64')
        self.assertEqual(deps, set(['foo-amd64']))

    def test_unknown_library(self):
        db = self.get_package_db()
        deps = db.get_dependencies('libfoo.so.0')
        self.assertEqual(deps, set())

    def test_update_source_package(self):
        db = self.get_package_db()
        db.update_source_package(
            'foo', [([('libfoo.so.1', 'foo-bin')], 'i386')])
        deps = db.get_dependencies('libfoo.so.1')
        self.assertEqual(deps, set(['foo-bin']))

    def test_update_existing_source_package_no_libraries(self):
        db = self.get_package_db()
        db.update_source_package('foo', [([('libfoo.so.1', 'foo-bin')], 'i386')])
        # Run again, this time with no symbols, representing that a newer
        # version of the package no longer exports any libraries.
        db.update_source_package('foo', [([], 'i386')])
        deps = db.get_dependencies('libfoo.so.1')
        self.assertEqual(deps, set())

    def test_update_source_package_two_architectures(self):
        # If two architectures are updated separately then they
        # shouldn't interfere
        db = self.get_package_db()
        db.update_source_package(
            'foo', [([('libfoo.so.1', 'foo-bin')], 'i386')])
        db.update_source_package(
            'foo', [([('libfoo.so.1', 'foo-bin-amd64')], 'amd64')])
        deps = db.get_dependencies('libfoo.so.1', arch='i386')
        self.assertEqual(deps, set(['foo-bin']))

    def test_fetch_symbol_files(self):
        # It's hard to test the function because it uses launchpadlib,
        # so we'll test the main point, taking the output of
        # package.iter_symbols(), passing it through build_symbol_list(),
        # and then to # update_source_package() to ensure that the signatures
        # match
        symbol_list = build_symbol_list([('libfoo.so.1 foo-bin', 'i386')])
        db = self.get_package_db()
        db.update_source_package('foo', symbol_list)
        deps = db.get_dependencies('libfoo.so.1')
        self.assertEqual(set(['foo-bin']), deps)

    def test_close(self):
        # Test that we can close the package db.
        db = PackageDatabase(self.db_fixture.conn)
        db.close()
        self.assertRaises(ClosedError, db.insert_new_library, 'foo',
                'libfoo.so.1', 'foo-bin', 'i386')

    def test_close_twice(self):
        # Test that we can close the package db twice with no exception.
        db = PackageDatabase(self.db_fixture.conn)
        db.close()
        db.close()


class TestBuildSymbolList(TestCase):

    def test_no_symbols(self):
        self.assertEqual([], build_symbol_list([]))

    def test_some_symbols(self):
        symbol_list = build_symbol_list([('a b', 'i386')])
        self.assertEqual([([('a', 'b')], 'i386')], symbol_list)


class TestDatabaseConfiguration(TestCase):

    def use_database_config(self, **db_settings):
        return self.useFixture(ConfigSettings(('database', db_settings)))

    def test_get_db_info_from_config_sqlite(self):
        other_tempdir = self.useFixture(TempDir())
        expected_db_path = os.path.join(other_tempdir.path, 'db')
        self.use_database_config(db_type='sqlite', path=expected_db_path)
        options = load_configuration().options
        self.assertRaises(ValueError, PackageDatabase.get_db_info_from_config,
                options)

    def test_default_create_no_config(self):
        nonexistent = self.getUniqueString()
        self.useFixture(ConfigFileFixture(nonexistent))
        self.assertIsInstance(
            PackageDatabase.create(), AptFilePackageDatabase)

    def test_default_create_empty_config(self):
        self.useFixture(ConfigSettings())
        self.assertIsInstance(
            PackageDatabase.create(), AptFilePackageDatabase)

    def test_get_db_info_from_config_postgres(self):
        expected_username = self.getUniqueString()
        expected_password = self.getUniqueString()
        expected_host = self.getUniqueString()
        expected_port = self.getUniqueInteger()
        expected_db_name = self.getUniqueString()

        self.use_database_config(
            db_type='postgres',
            username=expected_username,
            password=expected_password,
            host=expected_host,
            port=expected_port,
            db_name=expected_db_name)
        options = load_configuration().options
        uri = PackageDatabase.get_db_info_from_config(options)
        self.assertEqual(expected_db_name, uri.database)
        self.assertEqual(expected_port, uri.port)
        self.assertEqual(expected_host, uri.host)
        self.assertEqual(expected_password, uri.password)
        self.assertEqual(expected_username, uri.username)


class AptFilePackageDatabaseTestCase(TestCase):

    # point to our local contents file version that is a tad smaller
    CONTENTS_CACHE = os.path.join(
        os.path.dirname(__file__), "data", "apt-file-backend")

    def setUp(self):
        super(AptFilePackageDatabaseTestCase, self).setUp()
        self.db = AptFilePackageDatabase(self.CONTENTS_CACHE)

    def test_read_fixture_contents_worked(self):
        """ test that our fixture Contents file works as expected """
        # our test DB has 4 entries in the default search path
        self.assertEqual(
            len(self.db._get_lib_to_pkgs_mapping("oneiric", "i386")), 4)

    def test_get_dependencies(self):
        """ Test that data from the fixture dependencies file works """
        self.assertEqual(
            self.db.get_dependencies("libz.so.1"), set(["zlib1g"]))

    @patch("urllib.urlretrieve")
    def test_lazy_downloading(self, mock_urlretrieve):
        """ test that lazy downloading works """
        def _put_fixture_contents_file_in_place(url, target):
            with gzip.open(target, "w") as f:
                f.write("""
Some header text that is ignored
FILE                 LOCATION
usr/lib/libfoo.so.2  pkgfoo,pkgbar
""")
        tempdir = self.useFixture(TempDir())
        db = AptFilePackageDatabase(tempdir.path)
        mock_urlretrieve.side_effect = _put_fixture_contents_file_in_place
        self.assertEqual(
            db.get_dependencies("libfoo.so.2", arch="i386"),
            set(["pkgfoo", "pkgbar"]))
        self.assertEqual(len(db._get_lib_to_pkgs_mapping("oneiric", "i386")), 1)

    def test_close(self):
        # Test that there is a close method we can call
        self.db.close()


class FakeBPPH(object):

    def __init__(self):
        self.archive = namedtuple(
                'Archive', 'web_link')('http://lp.net/archive')
        self.distro_arch_series = namedtuple(
                'DistroArchSeries', 'architecture_tag')('i386')
        self.binary_package_name = 'foo'
        self.binary_package_version = '1'


class TestBinaryPackage(TestCase):

    def test_get_url(self):
        bpph = FakeBPPH()
        expected_url = '%s/+files/%s_%s_%s.deb' % (
            bpph.archive.web_link,
            bpph.binary_package_name,
            bpph.binary_package_version,
            bpph.distro_arch_series.architecture_tag,
            )
        self.assertEqual(expected_url, BinaryPackage(bpph).get_url())

    def test_get_url_with_epoch(self):
        # epochs are stripped from the version number
        bpph = FakeBPPH()
        bpph.binary_package_version = '1:1'
        expected_url = '%s/+files/%s_%s_%s.deb' % (
            bpph.archive.web_link,
            bpph.binary_package_name,
            '1',
            bpph.distro_arch_series.architecture_tag,
            )
        self.assertEqual(expected_url, BinaryPackage(bpph).get_url())
