
#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
API
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE.restfulie for details"

__all__ = ['API']

from restfulie.api  import BaseAPI
from restfulie.auth import OAuthMixin


#pylint: disable-msg=W0223         
class TwitterAuth(OAuthMixin):
    """ oauth method """
    
    implements = "sleipnir"

    @property
    def request_url(self):
        #return "https://api.twitter.com/oauth/request_token"
        return "http://127.0.0.1:8888/oauth/request_token"

    @property
    def authorize_url(self):
        #return "https://api.twitter.com/oauth/authorize"        
        return "http://127.0.0.1:8888/oauth/authorize"

    @property
    def access_url(self):
        return "http://127.0.0.1:8888/oauth/access_token"



class API(BaseAPI):
    """Extend BaseAPI class with custom methods"""

    API_BASE = "http://127.0.0.1:8000/1"
    #api.tweeter.com/1"
