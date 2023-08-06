# Copyright 2011-2012 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

import json
from StringIO import StringIO

from fixtures import MonkeyPatch
from pkgme.info_elements import PackageName
from testtools import TestCase

from devportalbinary.backend import (
    all_info,
    BASE_USER_ERROR,
    _convert_info,
    USER_ERROR_RETURN_CODE,
    want,
    )


class DummyBackend(object):

    def __init__(self, want, metadata):
        self._want = want
        self._metadata = metadata

    def get_metadata(self):
        return self._metadata

    def get_info(self, metadata):
        return {PackageName: metadata}

    def want(self):
        return self._want


class BrokenBackend(object):

    def __init__(self, error, *args, **kwargs):
        self._error = error
        self._args = args
        self._kwargs = kwargs

    def _raise(self):
        raise self._error(*self._args, **self._kwargs)

    def get_metadata(self):
        return {}

    def get_info(self, metadata):
        raise self._raise()

    def want(self):
        raise self._raise()


class TestDumpJSON(TestCase):

    def test_convert(self):
        package_name = self.getUniqueString()
        info = {PackageName: package_name}
        self.assertEqual(
            {PackageName.name: package_name}, _convert_info(info))


class TestAllInfo(TestCase):

    def test_all_info(self):
        metadata = {'foo': 'bar'}
        backend = DummyBackend(None, metadata)
        output = StringIO()
        all_info(backend, output)
        self.assertEqual(
            {PackageName.name: metadata}, json.loads(output.getvalue()))

    def test_default_to_stdout(self):
        stream = StringIO()
        self.useFixture(MonkeyPatch('sys.stdout', stream))
        metadata = {'foo': 'bar'}
        backend = DummyBackend(None, metadata)
        all_info(backend)
        self.assertEqual(
            {PackageName.name: metadata}, json.loads(stream.getvalue()))

    def test_return_zero_on_success(self):
        metadata = {'foo': 'bar'}
        backend = DummyBackend(None, metadata)
        output = StringIO()
        result = all_info(backend, output)
        self.assertEqual(0, result)

    def test_normal_error_raises(self):
        output = StringIO()
        backend = BrokenBackend(RuntimeError, "Told you so")
        self.assertRaises(RuntimeError, all_info, backend, output)

    def test_user_error_logs(self):
        output = StringIO()
        error = StringIO()
        backend = BrokenBackend(BASE_USER_ERROR, "Told you so")
        result = all_info(backend, output, error)
        self.assertEqual(USER_ERROR_RETURN_CODE, result)
        self.assertEqual('', output.getvalue())
        self.assertEqual("Told you so\n", error.getvalue())

    def test_error_in_get_metatada(self):
        output = StringIO()
        error = StringIO()
        backend = BrokenBackend(BASE_USER_ERROR, "Told you so")
        backend.get_metadata = backend._raise
        result = all_info(backend, output, error)
        self.assertEqual(USER_ERROR_RETURN_CODE, result)
        self.assertEqual('', output.getvalue())
        self.assertEqual("Told you so\n", error.getvalue())


class TestWant(TestCase):

    def test_default_to_stdout(self):
        stream = StringIO()
        self.useFixture(MonkeyPatch('sys.stdout', stream))
        want_reason = {'score': 10, 'reason': 'reason'}
        backend = DummyBackend(want_reason, None)
        want(backend)
        self.assertEqual(want_reason, json.loads(stream.getvalue()))

    def test_return_zero_on_success(self):
        want_reason = {'score': 10, 'reason': 'reason'}
        backend = DummyBackend(want_reason, None)
        output = StringIO()
        result = want(backend, output)
        self.assertEqual(0, result)

    def test_normal_error_raises(self):
        output = StringIO()
        backend = BrokenBackend(RuntimeError, "Told you so")
        self.assertRaises(RuntimeError, want, backend, output)

    def test_user_error_logs(self):
        output = StringIO()
        error = StringIO()
        backend = BrokenBackend(BASE_USER_ERROR, "Told you so")
        result = want(backend, output, error)
        self.assertEqual(USER_ERROR_RETURN_CODE, result)
        self.assertEqual('', output.getvalue())
        self.assertEqual("Told you so\n", error.getvalue())
