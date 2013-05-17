# coding: utf8
"""
    weasyprint.compat
    -----------------

    Workarounds for compatibility with Python 2 and 3 in the same code base.

    :copyright: Copyright 2011-2013 Simon Sapin and contributors, see AUTHORS.
    :license: BSD, see LICENSE for details.

"""

from __future__ import division, unicode_literals

import sys
import email
import gzip


__all__ = ['ClosingGzipFile', 'Request', 'base64_decode', 'base64_encode',
           'basestring', 'ints_from_bytes', 'iteritems', 'izip', 'parse_email',
           'parse_qs', 'pathname2url', 'quote', 'unicode', 'unquote',
           'unquote_to_bytes', 'urlencode', 'urljoin', 'urlopen',
           'urlopen_contenttype', 'urlparse_uses_relative', 'urlsplit',
           'xrange']


if sys.version_info[0] >= 3:
    # Python 3
    from urllib.parse import (
        urljoin, urlsplit, quote, unquote, unquote_to_bytes, parse_qs,
        urlencode, uses_relative as urlparse_uses_relative)
    from urllib.request import urlopen, Request, pathname2url
    from array import array
    from io import StringIO
    from base64 import (decodebytes as base64_decode,
                        encodebytes as base64_encode)

    unicode = str
    basestring = str
    xrange = range
    iteritems = dict.items
    izip = zip

    def urlopen_contenttype(url):
        """Return (file_obj, mime_type, encoding)"""
        result = urlopen(url)
        info = result.info()
        mime_type = info.get_content_type()
        charset = info.get_param('charset')
        return result, mime_type, charset

    def parse_email(data):
        if isinstance(data, bytes):
            data = data.decode('utf8')
        return email.message_from_string(data)

    def ints_from_bytes(byte_string):
        """Return a list of ints from a byte string"""
        return list(byte_string)


else:
    # Python 2
    from urlparse import (urljoin, urlsplit, parse_qs,
                          uses_relative as urlparse_uses_relative)
    from urllib2 import urlopen, Request
    from urllib import pathname2url, quote, unquote, urlencode
    from array import array as _array
    from itertools import izip, imap
    from base64 import (decodestring as base64_decode,
                        encodestring as base64_encode)

    try:
        from cStringIO import StringIO
    except ImportError:
        from StringIO import StringIO

    unicode = unicode
    basestring = basestring
    xrange = xrange
    iteritems = dict.iteritems

    def array(typecode, initializer):
        return _array(typecode.encode('ascii'), initializer)

    def urlopen_contenttype(url):
        """Return (file_obj, mime_type, encoding)"""
        result = urlopen(url)
        info = result.info()
        mime_type = info.gettype()
        charset = info.getparam('charset')
        return result, mime_type, charset

    def unquote_to_bytes(data):
        if isinstance(data, unicode):
            data = data.encode('ascii')
        return unquote(data)

    def parse_email(data):
        if isinstance(data, unicode):
            data = data.encode('utf8')
        return email.message_from_string(data)

    def ints_from_bytes(byte_string):
        """Return a list of ints from a byte string"""
        return imap(ord, byte_string)


if sys.version_info[0] < 3 or \
    sys.version_info[0] == 3 and sys.version_info[1] < 2:

    # GzipFile cannot be used for streaming before Python 3.2
    # http://bugs.python.org/issue11608
    class ClosingGzipFile(gzip.GzipFile):
        def __init__(self, filename=None, mode=None, compresslevel=None,
                fileobj=None, mtime=None, *args, **kwargs):
            if fileobj:
                fake_fileobj = StringIO(fileobj.read())
                fileobj.close()
                fileobj = fake_fileobj
            known_kwargs = {
                'filename': filename, 'mode': mode,
                'compresslevel': compresslevel, 'fileobj': fileobj,
                'mtime': mtime}
            kwargs.update((k, v) for k, v in known_kwargs.items() if v is not None)
            super(ClosingGzipFile, self).__init__(*args, **kwargs)

else:

    class ClosingGzipFile(gzip.GzipFile):
        def __init__(self, filename=None, mode=None, compresslevel=None,
                fileobj=None, mtime=None, *args, **kwargs):
            self.my_fileobj = fileobj
            known_kwargs = {
                'filename': filename, 'mode': mode,
                'compresslevel': compresslevel, 'fileobj': fileobj,
                'mtime': mtime}
            kwargs.update((k, v) for k, v in known_kwargs.items() if v is not None)
            super(ClosingGzipFile, self).__init__(*args, **kwargs)

        def close(self):
            super(ClosingGzipFile, self).close()
            if self.my_fileobj:
                self.my_fileobj.close()
