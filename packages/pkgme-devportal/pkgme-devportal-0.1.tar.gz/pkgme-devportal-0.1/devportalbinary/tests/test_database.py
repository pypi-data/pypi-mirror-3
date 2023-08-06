import os

from testtools import try_imports

IntegrityError = try_imports(
    ['pysqlite2.dbapi2.IntegrityError', 'sqlite3.IntegrityError'])

from fixtures import (
    EnvironmentVariableFixture,
    TempDir,
    )
from storm.locals import create_database, Store
from testtools import TestCase
from testtools.matchers import (
    Equals,
    Matcher,
    )

from devportalbinary.database import (
    load_configuration,
    PackageDatabase,
    )
from devportalbinary.testing import (
    ConfigFileFixture,
    ConfigSettings,
    )


class ResultsIn(Matcher):

    def __init__(self, db, rows):
        self._db = db
        self._rows = rows

    def match(self, query):
        # XXX: Abstraction violation
        results = self._db._store.execute(query)
        return Equals(self._rows).match(list(results))


class TestDatabase(TestCase):

    def get_package_db(self):
        database = create_database('sqlite:')
        store = Store(database)
        return PackageDatabase.create(store, store_type=PackageDatabase.SQLITE)

    def test_insert_new_library(self):
        db = self.get_package_db()
        db.insert_new_library('foo-src', 'libfoo.so.0', 'foo')
        self.assertThat(
            "SELECT source_package_name, library, dependency FROM libdep",
            ResultsIn(db, [('foo-src', 'libfoo.so.0', 'foo')]))

    def test_double_insert(self):
        db = self.get_package_db()
        db.insert_new_library('foo-src', 'libfoo.so.0', 'foo')
        self.assertRaises(
            IntegrityError,
            db.insert_new_library, 'foo-src', 'libfoo.so.0', 'foo')

    def test_differing_dependencies(self):
        db = self.get_package_db()
        db.insert_new_library('foo-src', 'libfoo.so.0', 'foo')
        db.insert_new_library('foo-src', 'libfoo.so.0', 'bar')
        deps = db.get_dependencies('libfoo.so.0')
        self.assertEqual(deps, set(['foo', 'bar']))

    def test_get_dependencies(self):
        db = self.get_package_db()
        db.insert_new_library('foo-src', 'libfoo.so.0', 'foo')
        deps = db.get_dependencies('libfoo.so.0')
        self.assertEqual(deps, set(['foo']))

    def test_unknown_library(self):
        db = self.get_package_db()
        deps = db.get_dependencies('libfoo.so.0')
        self.assertEqual(deps, set())

    def test_update_source_package(self):
        db = self.get_package_db()
        db.update_source_package(
            'foo', [[('libfoo.so.1', 'foo-bin')]])
        deps = db.get_dependencies('libfoo.so.1')
        self.assertEqual(deps, set(['foo-bin']))

    def test_update_existing_source_package_no_libraries(self):
        db = self.get_package_db()
        db.update_source_package('foo', [[('libfoo.so.1', 'foo-bin')]])
        # Run again, this time with no symbols, representing that a newer
        # version of the package no longer exports any libraries.
        db.update_source_package('foo', [])
        deps = db.get_dependencies('libfoo.so.1')
        self.assertEqual(deps, set())


class TestDatabaseConfiguration(TestCase):

    def use_database_config(self, **db_settings):
        return self.useFixture(ConfigSettings(('database', db_settings)))

    def test_get_db_info_from_config_sqlite(self):
        other_tempdir = self.useFixture(TempDir())
        expected_db_path = os.path.join(other_tempdir.path, 'db')
        self.use_database_config(db_type='sqlite', path=expected_db_path)
        options = load_configuration().options
        connection_string, store_type = PackageDatabase.get_db_info_from_config(options)
        self.assertEqual('sqlite', store_type)
        self.assertEqual('sqlite:%s' % expected_db_path, connection_string)

    def test_default_create_no_config(self):
        nonexistent = self.getUniqueString()
        self.useFixture(ConfigFileFixture(nonexistent))
        self.assertRaises(ValueError, PackageDatabase.create)

    def test_default_create_empty_config(self):
        self.useFixture(ConfigSettings())
        self.assertRaises(ValueError, PackageDatabase.create)

    def test_get_db_info_from_config_postgres(self):
        expected_username = self.getUniqueString()
        expected_password = self.getUniqueString()
        expected_host = self.getUniqueString()
        expected_port = self.getUniqueString()
        expected_db_name = self.getUniqueString()

        self.use_database_config(
            db_type='postgres',
            username=expected_username,
            password=expected_password,
            host=expected_host,
            port=expected_port,
            db_name=expected_db_name)
        options = load_configuration().options
        connection_string, store_type = PackageDatabase.get_db_info_from_config(options)
        self.assertEqual('postgres', store_type)
        expected_connection_string = "postgres://%s:%s@%s:%s/%s" % (
                expected_username, expected_password, expected_host,
                expected_port, expected_db_name)
        self.assertEqual(expected_connection_string, connection_string)
