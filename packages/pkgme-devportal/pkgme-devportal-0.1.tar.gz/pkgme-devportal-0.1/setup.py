# Copyright 2011 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

import distribute_setup
distribute_setup.use_setuptools()

from setup_helpers import (
    description,
    get_version,
    )
from setuptools import setup, find_packages


__version__ = get_version('devportalbinary/__init__.py')

setup(
    name='pkgme-devportal',
    version=__version__,
    packages=find_packages(),
    include_package_data=True,
    maintainer='pkgme developers',
    maintainer_email='pkgme-devs@lists.launchpad.net',
    description=description('README'),
    license='AGPLv3',
    url='http://launchpad.net/pkgme-devportal',
    download_url='https://launchpad.net/pkgme-devportal/+download',
    test_suite='devportalbinary.tests',
    install_requires = [
        'bzr',
        'configglue',
        'launchpadlib',
        'PIL',
        'pkgme',
        'fixtures',
        'storm',
        ],
    entry_points = {
        'console_scripts': [
            'fetch-symbol-files=devportalbinary.database:main',
            'guess-executable=devportalbinary.binary:print_executable',
            'guess-deps=devportalbinary.binary:print_dependencies',
            ],
        'pkgme.get_backends_path': ['binary=devportalbinary:get_backends_path'],
        },
    # Auto-conversion to Python 3.
    use_2to3=True,
    )
