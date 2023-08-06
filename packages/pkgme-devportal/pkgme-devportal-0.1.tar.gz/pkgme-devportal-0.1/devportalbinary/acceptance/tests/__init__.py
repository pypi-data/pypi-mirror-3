import os
import shutil

from fixtures import Fixture, MonkeyPatch
from testtools import TestCase
from testtools.matchers import PathExists

import pkgme
from pkgme.testing import TempdirFixture
from pkgme.debuild import build_source_package

from devportalbinary.testing import DatabaseFixture, IsImage


class TestData(Fixture):

    def __init__(self, datadir):
        self.datadir = datadir

    def setUp(self):
        Fixture.setUp(self)
        tempdir = self.useFixture(TempdirFixture())
        self.path = os.path.join(tempdir.path, "target")
        source_path = os.path.join(
            os.path.dirname(__file__), "..", "data", self.datadir)
        shutil.copytree(source_path, self.path)


class AcceptanceTests(TestCase):

    def setUp(self):
        super(AcceptanceTests, self).setUp()
        backend_dir = os.path.join(
            os.path.dirname(__file__), "..", "..", "..", "devportalbinary",
            "backends")
        self.useFixture(
            MonkeyPatch("pkgme.backend.EXTERNAL_BACKEND_PATHS", [backend_dir]))

    def run_pkgme(self, test_data):
        pkgme.write_packaging(
            test_data.path, allowed_backend_names=["binary", "pdf"])
        # also try to build the package to catch any errors there
        build_source_package(test_data.path, sign=False)

    def test_empty(self):
        """Should fail for a project with no binaries."""
        test_data = self.useFixture(TestData("empty"))
        self.assertRaises(
            Exception, self.run_pkgme, test_data)

    def test_python(self):
        """Should fail for a Python project."""
        test_data = self.useFixture(TestData("python"))
        self.assertRaises(
            Exception, self.run_pkgme, test_data)

    def test_gtk(self):
        """Runs successfully for a basic GTK+ application."""
        dep_db = self.useFixture(DatabaseFixture())
        dep_db.db.update_source_package("pthreads", [[("libpthread.so.0", "libpthread0")]])
        dep_db.db.update_source_package("eglibc", [[("libc.so.6", "libc6")]])
        test_data = self.useFixture(TestData("gtk"))
        self.run_pkgme(test_data)
        self.assertThat(
            os.path.join(test_data.path, "debian", "control"), PathExists())

    def test_bundled_library(self):
        """Runs successfully for a basic bundled libary."""
        dep_db = self.useFixture(DatabaseFixture())
        dep_db.db.update_source_package("eglibc", [[("libc.so.6", "libc6")]])
        test_data = self.useFixture(TestData("bundled_lib"))
        self.run_pkgme(test_data)
        self.assertThat(
            os.path.join(test_data.path, "debian", "control"), PathExists())
        self.assertIn(
            "\noverride_dh_shlibdeps:\n\t",
            open(os.path.join(test_data.path, "debian", "rules")).read())

    def test_pdf(self):
        test_data = self.useFixture(TestData("pdf"))
        self.run_pkgme(test_data)
        self.assertThat(
            os.path.join(test_data.path, "debian", "control"), PathExists())

    def test_pdf_with_icons(self):
        test_data = self.useFixture(TestData("pdf_with_icons"))
        self.run_pkgme(test_data)
        self.assertThat(
            os.path.join(test_data.path, "debian", "control"), PathExists())
        self.assertThat(
            os.path.join(
                test_data.path, "debian", "icons", "48x48", "jabberwocky.png"),
            PathExists())

    def test_pdf_with_icons_wrong_size(self):
        test_data = self.useFixture(TestData("pdf_with_icons_wrong_size"))
        self.run_pkgme(test_data)
        self.assertThat(
            os.path.join(test_data.path, "debian", "control"), PathExists())
        generated_icon = os.path.join(
            test_data.path, "debian", "icons", "48x48", "jabberwocky.png")
        self.assertThat(generated_icon, PathExists())
        self.assertThat(
            generated_icon, IsImage(width=48, height=48, kind="png"))


def test_suite():
    import unittest
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(__name__)
    return suite
