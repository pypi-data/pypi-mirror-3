# coding: utf8
"""
    weasyprint.utils
    ----------------

    Various utility functions and classes.

    :copyright: Copyright 2011-2012 Simon Sapin and contributors, see AUTHORS.
    :license: BSD, see LICENSE for details.

"""

from __future__ import division, unicode_literals

import io
import re
import base64
import os.path

from . import VERSION_STRING
from .logger import LOGGER
from .compat import (
    urljoin, urlsplit, quote, unquote, unquote_to_bytes, urlopen_contenttype,
    Request, parse_email, pathname2url, unicode)


# Both are needed in Python 3 as the re module does not like to mix
UNICODE_SCHEME_RE = re.compile('^([a-z][a-z0-1.+-]*):', re.I)
BYTES_SCHEME_RE = re.compile(b'^([a-z][a-z0-1.+-]*):', re.I)

OPENER_BY_SCHEME = {}

def register_opener(scheme):
    """Register globally an opener function for a given URI scheme.

    Expected usage::

        from weasyprint.urls import register_opener
        @register_opener('foo')
        def git_urlopen(url):
            url = urlparse.urlsplit(url)
            assert url.scheme == 'foo'
            # ...
            return fileobj, mimetype, charset

    """
    def decorator(function):
        OPENER_BY_SCHEME[scheme] = function
        return function
    return decorator


def iri_to_uri(url):
    """Turn an IRI that can contain any Unicode character into an ASII-only
    URI that conforms to RFC 3986.
    """
    # Use UTF-8 as per RFC 3987 (IRI)
    url = url.encode('utf8')
    # This is a full URI, not just a component. Only %-encode characters
    # that are not allowed at all in URIs. Everthing else is "safe":
    # * Reserved characters: /:?#[]@!$&'()*+,;=
    # * Unreserved characters: ASCII letters, digits and -._~
    #   Of these, only '~' is not in urllib’s "always safe" list.
    # * '%' to avoid double-encoding
    return quote(url, safe=b"/:?#[]@!$&'()*+,;=~%")


def path2url(path):
    """Return file URL of `path`"""
    path = os.path.abspath(path)
    if isinstance(path, unicode):
        path = path.encode('utf8')
    # TODO: should this be 'file://' ? Maybe only on Unix?
    return 'file:' + pathname2url(path)


def url_is_absolute(url):
    return bool(
        (UNICODE_SCHEME_RE if isinstance(url, unicode) else BYTES_SCHEME_RE)
        .match(url))


def get_url_attribute(element, attr_name):
    """Get the URI corresponding to the ``attr_name`` attribute.

    Return ``None`` if:

    * the attribute is empty or missing or,
    * the value is a relative URI but the document has no base URI.

    Otherwise, return an absolute URI.

    """
    attr_value = element.get(attr_name, '').strip()
    if attr_value:
        # TODO: support the <base> HTML element, but do not use
        # lxml.html.HtmlElement.make_links_absolute() that changes
        # the tree for content: attr(href)
        if url_is_absolute(attr_value):
            return attr_value
        elif element.base_url:
            return urljoin(element.base_url, attr_value)
        else:
            LOGGER.warn(
                'Relative URI reference without a base URI: '
                '<%s %s="%s"> at line %d',
                element.tag, attr_name, attr_value, element.sourceline)


def get_link_attribute(element, attr_name):
    """Return ('external', absolute_uri) or
    ('internal', unquoted_fragment_id) or None.

    """
    attr_value = element.get(attr_name, '').strip()
    if attr_value.startswith('#'):
        # Do not require a base_url when the value is just a fragment.
        return 'internal', unquote(attr_value[1:])
    else:
        uri = get_url_attribute(element, attr_name)
        if uri is not None:
            document_uri = urlsplit(element.base_url or '')
            parsed = urlsplit(uri)
            # Compare with fragments removed
            if parsed[:-1] == document_uri[:-1]:
                return 'internal', unquote(parsed.fragment)
            else:
                return 'external', uri


def ensure_url(string):
    """Get a ``scheme://path`` URL from ``string``.

    If ``string`` looks like an URL, return it unchanged. Otherwise assume a
    filename and convert it to a ``file://`` URL.

    """
    if url_is_absolute(string):
        return string
    else:
        return path2url(string.encode('utf8'))


def decode_base64(data):
    """Decode base64, padding being optional.

    "From a theoretical point of view, the padding character is not needed,
     since the number of missing bytes can be calculated from the number
     of Base64 digits."

    https://en.wikipedia.org/wiki/Base64#Padding

    :param data: Base64 data as an ASCII byte string
    :returns: The decoded byte string.

    """
    missing_padding = 4 - len(data) % 4
    if missing_padding:
        data += b'='* missing_padding
    return base64.decodestring(data)


@register_opener('data')
def open_data_url(url):
    """Decode URLs with the 'data' scheme. urllib can handle them
    in Python 2, but that is broken in Python 3.

    Inspired from Python 2.7.2’s urllib.py.

    """
    # syntax of data URLs:
    # dataurl   := "data:" [ mediatype ] [ ";base64" ] "," data
    # mediatype := [ type "/" subtype ] *( ";" parameter )
    # data      := *urlchar
    # parameter := attribute "=" value
    try:
        header, data = url.split(',', 1)
    except ValueError:
        raise IOError('bad data URL')
    header = header[5:]  # len('data:') == 5
    if header:
        semi = header.rfind(';')
        if semi >= 0 and '=' not in header[semi:]:
            content_type = header[:semi]
            encoding = header[semi+1:]
        else:
            content_type = header
            encoding = ''
        message = parse_email('Content-type: ' + content_type)
        mime_type = message.get_content_type()
        charset = message.get_content_charset()
    else:
        mime_type = 'text/plain'
        charset = 'US-ASCII'
        encoding = ''

    data = unquote_to_bytes(data)
    if encoding == 'base64':
        data = decode_base64(data)

    return io.BytesIO(data), mime_type, charset


def urlopen(url):
    """Fetch an URL and return ``(file_like, mime_type, charset)``.

    It is the caller’s responsability to call ``file_like.close()``.
    """
    match = UNICODE_SCHEME_RE.match(url)
    if not match:
        raise ValueError('Not an absolute URI: %r' % url)
    opener = OPENER_BY_SCHEME.get(match.group(1))
    if opener:
        return opener(url)
    else:
        url = iri_to_uri(url)
        return urlopen_contenttype(Request(url,
            headers={'User-Agent': VERSION_STRING}))
