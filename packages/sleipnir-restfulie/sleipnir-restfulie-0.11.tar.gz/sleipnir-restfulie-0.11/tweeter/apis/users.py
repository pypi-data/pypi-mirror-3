
#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
users
"""

from __future__ import absolute_import

__author__   = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE.restfulie for details"

# Import required modules
from restfulie.client import Extend, validate

# local submodule requirements
from ..api import API


class Client(object):
    """This class will extend main Client object"""

    __metaclass__ = Extend
  
    USERS_API = {
      "show" : {
        "endpoint" : '/users/show/%(username)s',
        "method"   : 'get',
        "required" : ['username'],
        },

      "show_authorized" : {
        "endpoint" : '/users/show/%(username)s',
        "method"   : 'get',
        "auth"     : "sleipnir",
        "required" : ['username'],
        },
        
        "update": {
            "endpoint" : '/users/show/%(username)s',
            "method"   : 'post',
            "auth"     : "sleipnir",
            "required" : ['username'],
        }
    }
    
    @validate('USERS_API')
    def users(self, action, args, callback):
        return API.invoke(self, self.USERS_API[action], args, callback)
    
