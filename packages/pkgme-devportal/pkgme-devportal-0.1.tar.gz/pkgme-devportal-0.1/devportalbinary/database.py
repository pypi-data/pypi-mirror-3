# Copyright 2011 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

import errno
from itertools import chain
import os
import shutil
import tempfile

from bzrlib import urlutils
from fixtures import (
    Fixture,
    TempDir,
    )

from launchpadlib import (
    uris,
    )
from launchpadlib.launchpad import Launchpad
from pkgme.run_script import run_subprocess
from storm.locals import create_database, Store

from .configuration import (
    CONF_FILE_ENV_VAR,
    get_config_file_path,
    load_configuration,
    )
from .utils import download_file


# XXX: Historic name of this package.  Update to 'pkgme-devportal' and
# re-authorize.
APPLICATION_NAME = 'pkgme-binary'
SERVICE_ROOT = uris.LPNET_SERVICE_ROOT


# A list of package names that don't match lib*, but which we want
# to scan anyway.
PACKAGE_NAME_WHITELIST = [
    "e2fslibs",
    "odbcinst1debian2",
    "python2.7-dbg",
    "uno-libs3",
    "zlib1g",
    ]


def is_library_package(deb_filename):
    """Is ``deb_filename`` likely to contain libraries?"""
    if deb_filename.startswith('lib'):
        return True
    for prefix in PACKAGE_NAME_WHITELIST:
        if deb_filename.startswith(prefix):
            return True
    return False


class LaunchpadFixture(Fixture):

    def __init__(self, application_name, service_root):
        super(LaunchpadFixture, self).__init__()
        self._app_name = application_name
        self._service_root = service_root

    def setUp(self):
        super(LaunchpadFixture, self).setUp()
        tempdir = self.useFixture(TempDir())
        self.anonymous = Launchpad.login_anonymously(
            self._app_name, self._service_root, tempdir.path)


def iter_published_sources(lp, since=None, name=None, exact_match=False):
    ubuntu = lp.distributions['ubuntu']
    archive = ubuntu.main_archive
    # XXX: oneiric is a puppy that is just for christmas. Specifically, it's a
    # bug that this is looking in oneiric, should instead be looking in
    # ... well, we don't know.
    oneiric = ubuntu.getSeries(name_or_version='oneiric')
    filters = dict(distro_series=oneiric)
    if since:
        filters['created_since_date'] = since
    if name:
        filters['source_name'] = name
    filters['exact_match'] = exact_match
    sources = chain(
        archive.getPublishedSources(status='Published', **filters),
        archive.getPublishedSources(status='Pending', **filters))
    return sources


def iter_published_binaries(lp, since=None, name=None, exact_match=False):
    architectures = load_configuration().options.architectures_supported
    ubuntu = lp.distributions['ubuntu']
    archive = ubuntu.main_archive
    # XXX: oneiric is a puppy that is just for christmas. Specifically, it's a
    # bug that this is looking in oneiric, should instead be looking in
    # ... well, we don't know.
    oneiric = ubuntu.getSeries(name_or_version='oneiric')
    our_series = (
        oneiric.getDistroArchSeries(archtag=tag) for tag in architectures)
    filters = dict(status='Published')
    if since:
        filters['created_since_date'] = since
    if name:
        filters['binary_name'] = name
    filters['exact_match'] = exact_match
    return chain(
        *[archive.getPublishedBinaries(distro_arch_series=series, **filters)
          for series in our_series])


class BinaryPackage(object):

    def __init__(self, bpph):
        self.bpph = bpph

    @classmethod
    def find(cls, lp, name):
        # XXX: Not sure the first one will be the one we want. Probably want
        # to sort based on date_published.
        try:
            return cls(iter_published_binaries(lp, name=name, exact_match=False).next())
        except StopIteration:
            return None

    def get_url(self):
        """Get the download URL for this binary package."""
        return '%s/+files/%s_%s_%s.deb' % (
            self.bpph.archive.web_link,
            self.bpph.binary_package_name,
            self.bpph.binary_package_version,
            self.bpph.distro_arch_series.architecture_tag,
            )

    def get_symbol_contents(self):
        directory = tempfile.mkdtemp()
        try:
            url = self.get_url()
            filename = os.path.splitext(urlutils.basename(url))[0]
            if not is_library_package(filename):
                return
            path = download_file(url, directory)
            symbols_contents = extract_symbols_file(path)
            return symbols_contents
        finally:
            shutil.rmtree(directory)

    def iter_symbols(self):
        contents = self.get_symbol_contents()
        if contents:
            yield contents


class SourcePackage(object):

    def __init__(self, spph):
        self.spph = spph

    @classmethod
    def find(cls, lp, name):
        """Get a ``SourcePackage`` object for the source package ``name``."""
        try:
            return cls(iter_published_sources(lp, name=name, exact_match=True).next())
        except StopIteration:
            # We've been asked to get a SourcePackagePublishingHistory for a
            # package that's not in the series we're focusing on. Just return
            # None for now.
            return None

    def iter_symbols(self):
        """Iterate over the symbols files provided by 'spph'.

        Yields the contents of the symbol files found in the binary packages built
        from the source package in spph.

        Any binary packages that do not start with 'lib' are ignored. All
        architectures other than those in ``ARCHITECTURES`` are ignored.

        :param spph: A SourcePackagePublishingHistory object from Launchpad.
        """
        directory = tempfile.mkdtemp()
        binary_file_urls = self.spph.binaryFileUrls()
        architectures = load_configuration().options.architectures_supported
        for url in binary_file_urls:
            filename = os.path.splitext(urlutils.basename(url))[0]
            if not is_library_package(filename):
                continue
            # XXX: This is a bit of a hack to work around the fact that
            # Launchpad has no way of filtering binary packages for a source
            # package by architecture. See bug 881509.
            architecture = filename.split('_')[-1]
            if architecture not in architectures:
                continue
            path = download_file(url, directory)
            symbols_contents = extract_symbols_file(path)
            if symbols_contents:
                yield symbols_contents
        shutil.rmtree(directory)


def extract_symbols_file(binary_package_path):
    """Return the contents of the symbols file for a binary package.

    :param binary_package_path: The path to a binary package.
    """
    temp_dir = tempfile.mkdtemp()
    try:
        run_subprocess(['dpkg-deb', '-e', binary_package_path, temp_dir])
        symbol_path = os.path.join(temp_dir, 'symbols')
        try:
            return open(symbol_path).read()
        except (OSError, IOError), e:
            if e.errno == errno.ENOENT:
                return
            raise
    finally:
        shutil.rmtree(temp_dir)


def iter_so_names(symbol_contents):
    """Yield (library, dependency) from a symbols file.

    Ignores versions and a whole bunch of other stuff and is probably the
    wrong API even.
    """

    # XXX: This is going to yield sonames and package names for now. Really,
    # there should be something parsing the symbols file and another thing to
    # somehow turn those into dependencies with versions.

    # Doesn't know how to handle lines like this:
    #
    # libformw.so.5 #PACKAGE#.
    #
    # This is OK, as we're only processing symbols files from binary packages
    # rather than source packages.

    for line in symbol_contents.splitlines():
        if not line:
            # Blank lines are skipped
            continue
        if line.startswith('|'):
            # Alternative dependency template
            # e.g. | libgl1-mesa-glx #MINVER#
            continue
        if line.startswith('*'):
            # Meta-information
            # e.g. * Build-Depends-Package: libgl1-mesa-dev
            continue
        if line.startswith(' '):
            # Symbol
            # e.g.  gdk_add_client_message_filter@Base 2.8.0
            continue
        if line.startswith('#'):
            # Lines starting with '#' are comments.  There are also DEPRECATED
            # and MISSING, and jml doesn't really know what they mean
            continue
        library, dependency = tuple(line.split()[:2])
        if '#include' in library:
            # To skip lines that are includes.  XXX: Properly ought to process
            # the tags that might appear before the include
            # line.
            #
            # e.g. (arch=!armel)#include "libdiagnostics0.symbols.backtrace"
            continue
        yield library, dependency


class PackageDatabase(object):

    SQLITE = 'sqlite'
    POSTGRES = 'postgres'

    def __init__(self, store):
        self._store = store

    @classmethod
    def _get_storm_sqlite_connection_string(cls, opts):
        if not opts.database_path:
            raise ValueError(
                "Cannot create database, no connection info available. "
                "Looked in %s. Perhaps %s is set incorrectly?" % (
                    get_config_file_path(),
                    CONF_FILE_ENV_VAR))
        return '%s:%s' % (opts.database_db_type, opts.database_path)

    @classmethod
    def _get_storm_postgres_connection_string(cls, opts):
        for attr in ('database_host', 'database_port',
                'database_username', 'database_password', 'database_db_name'):
            if not getattr(opts, attr, None):
                raise AssertionError(
                    "You must specify %s for %s" % (
                        attr, opts.database_db_type))
        return '%s://%s:%s@%s:%s/%s' % (
                    opts.database_db_type, opts.database_username,
                    opts.database_password, opts.database_host,
                    opts.database_port, opts.database_db_name)

    @classmethod
    def _get_storm_connection_string(cls, opts):
        if opts.database_db_type == cls.SQLITE:
            return cls._get_storm_sqlite_connection_string(opts)
        elif opts.database_db_type == cls.POSTGRES:
            return cls._get_storm_postgres_connection_string(opts)
        else:
            raise AssertionError(
                "Unsupported database: %s" % opts.database_db_type)

    @classmethod
    def get_db_info_from_config(cls, opts):
        connection_string = cls._get_storm_connection_string(opts)
        return connection_string, opts.database_db_type

    @classmethod
    def get_store_from_config(cls, opts):
        """Create a storm store based on a config file.

        This method will create a storm store based
        on the information in ``~/.config/pkgme-binary/conf``

        :return: a tuple of (store, store_type), where store_type
            is one of cls.SQLITE or cls.POSTGRES, indicating what
            is at the other end of the store.
        """
        connection_string, store_type = cls.get_db_info_from_config(opts)
        database = create_database(connection_string)
        return Store(database), store_type

    @classmethod
    def create(cls, store=None, store_type='sqlite'):
        if store is None:
            options = load_configuration().options
            store, store_type = cls.get_store_from_config(options)
        if store_type == 'sqlite':
            store.execute(
                "CREATE TABLE IF NOT EXISTS libdep ("
                "source_package_name TEXT, "
                "library TEXT, "
                "dependency TEXT, "
                "CONSTRAINT libdep_uniq UNIQUE (source_package_name, "
                "library, dependency))")
        elif store_type == 'postgres':
            # Postgres only supports IF NOT EXISTS starting from 9.1
            exists = store.execute(
                "SELECT COUNT(relname) FROM pg_class WHERE "
                "relname = 'libdep'").get_one()[0]
            if not exists:
                store.execute(
                    "CREATE TABLE libdep ("
                    "source_package_name TEXT, "
                    "library TEXT, "
                    "dependency TEXT, "
                    "CONSTRAINT libdep_uniq UNIQUE (source_package_name, "
                    "library, dependency))")
        else:
            raise AssertionError("Unsupported database type: %s" % store_type)
        store.commit()
        return cls(store)

    def get_dependencies(self, library_name):
        """Get the binary packagaes that provide 'library_name'."""
        result = self._store.execute("SELECT dependency FROM libdep WHERE library = ?",
                  (unicode(library_name),))
        return set([dependency for [dependency] in result])

    def insert_new_library(self, source_package_name, library_name, dependency):
        """Insert a library and its needed dependency into the database.

        :param library_name: A full soname, e.g. libfoo.so.1.
        :param dependency: A binary package dependency, possibly including
            version.
        """
        self._store.execute("INSERT INTO libdep VALUES (?, ?, ?)",
                  (unicode(source_package_name), unicode(library_name), unicode(dependency)))

    def update_source_package(self, source_package_name, symbols):
        """Update the database with the symbols from 'source_package_name'.

        :param source_package_name: The name of the source package where the
            symbols came from.
        :param symbols: A list of representations of symbols files, where each
            representation is a list of tuples of library and
            dependency. e.g. [[(libfoo, foo), ...], ...].
        """
        self._store.execute("DELETE FROM libdep WHERE source_package_name = ?",
                  (unicode(source_package_name),))
        for symbols in symbols:
            for library, dependency in symbols:
                self.insert_new_library(
                    source_package_name, library, dependency)
        self._store.commit()


def fetch_symbol_files(scan_mode, package_name, db):
    """Fetch the symbol files for ``source_package_name`` into ``directory``."""
    if scan_mode == 'binary':
        finder = BinaryPackage.find
    else:
        finder = SourcePackage.find
    with LaunchpadFixture(APPLICATION_NAME, SERVICE_ROOT) as lp:
        package = finder(lp.anonymous, package_name)
        if not package:
            return
        symbols = [
            list(iter_so_names(symbols))
            for symbols in package.iter_symbols()]
    db.update_source_package(package_name, symbols)


def main():
    """Import the symbol files for 'package_name'."""
    glue = load_configuration()
    store, db_type = PackageDatabase.get_store_from_config(glue.options)
    package_name = glue.args[0]
    db = PackageDatabase.create(store, db_type)
    fetch_symbol_files(glue.options.scan_mode, package_name, db)
