# Copyright 2011-2012 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

import os

from configglue import glue
from configglue import parser

from configglue.schema import (
    Schema,
    Section,
    DictOption,
    StringOption,
    TupleOption,
    )


# The environment variable that controls the config file location.
CONF_FILE_ENV_VAR = 'PKGME_DEVPORTAL_CONFIG_FILE'

# Where to look if the environment variable isn't set.
# XXX: 'pkgme-binary' is the historic name of this package.  Change this
# to look first in ~/.config/pkgme-devportal/conf and then fall back to
# this one.  Once production systems are updated to the new config, remove
# the fallback.
_DEFAULT_CONF_FILE = '~/.config/pkgme-binary/conf'


class DevportalSchema(Schema):

    # database
    database = Section()
    database.db_type = StringOption(default='sqlite',
            help=('The database to use, one of "sqlite", or "postgres"'))
    database.host = StringOption(
            help='The database host (for postgres)')
    database.port = StringOption(
            help='The database port (for postgres)')
    database.username = StringOption(
            help='The database username (for postgres)')
    database.password = StringOption(
            help='The database password (for postgres)')
    database.db_name = StringOption(
            help='The database name (for postgres)')
    database.path = StringOption(
            help='The path to the database file (for sqlite)')

    scan_mode = StringOption(
        help='To scan binary or source packages.')

    # overrides
    libraries = Section()
    default_lib_overrides = { 'libasound.so.2': 'libasound2',
                              'libGL.so.1': 'libgl1-mesa-glx',
                            }
    libraries.overrides = DictOption(
        default=default_lib_overrides,
        help='mapping of library name to pkgname to force picking selected '
             'dependencies')

    # The architectures that we fetch binary packages for.
    #
    # XXX: Really, we should be fetching the binary packages for _all_
    # architectures and storing their symbols in the database keyed by
    # architecture, and then using the architecture of the incoming binary to
    # figure out which libraries we need (XXX - not sure how multiarch affects
    # this.  Instead, for the moment we are assuming that all binaries are
    # i386.
    architectures = Section()
    architectures.supported = TupleOption(
        # XXX: mvo: it seems we don't need "all" here as we are interessted
        #           in binary symbols only?
        default=("i386",),
        help='The supported architectures')

def get_config_file_path():
    """Return the path to the configuration file."""
    from_env = os.environ.get(CONF_FILE_ENV_VAR, None)
    if from_env:
        return from_env
    return os.path.expanduser(_DEFAULT_CONF_FILE)


def load_configuration():
    config_location = get_config_file_path()
    config_files = []
    if os.path.exists(config_location):
        config_files.append(config_location)
    # tell the SchemaConfigParser that we need our data case-sensitive
    parser.SchemaConfigParser.optionxform = str
    return glue.configglue(DevportalSchema, config_files)
