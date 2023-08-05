# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.bender.http
import mock
import unittest
import urllib2


class HTTPServerTest(unittest.TestCase):

    port = 12345

    def setUp(self):
        self.bender = mock.Mock()
        self.httpd = gocept.bender.http.HTTPServer.start(
            'localhost', self.port, self.bender, 'user', 'pass')

    def tearDown(self):
        self.httpd.shutdown()

    def make_request(self, user=None, password=None, data='foo'):
        url = 'http://localhost:%s' % self.port
        passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
        passman.add_password(None, url, user, password)
        authhandler = urllib2.HTTPBasicAuthHandler(passman)
        opener = urllib2.build_opener(authhandler)
        return opener.open(url, data)

    def test_no_credentials_should_return_unauthorized(self):
        try:
            self.make_request()
        except urllib2.HTTPError, e:
            self.assertEqual(401, e.getcode())
        else:
            self.fail('nothing raised')

        self.assertFalse(self.bender.say.called)

    def test_wrong_credentials_should_return_unauthorized(self):
        try:
            self.make_request(user='wrong', password='invalid')
        except urllib2.HTTPError, e:
            self.assertEqual(401, e.getcode())
        else:
            self.fail('nothing raised')

        self.assertFalse(self.bender.say.called)

    def test_correct_credentials_should_work(self):
        self.make_request(user='user', password='pass')
        self.bender.say.assert_called_with('foo')
