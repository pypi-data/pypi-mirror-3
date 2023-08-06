# Copyright 2011-2012 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

import json

from pkgme.testing import TempdirFixture

from devportalbinary.binary import MetadataBackend
from devportalbinary.pdf import PdfBackend
from devportalbinary.testing import BackendTests


class PdfBackendTests(BackendTests):

    BACKEND = PdfBackend

    def make_metadata_file(self, tempdir, metadata=None):
        if metadata is None:
            metadata = {}
        tempdir.create_file(
            MetadataBackend.METADATA_FILE, json.dumps(metadata))

    def test_want_with_metadata(self):
        # If we detect the metadata file and a pdf, then we score 20.
        tempdir = self.useFixture(TempdirFixture())
        self.make_metadata_file(tempdir)
        filename = self.getUniqueString() + ".pdf"
        tempdir.touch(filename)
        backend = PdfBackend(tempdir.path)
        self.assertEqual(20, backend.want())

    def test_want_with_just_metadata(self):
        # If we detect just the metadata file then we score 0.
        tempdir = self.useFixture(TempdirFixture())
        self.make_metadata_file(tempdir)
        backend = PdfBackend(tempdir.path)
        self.assertEqual(0, backend.want())

    def test_want_with_just_pdf(self):
        # If we detect just a pdf file then we score 0.
        tempdir = self.useFixture(TempdirFixture())
        filename = self.getUniqueString() + ".pdf"
        tempdir.touch(filename)
        backend = PdfBackend(tempdir.path)
        self.assertEqual(0, backend.want())

    def test_want_with_extra_files(self):
        # If we detect other files then we score 0. This is so that
        # this backend doesn't trigger on something that just happens
        # to contain a pdf.
        tempdir = self.useFixture(TempdirFixture())
        self.make_metadata_file(tempdir)
        filename = self.getUniqueString() + ".pdf"
        tempdir.touch(filename)
        other_filename = self.getUniqueString() + ".foo"
        tempdir.touch(other_filename)
        backend = PdfBackend(tempdir.path)
        self.assertEqual(0, backend.want())

    def test_want_with_debian_dir(self):
        # If the other file is a debian dir then we score 20 still.
        # This just makes local testing of the backend easier.
        tempdir = self.useFixture(TempdirFixture())
        self.make_metadata_file(tempdir)
        filename = self.getUniqueString() + ".pdf"
        tempdir.touch(filename)
        other_filename = "debian"
        tempdir.touch(other_filename)
        backend = PdfBackend(tempdir.path)
        self.assertEqual(20, backend.want())

    def test_want_with_icons(self):
        tempdir = self.useFixture(TempdirFixture())
        icon_file = self.getUniqueString() + '.png'
        tempdir.touch(icon_file)
        self.make_metadata_file(
            tempdir, {'icons': {'48x48': icon_file}})
        filename = self.getUniqueString() + ".pdf"
        tempdir.touch(filename)
        backend = PdfBackend(tempdir.path)
        self.assertEqual(20, backend.want())

    def test_architecture(self):
        # The pdf backend set architecture to all
        backend = self.make_backend()
        architecture = backend.get_architecture(None)
        self.assertEqual('all', architecture)

    def test_build_depends(self):
        # The pdf backend has simple build dependencies
        backend = self.make_backend()
        build_depends = backend.get_build_depends(None)
        self.assertEqual('debhelper (>=7)', build_depends)

    def test_depends(self):
        # The pdf backend depends on xdg-utils
        backend = self.make_backend()
        depends = backend.get_depends(None)
        self.assertEqual('xdg-utils, ${misc:Depends}', depends)

    def test_description(self):
        # The pdf backend gets the description from the metadata file.
        expected_description = 'best pdf evar'
        metadata = {MetadataBackend.DESCRIPTION: expected_description}
        backend = self.make_backend()
        description = backend.get_description(metadata)
        self.assertEqual(expected_description, description)

    def test_executable_opens_pdf(self):
        tempdir = self.useFixture(TempdirFixture())
        tempdir.touch('foo.pdf')
        package_name = self.getUniqueString()
        backend = PdfBackend(tempdir.path)
        executable = backend.get_executable(package_name)
        self.assertEqual(
            '/usr/bin/xdg-open /opt/%s/%s' % (package_name, 'foo.pdf'),
            executable)
