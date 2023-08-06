# Copyright 2011 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from contextlib import closing
import errno
import gzip
from itertools import chain
import os
import shutil
import tempfile
import urllib

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
from storm.uri import URI as StormURI

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
        version = self.bpph.binary_package_version
        if ':' in version:
            version = version[version.index(':')+1:]
        arch = self.bpph.distro_arch_series.architecture_tag
        if not self.bpph.architecture_specific:
            arch = 'all'
        return '%s/+files/%s_%s_%s.deb' % (
            self.bpph.archive.web_link,
            self.bpph.binary_package_name,
            version,
            arch,
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
            yield contents, self.bpph.distro_arch_series.architecture_tag


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
                yield symbols_contents, architecture
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


def iter_contents_file(contents):
    """ Yield (full-library-path, set-of-pkgnames) from a Contents file.

    It expects a line starting with "FILE" that tells it when the header ends
    and the actual content starts.
    """
    found_start_marker = False
    for line in contents:
        if not found_start_marker:
            if line.startswith("FILE"):
                found_start_marker = True
            continue
        (path, sep, pkgs) = [s.strip() for s in line.rpartition(" ")]
        # pkgs is formated a bit funny, e.g. universe/pkgname
        pkgs = set([os.path.basename(pkg) for pkg in pkgs.split(",")])
        yield (path, pkgs)


class URI(StormURI):
    """A stand-in for Storm's URI class.

    This class implements the same interface as `storm.uri.URI`, except
    that the constructor has a different signature. Storm's version takes
    a string and parses it, this version can be used when you already
    have a parsed version and just need to create the object.
    """

    def __init__(self, scheme=None, host=None, port=None, username=None,
                 password=None, database=None, options=None):
        self.scheme = scheme
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        self.options = options
        if self.options is None:
            self.options = dict()


class AptFilePackageDatabase(object):
    """ Really dumb database that just uses apt-file for local testing """

    # we could also read /etc/ld.so.conf.d/*.conf but this maybe different on
    # different distroseries especially if
    #    server-distroseries != target-distroseries
    #  (I wish there was ldconfig --print-search-dirs)
    LD_SEARCH_PATH = [
        # standards
        "lib",
        "usr/lib",
        "usr/local/lib",
        # old biarch
        "lib32",
        "usr/lib32",
        # new multiarch
        "lib/i686-linux-gnu",
        "lib/i386-linux-gnu",
        "lib/x86_64-linux-gnu",
        "usr/lib/i386-linux-gnu",
        "usr/lib/i686-linux-gnu",
        "usr/lib/x86_64-linux-gnu",
        # ?
        "usr/lib/x86_64-linux-gnu/fakechroot",
        "usr/lib/x86_64-linux-gnu/mesa",
        "usr/lib/x86_64-linux-gnu/mesa-egl",
        "usr/lib/i386-linux-gnu/mesa",
        ]

    DISTROSERIES = "oneiric"

    CONTENTS_FILE_URL_LOCATION = (
        "http://archive.ubuntu.com/ubuntu/dists/%(distroseries)s/"
        "Contents-%(arch)s.gz")

    CONTENTS_FILE = "Contents-%(distroseries)s-%(arch)s"

    def __init__(self, cachedir=None):
        self.cachedir = os.path.expanduser(cachedir)
        self._distroseries_arch_cache = {}

    def _get_lib_to_pkgs_mapping(self, distroseries, arch):
        """ Returns a dict of { library-name : set([pkg1,pkg2])

        This function will return a dict to lookup library-name to package
        dependencies for the given distroseries and architecture
        """
        if not (distroseries, arch) in self._distroseries_arch_cache:
            self._distroseries_arch_cache[(distroseries, arch)] = \
                      self._get_mapping_from_contents_file(distroseries, arch)
        return self._distroseries_arch_cache[(distroseries, arch)]

    def _get_contents_file_cache_path(self, distroseries, arch):
        """ Return the path in the cache for the given distroseries, arch """
        return os.path.join(
            self.cachedir, self.CONTENTS_FILE % {
                'distroseries' : distroseries, 'arch' : arch })

    def _get_contents_file_server_url(self, distroseries, arch):
        """ Return the remote server URL for the given distroseries, arch """
        return self.CONTENTS_FILE_URL_LOCATION % {
            'distroseries' : distroseries, 'arch' : arch }

    def _get_mapping_from_contents_file(self, distroseries, arch):
        """ Return lib,pkgs mapping from contents file for distroseries, arch

        This expects the contents file to be in the cachedir already.
        """
        lib_to_pkgs = {}
        path = self._get_contents_file_cache_path(distroseries, arch)
        with open(path) as f:
            for (path, pkgs) in filter(
                lambda (p, pkgs): os.path.dirname(p) in self.LD_SEARCH_PATH,
                iter_contents_file(f)):
                basename = os.path.basename(path)
                if not basename in lib_to_pkgs:
                    lib_to_pkgs[basename] = set()
                lib_to_pkgs[basename] |= pkgs
        return lib_to_pkgs

    def _download_contents_file_compressed(self, distroseries, arch):
        """ Downloads the content file for distroseries, arch into target """
        # XXX: we may eventually want to merge the Contents files from
        #      the -updates repository too in addition to the main archive
        url = self._get_contents_file_server_url(distroseries, arch)
        target = self._get_contents_file_cache_path(distroseries, arch)
        compressed_target = target + os.path.splitext(url)[1]
        # download
        urllib.urlretrieve(url, compressed_target)
        return compressed_target

    def _prune_contents_gz_file(self, infile, outfile):
        """ Read a compressed Contents.gz and write out a pruned version.

        This will use iter_contents_file to go over infile and write
        the relevant lines that are in the LD_SEARCH_PATH to outfile.
        """
        with open(outfile, "w") as outf, gzip.open(infile) as inf:
            # first write the header
            outf.write("FILE  LOCATION\n")
            # then iter over all relevant lines and write them out
            for (path, pkgs) in filter(
                lambda (p,pkgs): os.path.dirname(p) in self.LD_SEARCH_PATH,
                iter_contents_file(inf)):
                outf.write("%s %s\n" % (path, ",".join(pkgs)))

    def _download_and_prepare_contents_file_if_needed(self, distroseries, arch):
        """ Ensure there is a usable Contents file in the cachedir

        This will download, uncompress and prune a Conents file for
        distroseries, arch so that get_dependencies works.
        """
        # mvo: We can (and should eventually) do etag/if-modified-since
        #      matching here. But its not really important as long as
        #      we package for stable distroseries as the Contents file
        #      will not change
        path = self._get_contents_file_cache_path(distroseries, arch)
        if not os.path.exists(path):
            compressed_contents = self._download_contents_file_compressed(
                distroseries, arch)
            # and prune from ~300mb to 1mb uncompressed as we are only
            # interested in the library path parts
            self._prune_contents_gz_file(compressed_contents, path)
            os.remove(compressed_contents)

    def get_dependencies(self, lib, arch="i386"):
        # do lazy downloading for now, we could also make this part
        # of bin/fetch-symbols I guess(?)
        self._download_and_prepare_contents_file_if_needed(
            self.DISTROSERIES, arch)
        lib_to_pkgs = self._get_lib_to_pkgs_mapping(self.DISTROSERIES, arch)
        return lib_to_pkgs.get(lib)

    def close(self):
        pass


class PackageDatabase(object):

    # the various db backends, aptfile is a bit special
    SQLITE = 'sqlite'
    POSTGRES = 'postgres'
    APTFILE = 'aptfile'

    def __init__(self, store):
        self._store = store

    @classmethod
    def _get_storm_sqlite_connection_uri(cls, opts):
        raise ValueError(
            "SQLite is no longer supported, you must migrate to postgresql.")

    @classmethod
    def _get_storm_postgres_connection_uri(cls, opts):
        if not getattr(opts, 'database_db_name', None):
            raise ValueError(
                "Can't create database, no connection info available. "
                "You must specify %s. Looked in %s. "
                "Perhaps %s is set incorrectly?" % (
                    'db_name', get_config_file_path(), CONF_FILE_ENV_VAR))
        return URI(scheme=opts.database_db_type,
                   username=opts.database_username,
                   password=opts.database_password,
                   host=opts.database_host,
                   port=opts.database_port,
                   database=opts.database_db_name)

    @classmethod
    def _get_storm_connection_uri(cls, opts):
        if opts.database_db_type == cls.POSTGRES:
            return cls._get_storm_postgres_connection_uri(opts)
        elif opts.database_db_type == cls.SQLITE:
            return cls._get_storm_sqlite_connection_uri(opts)
        else:
            raise AssertionError(
                "Unsupported database: %s" % opts.database_db_type)

    @classmethod
    def get_db_info_from_config(cls, opts):
        return cls._get_storm_connection_uri(opts)

    @classmethod
    def get_store_from_config(cls, opts):
        """Create a storm store based on a config file.

        This method will create a storm store based
        on the information in ``~/.config/pkgme-binary/conf``

        :return: a tuple of (store, store_type), where store_type
            is one of cls.SQLITE or cls.POSTGRES, indicating what
            is at the other end of the store.
        """
        connection_info = cls.get_db_info_from_config(opts)
        database = create_database(connection_info)
        return Store(database)

    @classmethod
    def create(cls, store=None):
        if store is None:
            options = load_configuration().options
            # XXX: not elegant
            if options.database_db_type == cls.APTFILE:
                return AptFilePackageDatabase(options.database_aptfile_cachedir)
            store = cls.get_store_from_config(options)
        return cls(store)

    def get_dependencies(self, library_name, arch='i386'):
        """Get the binary packages that provide 'library_name'."""
        result = self._store.execute(
            "SELECT dependency FROM libdep WHERE library = ? AND architecture = ?",
                  (unicode(library_name), unicode(arch)))
        return set([dependency for [dependency] in result])

    def insert_new_library(self, source_package_name, library_name,
                           dependency, arch):
        """Insert a library and its needed dependency into the database.

        :param library_name: A full soname, e.g. libfoo.so.1.
        :param dependency: A binary package dependency, possibly including
            version.
        """
        self._store.execute(
            "INSERT INTO libdep VALUES (?, ?, ?, ?)",
            (unicode(source_package_name),
             unicode(library_name),
             unicode(dependency),
             unicode(arch)))

    def update_source_package(self, source_package_name, symbol_list):
        """Update the database with the symbols from 'source_package_name'.

        :param source_package_name: The name of the source package where the
            symbols came from.
        :param symbol_list: A list of representations of symbols files, where each
            representation is a list of tuples of library and
            dependency and an architecture string.
            e.g. [([(libfoo, foo), ...], 'i386'), ...].
            Each architecture should only appear once in the list.
        """
        for symbols in symbol_list:
            deps, architecture = symbols
            self._store.execute(
                    "DELETE FROM libdep WHERE source_package_name = ? "
                    "AND architecture = ?",
                    (unicode(source_package_name), unicode(architecture)))
            for library, dependency in deps:
                self.insert_new_library(
                    source_package_name, library, dependency, architecture)
        self._store.commit()

    def close(self):
        self._store.close()


def build_symbol_list(symbols):
    symbol_list = [
        (list(iter_so_names(symbols)), architecture)
        for symbols, architecture in symbols]
    return symbol_list


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
        symbol_list = build_symbol_list(package.iter_symbols())
    db.update_source_package(package_name, symbol_list)


def main():
    """Import the symbol files for 'package_name'."""
    glue = load_configuration()
    with closing(PackageDatabase.get_store_from_config(glue.options)) as store:
        package_name = glue.args[0]
        db = PackageDatabase(store)
        fetch_symbol_files(glue.options.scan_mode, package_name, db)
