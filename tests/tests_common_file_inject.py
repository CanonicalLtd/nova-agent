
from novaagent.common import file_inject


import logging
import base64
import shutil
import stat
import glob
import sys
import os


if sys.version_info[:2] >= (2, 7):
    from unittest import TestCase
else:
    from unittest2 import TestCase


try:
    from unittest import mock
except ImportError:
    import mock


class TestHelpers(TestCase):
    def setUp(self):
        logging.disable(logging.ERROR)
        if not os.path.exists('/tmp/test_file'):
            with open('/tmp/test_file', 'a+') as f:
                f.write('This is a test file')
                os.utime('/tmp/test_file', None)

            fd = os.open('/tmp/test_file', os.O_RDONLY)
            os.fchmod(
                fd,
                stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH
            )

    def tearDown(self):
        logging.disable(logging.NOTSET)
        files = glob.glob('/tmp/test_file*')
        for item in files:
            os.remove(item)

        try:
            shutil.rmtree('/tmp/tests')
        except Exception:
            pass

    # Fix for python 2.x
    def permissions_to_unix_name(self, os_stat):
        is_dir = 'd' if stat.S_ISDIR(os_stat.st_mode) else '-'
        permissions_dict = {
            '7': 'rwx',
            '6': 'rw-',
            '5': 'r-x',
            '4': 'r--',
            '0': '---'
        }
        perms = str(oct(os_stat.st_mode)[-3:])
        readable_perms = is_dir + ''.join(
            permissions_dict.get(x, x) for x in perms
        )
        return readable_perms

    def test_file_permission(self):
        class MockStat(object):
            def __init__(self):
                self.st_mode = 33188
                self.st_uid = 1001
                self.st_gid = 1001

        with mock.patch('novaagent.common.file_inject.os.stat') as stat:
            stat.return_value = MockStat()
            mode, uid, gid = file_inject._get_file_permissions(
                '/tmp/test_file'
            )

        self.assertEqual(mode, 33188, 'Mode is not expected value')
        self.assertEqual(uid, 1001, 'UID is not expected value')
        self.assertEqual(gid, 1001, 'GID is not expected value')

    def test_file_permission_exception(self):
        os.remove('/tmp/test_file')
        mode, uid, gid = file_inject._get_file_permissions('/tmp/test_file')
        self.assertEqual(mode, None, 'Mode is not expected value')
        self.assertEqual(uid, 0, 'UID is not expected value')
        self.assertEqual(gid, 0, 'GID is not expected value')

    def test_write_file(self):
        file_inject._write_file(
            '/tmp/test_file_write',
            'File Contents'
        )
        files = glob.glob('/tmp/test_file*')
        self.assertEqual(
            len(files),
            2,
            'Did not find any files'
        )
        found_file = False
        temp_contents = None
        for f in files:
            if '/tmp/test_file_write' == f:
                with open(f) as temp_file:
                    temp_contents = temp_file.read()

                found_file = True

        assert found_file, 'Did not find written file in expected path'
        self.assertEqual(
            temp_contents,
            'File Contents',
            'Written data in file is not what was expected'
        )
        permissions = os.stat('/tmp/test_file_write')
        try:
            readable_perms = stat.filemode(permissions.st_mode)
        except Exception:
            readable_perms = self.permissions_to_unix_name(permissions)

        self.assertEqual(
            readable_perms,
            '-rw-------',
            'Permissions are not 600 as expected'
        )

    def test_write_file_existing_file(self):
        file_inject._write_file(
            '/tmp/test_file',
            'File Contents'
        )
        files = glob.glob('/tmp/test_file*')
        self.assertEqual(
            len(files),
            2,
            'Did not find any files'
        )
        found_file = False
        temp_contents = None
        for f in files:
            if '/tmp/test_file' == f:
                with open(f) as temp_file:
                    temp_contents = temp_file.read()

                found_file = True

        assert found_file, 'Did not find written file in expected path'
        self.assertEqual(
            temp_contents,
            'File Contents',
            'Written data in file is not what was expected'
        )
        permissions = os.stat('/tmp/test_file')
        try:
            readable_perms = stat.filemode(permissions.st_mode)
        except Exception:
            readable_perms = self.permissions_to_unix_name(permissions)

        self.assertEqual(
            readable_perms,
            '-rw-r--r--',
            'Permissions are not 644 as expected'
        )

    def test_instantiate_file_inject(self):
        file_inject.FileInject()
        assert True, 'Class did not generate exception'

    def test_inject_file_cmd(self):
        test = file_inject.FileInject()
        encode_details = base64.b64encode(
            b'/tmp/tests/test_file_write,Testing the inject'
        )
        error, message = test.injectfile_cmd(encode_details)
        self.assertEqual(error, "0", "Did not get expected error code")
        self.assertEqual(
            message,
            "",
            "Did not get expected message on success"
        )
        files = glob.glob('/tmp/tests/test_file*')
        self.assertEqual(
            len(files),
            1,
            'Did not find any files'
        )
        found_file = False
        temp_contents = None
        for f in files:
            if '/tmp/tests/test_file_write' == f:
                with open(f) as temp_file:
                    temp_contents = temp_file.read()

                found_file = True

        assert found_file, 'Did not find written file in expected path'
        self.assertEqual(
            temp_contents,
            'Testing the inject',
            'Written data in file is not what was expected'
        )
        permissions = os.stat('/tmp/tests/test_file_write')
        try:
            readable_perms = stat.filemode(permissions.st_mode)
        except Exception:
            readable_perms = self.permissions_to_unix_name(permissions)

        self.assertEqual(
            readable_perms,
            '-rw-------',
            'Permissions are not 600 as expected'
        )

    def test_inject_file_cmd_exception(self):
        test = file_inject.FileInject()
        error, message = test.injectfile_cmd('Unencoded data')
        self.assertEqual(error, "500", "Did not get expected error code")
        self.assertEqual(
            message,
            "Error doing base64 decoding of data",
            "Did not get expected message on error"
        )
