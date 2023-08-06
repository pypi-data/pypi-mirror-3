#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
client
"""

from __future__ import absolute_import

__author__   = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE.restfulie for details"

# Import here any required modules.
from contextlib import contextmanager
from functools import wraps

__all__ = ['Client']

# local submodule requirements
from .credentials import Credentials

class Client(object):
    """Base class to implement a remote API"""

    def __init__(self):
        self._config = Credentials()

    @contextmanager
    def configure(self):
        """Get an accessor to credentials element"""
        yield self._config

    @property
    def credentials(self):
        """Get credentials element"""
        return self._config

    @property
    def write_enabled(self):
        """Check if config has valid credentials. Return false
        otherwise"""
        raise NotImplementedError


class Extend(type):
    """
    Allow Ad-hoc inheritance. See
    http://code.activestate.com/recipes/412717-extending-classes/ for
    details
    """

    #pylint: disable-msg=W0613
    def __new__(mcs, name, bases, dct):
        prev = globals()[name]
        del dct['__module__']
        del dct['__metaclass__']
        for key, value in dct.iteritems():
            if key == "__doc__":
                continue
            setattr(prev, key, value)
        return prev


def validate(table):
    """Check that required attributes are present on method invoke"""
    #pylint: disable-msg=C0111
    def wrap_f(func):
        def new_func(instance, action, args, callback=None):
            if action not in getattr(instance, table):
                raise AttributeError("Missing action '%s'" % action)
            return func(instance, action, args, callback)
        return wraps(func)(new_func)
    return wrap_f


