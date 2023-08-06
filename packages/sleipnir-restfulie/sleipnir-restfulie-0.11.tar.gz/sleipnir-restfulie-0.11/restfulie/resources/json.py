#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
json

Json converter and resource
"""

from __future__ import absolute_import

__author__ = "caelum - http://caelum.com.br"
__modified_by__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE.restfulie for details"

# Import here any required modules.
from itertools import ifilter
import simplejson as json

__all__ = []

# Project requirements

# local submodule requirements
from ..resource import Resource
from ..links import Links, Link
from ..converters import ConverterMixin


class JsonResource(Resource):
    """This resource is returned when a JSON is unmarshalled"""

    def __init__(self, data):
        """JsonResource attributes can be accessed with 'dot'"""
        super(JsonResource, self).__init__()
        assert isinstance(data, dict)
        for key, value in ifilter(lambda x: x[0] != 'link', data.iteritems()):
            if isinstance(value, (list, tuple,)):
                setattr(self, key, [self.parse(element) for element in value])
            else:
                setattr(self, key, self.parse(value))

        # store dict
        self._dict  = data
        self._links = None

    def __len__(self):
        return len(self._dict)

    def _find_dicts_in_dict(self, data):
        """Get all dictionaries on a structure and returns a list of it"""
        dicts = []
        if isinstance(data, dict):
            dicts.append(data)
            for value in data.itervalues():
                dicts.extend(self._find_dicts_in_dict(value))
        return dicts

    def _parse_links(self, data):
        """Find links on JSON dictionary"""
        retval, dct_filter = [], lambda x: '_links' in x
        for dct in ifilter(dct_filter, self._find_dicts_in_dict(data)):
            #Set a json as the default content-type for this link if
            #no one has been set by the server
            #pylint:disable-msg=W0106
            for key, link in dct['_links'].iteritems():
                link = dict(link)
                link.setdefault('rel', key)
                link.setdefault('type', 'application/json')
                retval.append(Link(**link))
        return retval

    def link(self, rel):
        return self.links().get(rel)

    def links(self):
        if not self._links:
            self._links = Links(self._parse_links(self._dict))
        return self._links

    def error(self):
        if not self._error:
            self._error = self._dict.get('_error')
        return self._error
        
    @classmethod
    def parse(cls, value):
        """Pyhtonize a Json value"""
        return cls(value) if isinstance(value, dict) else value

class JsonConverter(ConverterMixin):
    """Converts objects from and to JSON"""

    types = ['application/json', 'text/json', 'json']

    def __init__(self):
        ConverterMixin.__init__(self)

    #pylint: disable-msg=R0201
    def marshal(self, content):
        """Produces a JSON representation of the given content"""
        return json.dumps(content)

    #pylint: disable-msg=R0201
    def unmarshal(self, json_content):
        """Produces an object for a given JSON content"""
        return JsonResource(json.loads(json_content.read()))


