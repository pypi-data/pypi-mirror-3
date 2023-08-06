#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
processors
"""

from __future__ import absolute_import

__author__ = "caelum - http://caelum.com.br"
__modified_by__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE.restfulie for details"

# Import here any required modules.
from base64 import b64encode
from urllib import splittype, splithost

from tornado.gen import Task, engine
from tornado.httputil import url_concat
from tornado.httpclient import AsyncHTTPClient, HTTPClient, HTTPError

__all__ = []

# Project requirements
from oauth2 import Request, Consumer, Token, SignatureMethod_HMAC_SHA1

try:
    from urlparse import parse_qs
except ImportError:
    # fall back for Python 2.5
    from cgi import parse_qs


# local submodule requirements
from .processor import AuthMixin

class AuthError(Exception):
    """Auth exception"""

class HandShakeError(Exception):
    """Error on auth process"""
    def __init__(self, response):
        Exception.__init__(self, response.error)
        self.response = response
    
#pylint: disable-msg=R0903
class BasicAuth(AuthMixin):
    """Processor responsible for making HTTP simple auth"""

    implements = "plain"

    def authorize(self, credentials, request, env, callback):
        self.authorize_sync(credentials, request, env)
        callable(callback) and callback()

    def authorize_sync(self, credentials, request, env):
        creden = credentials.to_list("consumer_key", "consumer_secret")
        encode = b64encode("%s:%s" % creden)
        request.headers['authorization'] = 'Basic %s' % encode


class OAuthMixin(AuthMixin):
    """ oauth method """

    @property
    def request_url(self):
        """Get request_token url according to OAuth 1.0 specs"""
        raise NotImplementedError

    @property
    def access_url(self):
        """Get access_token url according to OAuth 1.0 specs"""
        raise NotImplementedError

    @property
    def authorize_url(self):
        """Get authorize url according to OAuth 1.0 specs"""
        raise NotImplementedError

    @property
    #pylint: disable-msg=W0201
    def method(self):
        """Get method used to sign oauth requests"""
        if not hasattr(self, "_method"):
            self._method = SignatureMethod_HMAC_SHA1()
        return self._method

    ##
    # Fetch methods (HTTP/HTTPS)
    #
    def _fetch(self, consumer, token, params, uri, callback):
        """Send request async"""
        def on_response(response):
            if not response.error:
                return callback(Token.from_string(response.buffer.read()))
            raise HandShakeError(response)

        # process
        request = self._get_request(consumer, token, params, uri)
        AsyncHTTPClient().fetch(request.to_url(),
            callback=on_response,
            method=request.method,
            headers=request.to_header())

    def _fetch_sync(self, consumer, token, params, uri):
        """Send request sync"""
        request = self._get_request(consumer, token, params, uri)
        response = HTTPClient().fetch(uri,
            method=request.method,
            headers=request.to_header())
        return Token.from_string(response.buffer.read())

    ##
    # OAuth related (sugar) protected methods
    #
    @staticmethod
    def _get_realm(uri):
        """ calculate realm """
        schema, rest = splittype(uri)
        hierpart = ''
        if rest.startswith('//'):
            hierpart = '//'
        host, rest = splithost(rest)
        return schema + ':' + hierpart + host

    def _get_request(self, consumer, token, params, uri):
        """Prepare an oauth request based on arguments"""
        request = Request.from_consumer_and_token(
            consumer, token, parameters=params, http_url=uri)
        request.sign_request(self.method, consumer, token)
        return request

    def _get_consumer(self, credentials):
        """Prepare and store consumer based on oauth arguments"""
        if 'consumer' not in credentials.store(self.implements):
            creds = credentials.to_list("consumer_key", "consumer_secret")
            assert all(creds)
            credentials.store(self.implements)['consumer'] = Consumer(*creds)
        return credentials.store(self.implements)['consumer']

    def _get_token(self, credentials):
        """Prepare and store a token based on credentials"""
        if 'token' not in credentials.store(self.implements):
            creds = credentials.to_list("token_key", "token_secret")
            if all(creds):
                credentials.store(self.implements)['token'] = Token(*creds)
        return credentials.store(self.implements).get('token', None)

    ##
    # OAuth Public token adquisition methods
    #
    def request_token(self, credentials, callback=None):
        """Implements first stage on OAuth  dance async"""
        self._fetch(                                     \
            self._get_consumer(credentials),             \
            None, credentials.to_dict("oauth_callback"), \
            self.request_url, callback)

    def request_token_sync(self, credentials):
        """Implements first stage on OAuth dance sync"""
        return self._fetch_sync(                         \
            self._get_consumer(credentials),             \
            None, credentials.to_dict("oauth_callback"), \
                self.request_url)
    ###
    # OAuth authorization methods
    #
    def authorization_redirect(self, token):
        """Get the authorization URL to redirect the user"""
        request = Request.from_token_and_callback(       \
            token=token, http_url=self.authorize_url)
        return request.to_url()

    def authorization_redirect_url(self, token, callback):
        """Handle url redirection after user authenticates"""
        raise NotImplementedError

    def authorization_redirect_url_sync(self, token):
        """
        Handle url redirection after user authenticates syncronously
        """
        raise NotImplementedError

    ##
    # OAuth access methods
    #
    def access_token(self, credentials, token, verifier, callback):
        """
        After user has authorized the request token, get access token
        with user supplied verifier
        """
        self._fetch(                                     \
            self._get_consumer(credentials), token,      \
            {'oauth_verifier' : verifier}, self.access_url, callback)

    def access_token_sync(self, credentials, token, verifier):
        """
        After user has authorized the request token, get access token
        with user supplied verifier
        """
        return self._fetch_sync(                         \
            self._get_consumer(credentials), token,      \
            {'oauth_verifier' : verifier}, self.access_url)

    ###
    # XAuth stuff (2LO)
    #
    def xauth_access_token(self, credentials, callback):
        """
        Get an access token from an username and password combination.
        """
        parameters = {
            'x_auth_mode':     'client_auth',
            'x_auth_username': credentials.username,
            'x_auth_password': credentials.password,
            }

        self._fetch(                                    \
            self._get_consumer(credentials), None,      \
            parameters, self.access_url, callback)

    def xauth_access_token_sync(self, credentials):
        """
        Get an access token from an username and password combination.
        """
        parameters = {
            'x_auth_mode':     'client_auth',
            'x_auth_username': credentials.username,
            'x_auth_password': credentials.password,
            }

        self._fetch_sync(                              \
            self._get_consumer(credentials), None,     \
            parameters, self.access_url)

    ###
    # OAuth sign
    # 
    def sign(self, credentials, request, env):
        """Sign request"""
        
        #pylint: disable-msg=C0103
        POST_CONTENT_TYPE = 'application/x-www-form-urlencoded'

        consumer = self._get_consumer(credentials)
        token    = self._get_token(credentials)
        
        if not consumer or not token:
            raise AuthError("Missing oauth tokens")

        # POST
        headers  = request.headers
        if request.verb == "POST":
            assert 'content-type' in headers
            
        # Only hash body and generate oauth_hash for body if
        # Content-Type != form-urlencoded
        isform = headers.get('content-type') == POST_CONTENT_TYPE

        # process post contents if required
        body, parameters = env.get('body', ''), None
        if isform and body:
            parameters = parse_qs(body)

        # update request uri
        oauth_request = Request.from_consumer_and_token(
            consumer, token, request.verb,
            url_concat(request.uri, env["params"]),
            parameters, body, isform)

        # sign
        oauth_request.sign_request(self.method, consumer, token)

        # process body if form or uri if a get/head
        if isform:
            env['body'] = oauth_request.to_postdata()
        elif request.verb in ('GET', 'HEAD',):
            # remove params and update uri store params
            request.uri   = oauth_request.to_url()
            env["params"] = None
        else:
            headers.update(oauth_request.to_header(               \
                    realm=self._get_realm(request.uri)))

    @engine
    def _authenticate(self, credentials, callback):
        token = None
        try:
            if credentials.callback:
                # Use PIN based OAuth
                token = yield Task(self.request_token, credentials)
                reurl = self.authorization_redirect(token)
                verfy = credentials.callback(reurl)
                token = yield Task(self.access_token, credentials, token, verfy)
            else:
                # Use XAuth
                token = yield Task(self.xauth_access_token, credentials)
            # retval
            callback(token)
        # A handshake error is also notified.
        except HandShakeError, err:
            callback(err.response.error)
        except HTTPError, err:
            callback(err)

    def _authenticate_sync(self, credentials):
        token = None
        if credentials.callback:
            # Use PIN based OAuth
            token = self.request_token_sync(credentials)
            reurl = self.authorization_redirect(token)
            verfy = credentials.callback(reurl)
            token = self.access_token_sync(credentials, token, verfy)
        else:
            # Use XAuth
            token = self.xauth_access_token_sync(credentials)
        return token

    def _update_credentials(self, credentials, token):
        # store token
        credentials.store(self.implements)['token'] = None
        if isinstance(token, Token):
            credentials.store(self.implements)['token']=token


    ##
    # Auth Main methods
    @engine
    def authorize(self, credentials, request, env, callback):
        response = None
        try:
            self.sign(credentials, request, env)
        except AuthError:
            response = yield Task(self._authenticate, credentials)
            self._update_credentials(credentials, response)
        # fetch token or response from server
        response = response or credentials.store(self.implements)['token']
        callback(response)
        
    def authorize_sync(self, credentials, request, env):
        try:
            self.sign(credentials, request, env)
        except AuthError:
            # fetch token
            token = self._authenticate_sync(credentials)
            self._update_credentials(credentials, token)

