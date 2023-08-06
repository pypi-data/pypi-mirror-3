# oosapy
# Copyright 11870.com
# See LICENSE for details.

import urllib
import cgi

import httplib2

from error import OosApyError
import api
import oauth


def _extract_params(url):
    parts = url.split('?')
    if len(parts) == 1:
        return {}
    params = cgi.parse_qs(url.split('?')[1])
    for k,v in params.iteritems():
        params[k] = v[0]
    return params

def _add_params(url, params):
    if len(params) == 0:
        return url
    separator = "?" if url.find("?") == -1 else "&"
    return url + separator + urllib.urlencode(params)

def _manage_parameters(url, parameters):
    params = parameters.copy()
    params.update(_extract_params(url))

    new_url = _add_params(url.split("?")[0], params)

    return new_url, params

def _check_response(resp):
    def get_message(data):
        s = data.index("<message>")+len("<message>")
        e = data.index("</message>")
        return data[s:e]

    status = int(resp[0]['status'])
    if status == 400:
        raise OosApyError("Bad request", resp)
    elif status == 401:
        raise OosApyError("Authentication error", resp)
    elif status == 403:
        raise OosApyError(get_message(resp[1]), resp)
    elif status == 404:
        raise OosApyError("Not found", resp)
    elif status == 500:
        raise OosApyError("Server error", resp)


class AuthenticationMethod():
    def is_anonymous(self):
        raise NotImplementedError

    def get_response(self, url, method='GET', body='', headers={}
                     , parameters={}):
        raise NotImplementedError

    def check_authentication(self):
        return True
        url = api.API.ROOT_URL + "/service"
        self.get_response(url)


class AnonymousAuthentication(AuthenticationMethod):
    """Class to handle the anonymous authentication.

    consumer_key -- the consumer key

    """

    def __init__(self, consumer_key):
        self.consumer_key = consumer_key
        self.connection = httplib2.Http()
        self.check_authentication()

    def is_anonymous(self):
        return True

    def get_response(self, url, method='GET', body='', headers={}
                     , parameters={}):
        """Get the response with the anonymous authentication"""
        url = _manage_parameters(url, parameters)[0]

        heads = headers.copy()
        heads['Authorization'] = 'app-token'
        heads['appToken'] = self.consumer_key
        resp = self.connection.request(url, 'GET', body, heads)
        _check_response(resp)
        return resp


class OAuthAuthentication(AuthenticationMethod):
    """Class to handle the OAuth user authentication and authorization.

    consumer_key -- the consumer key
    consumer_secret -- the consumer secret
    access_token -- the user access token
    token_secret -- the secret for the access token
    callback -- redirect url for requesting OAuth token

    """

    OAUTH_HOST = '11870.com'
    OAUTH_ROOT = '/services/manage-api/'

    def __init__(self, consumer_key, consumer_secret,
                 access_token=None, token_secret=None, callback=None):
        self._consumer = oauth.OAuthConsumer(consumer_key, consumer_secret)
        self._sigmethod = oauth.OAuthSignatureMethod_HMAC_SHA1()
        self.request_token = None
        self.access_token = None
        self.callback = callback
        if access_token != None and token_secret != None:
            self.access_token = oauth.OAuthToken(access_token, token_secret)
        self.connection = httplib2.Http()

        self.check_authentication()

    def is_anonymous(self):
        return False

    def _get_oauth_url(self, endpoint):
        return 'http://' + self.OAUTH_HOST + self.OAUTH_ROOT + endpoint

    def get_response(self, url, method='GET', body='', headers={}
                     , parameters={}):
        """Get the response with the OAuth authentication"""
        heads = headers.copy()

        url, params = _manage_parameters(url, parameters)

        if not heads.has_key("Content-Type"):
            heads["Content-Type"] = "application/atom+xml"

        if heads.get("Content-Type", "") == "application/x-www-form-urlencoded":
            params.update(_extract_params('?'+body))

        request = oauth.OAuthRequest.from_consumer_and_token(
            self._consumer, http_url=url, http_method=method,
            token=self.access_token, parameters=params
        )
        request.sign_request(self._sigmethod, self._consumer, self.access_token)
        heads.update(request.to_header())
        resp = self.connection.request(url, method, body, heads)
        _check_response(resp)
        return resp

    def _get_request_token(self):
        url = self._get_oauth_url('request-token')
        request = oauth.OAuthRequest.from_consumer_and_token(
            self._consumer, http_url=url, callback=self.callback
        )
        request.sign_request(self._sigmethod, self._consumer, None)
        resp = self.connection.request(url, 'GET', headers=request.to_header())
        self.request_token = oauth.OAuthToken.from_string(resp[1])
        return self.request_token


    def set_request_token(self, key, secret):
        self.request_token = oauth.OAuthToken(key, secret)

    def set_access_token(self, key, secret):
        self.access_token = oauth.OAuthToken(key, secret)

    def get_authorization_url(self, write=False):
        """Get the authorization URL where the user can give his permission.

        The request token is requested and used in the URL.

        write -- set to true if write permission is needed

        """
        # get the request token
        self._get_request_token()

        # build auth request and return as url
        url = self._get_oauth_url('authorize')

        parameters = {}
        if write:
            parameters['privilege'] = 'WRITE'

        request = oauth.OAuthRequest.from_token_and_callback(
            token=self.request_token, http_url=url, parameters=parameters
        )

        return request.to_url()

    def get_access_token(self, verifier=None):
        """After the user has given its authorization, get access token with
        the received verifier."""
        url = self._get_oauth_url('access-token')

        # build request
        request = oauth.OAuthRequest.from_consumer_and_token(
            self._consumer,
            token=self.request_token, http_url=url,
            verifier=str(verifier)
        )
        request.sign_request(self._sigmethod, self._consumer,
                             self.request_token)

        # send request
        resp = self.connection.request(url, 'GET', headers=request.to_header())
        self.access_token = oauth.OAuthToken.from_string(resp[1])
        return self.access_token

