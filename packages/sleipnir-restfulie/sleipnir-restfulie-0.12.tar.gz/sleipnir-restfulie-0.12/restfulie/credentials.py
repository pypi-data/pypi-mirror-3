#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
credentials
"""

from __future__ import absolute_import

__author__   = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE.restfulie for details"

# Import here any required modules.
from itertools import ifilter

__all__ = ['Credentials']


class Credentials(object):
    """
    Base class to define required credentials to use a remote
    service
    """
    _mechanisms = {}

    def __init__(self):
        self._api_key         = None
        self._consumer_key    = None
        self._consumer_secret = None
        self._token_key       = None
        self._token_secret    = None
        self._callback        = None

    def store(self, mechanism):
        """A store for auth mechanism data"""
        return self._mechanisms.setdefault(mechanism, {})

    def to_list(self, *args):
        """Get a list of properties collected in args"""
        return [getattr(self, arg) for arg in args]

    def to_dict(self, *args):
        """Get a dict of properties collected from args"""
        dct = {}
        for arg in ifilter(lambda x: hasattr(self, x), args):
            dct[arg] = getattr(self, arg)
        return dct

    @property
    def api_key(self):
        """Get API key required to use remote service"""
        return self._api_key or ""

    @api_key.setter
    def api_key(self, value):
        """Set API key requires to use remote service"""
        self._api_key = value

    @property
    def username(self):
        """Get username"""
        return self._token_key

    @username.setter
    def username(self, value):
        """set username"""
        self._token_key = value

    @property
    def password(self):
        """Get password"""
        return self._token_secret

    @password.setter
    def password(self, value):
        """Set password"""
        self._token_secret = value

    @property
    def consumer_key(self):
        """Get required key to authenticate (login)"""
        return self._consumer_key or ""

    @consumer_key.setter
    def consumer_key(self, value):
        """Set auth key"""
        self._consumer_key = value

    @property
    def consumer_secret(self):
        """Get password"""
        return self._consumer_secret or ""

    @consumer_secret.setter
    def consumer_secret(self, value):
        """Set password"""
        self._consumer_secret = value

    @property
    def token_key(self):
        """Get token on 2LO mechanisms"""
        return self._token_key

    @token_key.setter
    def token_key(self, value):
        """Set auth key"""
        self._token_key = value

    @property
    def token_secret(self):
        """Get tolen secret"""
        return self._token_secret

    @token_secret.setter
    def token_secret(self, value):
        """Set password"""
        self._token_secret = value

    @property
    def callback(self):
        """
        Callback to be invoked when user interaction is needed on
        handshake
        """
        return self._callback

    @callback.setter
    def callback(self, value):
        """Set callback"""
        self._callback = value

