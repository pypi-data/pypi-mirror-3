import random
import unittest
import duolingo
import urlparse
import httplib2
import urllib
import json

CONSUMER_KEY = ''
CONSUMER_SECRET = ''

ACCESS_KEY = ''
ACCESS_SECRET = ''

USERNAME = ''
PASSWORD = ''

LOGIN_URL = 'http://localhost:8080/login'
ALLOW_URL = 'http://localhost:8080/oauth/allow'
REVOKE_URL = 'http://localhost:8080/oauth/revoke'

class TestAuthorization(unittest.TestCase):
    """tests the oauth authorization"""

    def setUp(self):
        self.duolingo = duolingo.Duolingo(consumer_key=CONSUMER_KEY, consumer_secret=CONSUMER_SECRET)
        self.http = httplib2.Http()

    def tearDown(self):
        pass

    def test_initialization(self):
        self.assertRaises(duolingo.BadInitializationError, duolingo.Duolingo, consumer_key='erw', access_secret='jker')
        self.assertRaises(duolingo.BadInitializationError, duolingo.Duolingo, consumer_secret='erw', access_secret='jker')

    def test_request_token(self):
        self.duolingo.request_token()

    @unittest.skip
    def test_flow(self):
        #get request token
        url = self.duolingo.request_token()
        oauth_token = url.split('oauth_token')[1][1:]
        #login as user and authorize application
        self.login()
        verifier = self.allow(oauth_token)
        #get access token
        self.duolingo.access_token(verifier)
        #delete installation
        self.revoke(self.duolingo._access_token.key)

    def login(self):
        body = {'login': USERNAME, 'password': PASSWORD}
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        response, content = self.http.request(LOGIN_URL, 'POST', headers=headers, body=urllib.urlencode(body))
        self.cookie = response['set-cookie']

    def allow(self, oauth_token):
        body = {'oauth_token': oauth_token}
        headers = {'Content-type': 'application/x-www-form-urlencoded', 'Cookie': self.cookie}
        response, content = self.http.request(ALLOW_URL, 'POST', headers=headers, body=urllib.urlencode(body))
        redirect = json.loads(content)['redirect']
        verifier = dict(urlparse.parse_qsl(urlparse.urlparse(redirect).query))['verifier']
        return verifier

    def revoke(self, oauth_token):
        body = {'oauth_token': oauth_token}
        headers = {'Content-type': 'application/x-www-form-urlencoded', 'Cookie': self.cookie}
        response, content = self.http.request(REVOKE_URL, 'POST', headers=headers, body=urllib.urlencode(body))

class TestDuolingo(unittest.TestCase):
    """tests the actual duolingo API calls."""

    def setUp(self):
        self.duolingo = duolingo.Duolingo(consumer_key=CONSUMER_KEY, consumer_secret=CONSUMER_SECRET, access_key=ACCESS_KEY, access_secret=ACCESS_SECRET)

    def tearDown(self):
        pass

    def test_create_translate_job(self):
        job = self.duolingo.create_translate_job({
            u'title': u'Hello',
            u'text': u'erfsssafs',
            u'source_language': u'en',
            u'target_language': u'es',
            u'license': u'cc',
        })
        self.assertEquals('submitted', job['state'])

    def test_get_translate_job(self):
        #create translate job
        job = self.duolingo.create_translate_job({
            u'title': u'Hello',
            u'text': u'erfsssafs',
            u'source_language': u'en',
            u'target_language': u'es',
            u'license': u'cc',
        })
        #get it again
        job2 = self.duolingo.get_translate_job(job['id'])
        self.assertEquals(job2, job)

    def test_cancel_job(self):
        job = self.duolingo.create_translate_job({
            u'title': u'Hello',
            u'text': u'erfsssafs',
            u'source_language': u'en',
            u'target_language': u'es',
            u'license': u'cc',
        })
        job.cancel()
        self.assertEquals('cancelled', job['state'])

    @unittest.skip
    def test_approve_job(self):
        job = self.duolingo.create_translate_job({
            u'title': u'Hello',
            u'text': u'erfsssafs',
            u'source_language': u'en',
            u'target_language': u'es',
            u'license': u'cc',
        })
        job.approve()
        self.assertEquals('approved', job['state'])

    @unittest.skip
    def test_reject_job(self):
        job = self.duolingo.create_translate_job({
            u'title': u'Hello',
            u'text': u'erfsssafs',
            u'source_language': u'en',
            u'target_language': u'es',
            u'license': u'cc',
        })
        job.reject('not a good translation')
        self.assertEquals('rejected', job['state'])

if __name__ == '__main__':
    unittest.main()