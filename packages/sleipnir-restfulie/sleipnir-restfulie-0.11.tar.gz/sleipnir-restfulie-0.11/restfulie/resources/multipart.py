#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
multipart

multipart marshaller
"""

from __future__ import absolute_import

__author__ = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE.restfulie for details"

# Import here any required modules.
import hashlib
import cStringIO

__all__ = []

# Project requirements

# local submodule requirements
from ..converters import ConverterMixin


class Part(object):

    EOL="\r\n".encode('latin-1')

    def __init__(self, boundary, name, contents):
        self.boundary = boundary
        self.name     = name
        self.contents = contents

    def write(self, output):
        raise NotImplementedError

        
class ParamPart(Part):
    def write(self, output):
        output.writelines(("--", self.boundary, self.EOL))
        output.writelines(('Content-Disposition: form-data; name="', self.name, '"', self.EOL))
        output.writelines((self.EOL, self.contents, self.EOL))


class FilePart(Part):
    def write(self, output, algorithm=None):
        # write header
        output.writelines(("--", self.boundary, self.EOL))
        output.writelines(('Content-Disposition: form-data; name="', self.name, '"; filename="', self.name, '"' ,self.EOL))
        output.writelines(('Content-Type: application/octet-stream', self.EOL))
        output.writelines(('Content-Transfer-Encoding: binary', self.EOL))
        output.write(self.EOL)

        # write file contents
        digest = algorithm() or None
        for chunk in iter(lambda: self.contents.read(8192), b''):
            output.write(chunk)
            digest and digest.update(chunk)

        # end header
        output.write(self.EOL)
        return digest

    
class MultiPartConverter(ConverterMixin):
    """Multipart form encoder"""

    types = ['multipart/form-data']


    def __init__(self, boundary=None):
        # Only create a boundary property if boundary is defined
        if boundary is not None:
            self.boundary = boundary[0].split('=')[1]
        ConverterMixin.__init__(self)


    def marshal(self, content):
        """Produces a well formated multipart"""

        assert isinstance(content, dict)
        assert self.boundary

        # ouput buffer
        output = cStringIO.StringIO()

        # parse params
        for key, value in content.iteritems():
            # write header
            if hasattr(value, "writelines"):
                flpart = FilePart(self.boundary, key, value)
                digest = flpart.write(output, algorithm=hashlib.sha1)
                
                # prepare to write digest param
                key   = key + "_sha1sum"
                value = digest.hexdigest()

            # it's a param or we are writing sum
            param = ParamPart(self.boundary, key, value)
            param.write(output)

        output.writelines(("--", self.boundary, "--", Part.EOL))
        retval = output.getvalue()
        
        # free buffer and return contents
        output.close()
        return retval

