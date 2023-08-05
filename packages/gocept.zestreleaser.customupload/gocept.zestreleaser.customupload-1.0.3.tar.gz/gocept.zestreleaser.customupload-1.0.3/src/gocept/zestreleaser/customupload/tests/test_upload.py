# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.zestreleaser.customupload.upload
import mock
import tempfile
import unittest


class UploadTest(unittest.TestCase):

    context = {
        'tagdir': '/tmp/tha.example-0.1dev',
        'tag_already_exists': False,
        'version': '0.1dev',
        'workingdir': '/tmp/tha.example-svn',
        'name': 'tha.example',
        }

    @mock.patch('gocept.zestreleaser.customupload.upload.choose_destination')
    @mock.patch('zest.releaser.utils.ask')
    def test_no_destination_should_be_noop(self, ask, choose):
        choose.return_value = None
        gocept.zestreleaser.customupload.upload.upload(self.context)
        self.assertFalse(ask.called)

    @mock.patch('gocept.zestreleaser.customupload.upload.choose_destination')
    @mock.patch('zest.releaser.utils.ask')
    @mock.patch('os.system')
    def test_no_confirmation_should_exit(self, system, ask, choose):
        choose.return_value = 'server'
        ask.return_value = False
        gocept.zestreleaser.customupload.upload.upload(self.context)
        self.assertTrue(ask.called)
        self.assertFalse(system.called)

    @mock.patch('gocept.zestreleaser.customupload.upload.choose_destination')
    @mock.patch('zest.releaser.utils.ask')
    @mock.patch('os.system')
    @mock.patch('glob.glob')
    def test_call_scp(self, glob, system, ask, choose):
        choose.return_value = 'server'
        ask.return_value = True
        glob.return_value = ['/tmp/tha.example-0.1dev/dist/tha.example-0.1dev.tar.gz']
        gocept.zestreleaser.customupload.upload.upload(self.context)
        system.assert_called_with(
            'scp /tmp/tha.example-0.1dev/dist/tha.example-0.1dev.tar.gz server')


class ConfigTest(unittest.TestCase):

    @mock.patch('os.path.expanduser')
    def test_returns_configparser(self, expanduser):
        tmpfile = tempfile.NamedTemporaryFile()
        expanduser.return_value = tmpfile.name
        tmpfile.write("""
[gocept.zestreleaser.customupload]
my.package = my.dest
other.package = other.dest
""")
        tmpfile.flush()
        config = gocept.zestreleaser.customupload.upload.read_configuration()
        self.assertEqual('my.dest', config.get(
            'gocept.zestreleaser.customupload', 'my.package'))
