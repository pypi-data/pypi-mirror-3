##############################################################################
#
# Copyright (c) 2008 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id:$
"""
__docformat__ = "reStructuredText"

import re
import os
import urllib
import rfc822
import tempfile
import cStringIO

import zope.interface

from p01.cgi import interfaces


#TODO: should this be a zope.conf property?
maxlen = 0

#TODO: maybe move all those methods to a class?

OVERSIZE_FIELD_CONTENT = 1000


class SimpleField:
    """Simple key value pair field."""

    zope.interface.implements(interfaces.ISimpleField)

    def __init__(self, name, value):
        """Constructor from field name and value."""
        self.name = name
        self.value = value

    def __repr__(self):
        return "<%s, %r = %r>" % (self.__class__.__name__, self.name,
            self.value)


def parseFormData(method, inputStream=None, headers=None, boundary="",
    environ=os.environ, tmpFileFactory=None, tmpFileFactoryArguments=None):
    """Parse form data and return a list of fields."""
    # GET or HEAD request
    if method == 'GET' or method == 'HEAD':
        qs = environ.get('QUERY_STRING', None)
        if qs is not None:
            # parse query string and return a simple field storage
            return [SimpleField(key, value) for key, value
                    in parseQueryString(qs)]
        return None

    # POST request -- be specific, not that we catch unknown methods
    if method == 'POST':
        content_type = environ.get('CONTENT_TYPE')
        if content_type:
            if content_type.startswith('multipart/'):
                fieldStorage = parseMultiParts(inputStream, headers, boundary,
                    environ, tmpFileFactory, tmpFileFactoryArguments)
                return fieldStorage.list
            if content_type.startswith('application/x-www-form-urlencoded'):
                return parseUrlEncoded(inputStream, headers, environ)

    #all other types get None
    return None


def parseUrlEncoded(inputStream=None, headers=None, environ=os.environ):
    """Parse x-www-form-urlencoded form data and return a list of fields.
    No subparts or whatever supported"""

    # setup header if not given
    if headers is None:
        headers = {}

        if 'CONTENT_LENGTH' in environ:
            headers['content-length'] = environ['CONTENT_LENGTH']
        elif 'HTTP_CONTENT_LENGTH' in environ:
            headers['content-length'] = environ['HTTP_CONTENT_LENGTH']

    clen = -1
    if 'content-length' in headers:
        try:
            clen = int(headers['content-length'])
        except ValueError:
            pass
        if maxlen and clen > maxlen:
            # TODO: implement maxlen support via zope.conf or os.environ?
            raise ValueError, 'Maximum content length exceeded'

    qs = inputStream.read(clen)
    if qs is not None:
        # parse query string and return a simple field storage
        return [SimpleField(key, value) for key, value
                in parseQueryString(qs)]

    return None


def parseMultiParts(inputStream=None, headers=None, boundary="",
    environ=os.environ, tmpFileFactory=None, tmpFileFactoryArguments=None):
    """Parse multipart form data and return a list of fields.
    Or called for a contained part (where content-disposition is ``form-data``
    Or called for a separator part that get thrown away"""

    #TODO: maybe separate the above 3 functions into 3 different methods
    #      that could ensure more robust content checking

    fieldStorage = MultiPartField(inputStream, boundary, tmpFileFactory,
        tmpFileFactoryArguments)

    # setup header if not given
    if headers is None:
        headers = {}

        headers['content-type'] = environ.get('CONTENT_TYPE', 'text/plain')

        if 'CONTENT_LENGTH' in environ:
            headers['content-length'] = environ['CONTENT_LENGTH']
        elif 'HTTP_CONTENT_LENGTH' in environ:
            headers['content-length'] = environ['HTTP_CONTENT_LENGTH']

    fieldStorage.headers = headers

    # Process content-disposition header
    cdisp, pdict = "", {}
    if 'content-disposition' in fieldStorage.headers:
        cdisp, pdict = parseHeader(fieldStorage.headers['content-disposition'])
    fieldStorage.disposition = cdisp
    fieldStorage.disposition_options = pdict

    if 'name' in pdict:
        fieldStorage.name = pdict['name']

    if 'filename' in pdict:
        fieldStorage.filename = pdict['filename']

    # Process content-type header
    if 'content-type' in fieldStorage.headers:
        ctype, pdict = parseHeader(fieldStorage.headers['content-type'])
    else:
        ctype, pdict = "text/plain", {}

    fieldStorage.type = ctype
    fieldStorage.type_options = pdict
    fieldStorage.innerboundary = ""
    if 'boundary' in pdict:
        fieldStorage.innerboundary = pdict['boundary']
    clen = -1
    if 'content-length' in fieldStorage.headers:
        try:
            clen = int(fieldStorage.headers['content-length'])
        except ValueError:
            pass
        if maxlen and clen > maxlen:
            # TODO: implement maxlen support via zope.conf or os.environ?
            raise ValueError, 'Maximum content length exceeded'
    fieldStorage.length = clen

    if ctype.startswith('multipart/'):
        fieldStorage.readMulti(environ)
    else:
        fieldStorage.readSingle()

    return fieldStorage


def validBoundary(s):
    return re.match("^[ -~]{0,200}[!-~]$", s)


def parseHeader(line):
    """Returns the main content-type and a dictionary of options."""
    plist = [x.strip() for x in line.split(';')]
    key = plist.pop(0).lower()
    pdict = {}
    for p in plist:
        i = p.find('=')
        if i >= 0:
            name = p[:i].strip().lower()
            value = p[i+1:].strip()
            if len(value) >= 2 and value[0] == value[-1] == '"':
                value = value[1:-1]
                value = value.replace('\\\\', '\\').replace('\\"', '"')
            pdict[name] = value
    return key, pdict


def parseQueryString(qs):
    """Parse a URL-encoded query string into a list of key, value pair."""
    pairs = [s2 for s1 in qs.split('&') for s2 in s1.split(';')]
    r = []
    for kv in pairs:
        if not kv:
            continue
        nv = kv.split('=', 1)
        if len(nv) != 2:
            # ensure an empty string as value for a given key
            nv.append('')
        if len(nv[1]):
            name = urllib.unquote(nv[0].replace('+', ' '))
            value = urllib.unquote(nv[1].replace('+', ' '))
            r.append((name, value))

    return r


class MultiPartField:
    """Store a sequence of fields, reading multipart/form-data."""

    zope.interface.implements(interfaces.IMultiPartField)

    headers = None
    disposition = None
    disposition_options = None
    type = None
    type_options = None

    def __init__(self, inputStream=None, boundary="", tmpFileFactory=None,
        tmpFileFactoryArguments=None):
        """MultiPartField used for multipart content."""
        self.inputStream = inputStream
        self.outerboundary = boundary
        self.innerboundary = ""
        self.bufsize = 8*1024
        self.length = -1
        self.done = 0
        self.name = None
        self.filename = None
        self.list = None
        self.file = None
        if tmpFileFactory is None:
            self.tmpFileFactory = tempfile.TemporaryFile
        else:
            self.tmpFileFactory = tmpFileFactory
        self.tmpFileFactoryArguments = tmpFileFactoryArguments

    @property
    def value(self):
        if self.file and self.filename is None:
            # this will only return the file data as value if the filename is
            # not None. A real file upload value must get accessed via self.file
            # because it returns None as value.
            self.file.seek(0)
            value = self.file.read()
            self.file.seek(0)
            return value
        elif self.list is not None:
            return self.list
        return None

    def addPart(self, part):
        self.list.append(part)

    def readMulti(self, environ):
        """Read a part that is itself multipart."""
        ib = self.innerboundary
        if not validBoundary(ib):
            raise ValueError, 'Invalid boundary in multipart form: %r' % (ib,)
        self.list = []
        # consume first part
        part = parseMultiParts(self.inputStream, {}, ib, environ,
            self.tmpFileFactory, self.tmpFileFactoryArguments)
        # and throw it away
        while not part.done:
            headers = rfc822.Message(self.inputStream)
            part = parseMultiParts(self.inputStream, headers, ib, environ,
                self.tmpFileFactory, self.tmpFileFactoryArguments)
            self.addPart(part)
        self.skipLines()

    def readSingle(self):
        """Read an atomic part."""
        if self.length >= 0:
            self.readBinary()
            self.skipLines()
        else:
            self.readLines()
        self.file.seek(0)

    def readBinary(self):
        """Read binary data."""
        self.file = self.makeTMPFile()
        todo = self.length
        if todo >= 0:
            while todo > 0:
                data = self.inputStream.read(min(todo, self.bufsize))
                if not data:
                    self.done = -1
                    break
                self.file.write(data)
                todo = todo - len(data)

    def readLines(self):
        """Read lines until EOF or outerboundary."""
        if self.filename is not None:
            # if we have a file upload (known by a filename) we use our
            # tmpFileFactory
            self.file = self.makeTMPFile()
            self.__file = None
        else:
            # if we have no fileuplaod we start with a StringIO, later we move
            # the data to a tempfile.TemporaryFile if the data will become to
            # big
            self.file = self.__file = cStringIO.StringIO()
        if self.outerboundary:
            self.readLinesToOuterboundary()
        else:
            self.readLinesToEOF()

    def __write(self, line):
        if self.__file is not None:
            if self.__file.tell() + len(line) > OVERSIZE_FIELD_CONTENT:
                # copy data to tmp file if to big
                self.file = self.makeTMPFile()
                self.file.write(self.__file.getvalue())
                self.__file = None
        self.file.write(line)

    def readLinesToEOF(self):
        """Read lines until EOF."""
        while 1:
            line = self.inputStream.readline(1<<16)
            if not line:
                self.done = -1
                break
            self.__write(line)

    def readLinesToOuterboundary(self):
        """Read lines until outerboundary."""
        next = "--" + self.outerboundary
        last = next + "--"
        delim = ""
        last_line_lfend = True
        while 1:
            line = self.inputStream.readline(1<<16)
            if not line:
                self.done = -1
                break
            if line[:2] == "--" and last_line_lfend:
                strippedline = line.strip()
                if strippedline == next:
                    break
                if strippedline == last:
                    self.done = 1
                    break
            odelim = delim
            if line[-2:] == "\r\n":
                delim = "\r\n"
                line = line[:-2]
                last_line_lfend = True
            elif line[-1] == "\n":
                delim = "\n"
                line = line[:-1]
                last_line_lfend = True
            else:
                delim = ""
                last_line_lfend = False
            self.__write(odelim + line)

    def skipLines(self):
        """Skip lines until outer boundary is defined."""
        if not self.outerboundary or self.done:
            return
        next = "--" + self.outerboundary
        last = next + "--"
        last_line_lfend = True
        while 1:
            line = self.inputStream.readline(1<<16)
            if not line:
                self.done = -1
                break
            if line[:2] == "--" and last_line_lfend:
                strippedline = line.strip()
                if strippedline == next:
                    break
                if strippedline == last:
                    self.done = 1
                    break
            last_line_lfend = line.endswith('\n')

    def makeTMPFile(self):
        if self.tmpFileFactoryArguments is not None:
            return self.tmpFileFactory(**self.tmpFileFactoryArguments)
        else:
            return self.tmpFileFactory()

    def __repr__(self):
        if self.filename:
            return "<%s, %r: %r>" % (self.__class__.__name__, self.name,
                self.filename)
        else:
            return "<%s, %r>" % (self.__class__.__name__, self.name)
