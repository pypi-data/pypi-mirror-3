import urlparse
import oauth2 as oauth
import json
import httplib
import urllib

class BadInitializationError(Exception):
    pass

class BadStateError(Exception):
    pass

class AuthenticationError(Exception):
    pass

class NotAuthorizedError(Exception):
    pass

class DuolingoError(Exception):
    pass

REQUEST_TOKEN_URL = 'http://localhost:8080/oauth/request_token'
ACCESS_TOKEN_URL = 'http://localhost:8080/oauth/access_token'
AUTHORIZE_URL = 'http://localhost:8080/#/oauth/authorize'

BASE_URL = 'http://localhost:8080/'


class Duolingo(object):

    def __init__(self, consumer_key=None, consumer_secret=None, access_key=None, access_secret=None):
        if consumer_key != None and consumer_secret != None and access_key != None and access_secret != None:
            self._access_token = oauth.Token(key=access_key, secret=access_secret)
            self.consumer = oauth.Consumer(consumer_key, consumer_secret)
            self.client = oauth.Client(self.consumer, self._access_token)
            self.state = 'authorized'
        elif consumer_key != None and consumer_secret != None:
            self.consumer = oauth.Consumer(consumer_key, consumer_secret)
            self.state = 'unauthorized'
        else:
            raise BadInitializationError("you must initialize with at least a access_key/access_secret pair")

    def request_token(self):
        if not self.state == 'unauthorized':
            raise BadStateError("you must be unauthorized to call this methoed")
        client = oauth.Client(self.consumer)
        resp, content = client.request(REQUEST_TOKEN_URL, "GET")
        if resp['status'] != '200':
            raise AuthenticationError("Invalid response %s." % resp['status'])
        request_token = dict(urlparse.parse_qsl(content))
        self.request_token = oauth.Token(key=request_token['oauth_token'], secret=request_token['oauth_token_secret'])
        self.state = 'requested'
        return "%s?oauth_token=%s" % (AUTHORIZE_URL, request_token['oauth_token'])

    def access_token(self, oauth_verifier):
        if not self.state == 'requested':
            raise BadStateError("you must have a request token first")
        self.request_token.set_verifier(oauth_verifier)
        client = oauth.Client(self.consumer, self.request_token)
        resp, content = client.request(ACCESS_TOKEN_URL, "POST")
        access_token = dict(urlparse.parse_qsl(content))
        self._access_token = oauth.Token(key=access_token['oauth_token'], secret=access_token['oauth_token_secret'])
        self.client = oauth.Client(self.consumer, self._access_token)
        self.state = 'authorized'

    def __access_resource(self, url, method='GET', parameters={}, values={}):
        actual_url = url.replace('{{id}}', str(values['id'])) if 'id' in values else url
        if len(parameters)==0:
            resp, content = self.client.request(actual_url, method=method)
        else:
            resp, content = self.client.request(actual_url, method=method, body=urllib.urlencode(parameters))
        if resp['status'] != '200':
            raise DuolingoError("could not retrieve job:"+content)
        else:    
            data = json.loads(content)
            if data == None:
                raise NotAuthorizedError()
            if len(data) == 0:
                raise NotAuthorizedError()
            return data

    def create_translate_job(self, job, sandbox=False):
        return TranslateJob(self, self.__access_resource(BASE_URL+'translate_jobs', method="POST", parameters={'model':json.dumps(job)}))

    def get_translate_job(self, id_):
        return TranslateJob(self, self.__access_resource(BASE_URL+'translate_jobs/{{id}}', values={'id':id_}))

class TranslateJob(dict):
    
    def __init__(self, duolingo, data={}):
        self.duolingo = duolingo
        self.update(data)

    def __call(self, url, parameters={}):
        data = self.duolingo.__access_resource(url, method='POST', parameters=parameters, values={'id': self['id']})
        self.update(data)

    def cancel(self):
        return self.__call(BASE_URL+'translate_jobs/{{id}}/cancel')

    def approve(self):
        return self.__call(BASE_URL+'translate_jobs/{{id}}/approve')
        
    def reject(self, reason):
        return self.__call(BASE_URL+'translate_jobs/{{id}}/reject', {'reason': reason})