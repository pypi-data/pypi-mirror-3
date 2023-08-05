# -*- coding: utf-8 -*-

"""Houses the default global codec register and codecs."""

import cgi
import urllib

import lxml.etree
import lxml.objectify
import simplejson
import webob.multidict

from intessa.conneg.codec_base import CodecRegister, Codec
from intessa.conneg.content_type import ContentType


DEFAULT_REGISTER = CodecRegister()


class TextCodec(Codec):

    """Default text codec."""

    def encode(media_type, string, encoding='utf-8', errors='strict'):

        ur"""
        Encode a unicode string as a bytestring using an encoding.

        :param encoding:
            The encoding to use (default: ``'utf-8'``).
        :param errors:
            The strategy for handling encoding errors (default: ``'strict'``).
            See the documentation on the built-in ``unicode.encode()`` for more
            information about this option.

            >>> TextCodec.encode('text/plain', u"Héllo Wörld")
            (ContentType('text/plain; charset=utf-8'), 'H\xc3\xa9llo W\xc3\xb6rld')
            >>> TextCodec.encode('text/plain', u"Héllo Wörld", encoding='latin1')
            (ContentType('text/plain; charset=latin1'), 'H\xe9llo W\xf6rld')
        """

        encoded = string.encode(encoding, errors)
        c_type = ContentType('%s; charset=%s' % (media_type, encoding))
        return (c_type, encoded)

    def decode(c_type, bytes):

        ur"""
        Decode a bytestring to unicode, using the content type's charset.

            >>> TextCodec.decode(ContentType('text/plain; charset=utf-8'),
            ...                  'H\xc3\xa9llo W\xc3\xb6rld')
            u'H\xe9llo W\xf6rld'
            >>> TextCodec.decode(ContentType('text/plain; charset=latin1'),
            ...                              'H\xe9llo W\xf6rld')
            u'H\xe9llo W\xf6rld'

        If no charset is present, this method assumes the input is UTF-8::

            >>> TextCodec.decode(ContentType('text/plain'),
            ...                  'H\xc3\xa9llo W\xc3\xb6rld')
            u'H\xe9llo W\xf6rld'

        The decoder always uses 'strict' error handling::

            >>> TextCodec.decode(ContentType('text/plain; charset=us-ascii'), # doctest: +ELLIPSIS
            ...                  'H\xc3\xa9llo W\xc3\xb6rld')
            Traceback (most recent call last):
            ...
            UnicodeDecodeError: 'ascii' codec can't decode byte 0xc3 in position 1: ordinal not in range(128)
        """

        return bytes.decode(c_type.params.get('charset', 'utf-8'))

DEFAULT_REGISTER['text/plain'] = TextCodec
DEFAULT_REGISTER.alias('text', 'text/plain')


class SimpleFormCodec(Codec):

    """Codec for simple application/x-www-form-urlencoded HTML forms."""

    def encode(media_type, obj, encoding='utf-8', errors='strict'):

        u"""
        Encode a simple dictionary of strings to an HTML form.

        :param encoding:
            The encoding to use (default: ``'utf-8'``).
        :param errors:
            The strategy for handling encoding errors (default: ``'strict'``).
            See the documentation on the built-in ``unicode.encode()`` for more
            information about this option.

        The simplest case, dictionaries of bytestrings, works:

            >>> SimpleFormCodec.encode('application/x-www-form-urlencoded', # doctest: +ELLIPSIS
            ...     {'a': 'b', 'c': 'd'})
            (ContentType(...), 'a=b&c=d')

        You can also pass in lists of key, value pairs:

            >>> SimpleFormCodec.encode('application/x-www-form-urlencoded', # doctest: +ELLIPSIS
            ...     [('a', 'b'), ('c', 'd')])
            (ContentType(...), 'a=b&c=d')

        Unicode strings will be encoded according to the ``encoding`` and
        ``errors`` parameters:

            >>> SimpleFormCodec.encode('application/x-www-form-urlencoded', # doctest: +ELLIPSIS
            ...     [(u'héllo', u'wørld')])
            (ContentType('...; charset=utf-8'), 'h%C3%A9llo=w%C3%B8rld')
        """

        c_type = ContentType('%s; charset=%s' % (media_type, encoding))

        if hasattr(obj, 'iteritems'):
            pairs = obj.iteritems()
        else:
            pairs = iter(obj)
        encoded_pairs = list(SimpleFormCodec.encode_pairs(pairs, encoding=encoding, errors=errors))
        data = urllib.urlencode(encoded_pairs)

        return (c_type, data)

    @staticmethod
    def encode_pairs(pairs, encoding='utf-8', errors='strict'):
        encoder = lambda s: s.encode(encoding, errors=errors)
        for key, value in pairs:
            if isinstance(key, unicode):
                key = encoder(key)
            if isinstance(value, unicode):
                value = encoder(value)
            yield (key, value)

    def decode(c_type, bytes):

        r"""
        Decode the encoded form, returning a ``MultiDict``.

        For content types without a ``charset``, returns an instance of
        ``webob.multidict.MultiDict`` with bytestrings:

            >>> form_type = ContentType('application/x-www-form-urlencoded')
            >>> SimpleFormCodec.decode(form_type, 'a=b&c=d')
            MultiDict([('a', 'b'), ('c', 'd')])

        If a charset is given, the input is decoded using it, returning a
        ``UnicodeMultiDict`` instead:

            >>> utf8_form_type = ContentType(
            ...     'application/x-www-form-urlencoded; charset=utf-8')
            >>> SimpleFormCodec.decode(utf8_form_type, 'h%C3%A9llo=w%C3%B8rld')
            UnicodeMultiDict([(u'h\xe9llo', u'w\xf8rld')])
        """

        pairs = cgi.parse_qsl(bytes)
        multi_dict = webob.multidict.MultiDict(pairs)
        if 'charset' in c_type.params:
            encoding = c_type.params['charset']
            multi_dict = webob.multidict.UnicodeMultiDict(multi_dict,
                                                          encoding=encoding,
                                                          decode_keys=True)
        return multi_dict

DEFAULT_REGISTER['application/x-www-form-urlencoded'] = SimpleFormCodec
DEFAULT_REGISTER.alias('form', 'application/x-www-form-urlencoded')


class JSONCodec(Codec):

    """Default JSON codec, powered by simplejson."""

    def encode(media_type, obj, **params):

        r"""
        Encode an object as JSON using ``simplejson.dumps()``.

        Additional parameters will be passed to ``simplejson.dumps()`` as-is.

            >>> JSONCodec.encode('application/json', {"a": 1})
            ('application/json', '{"a": 1}')
            >>> JSONCodec.encode('application/json', {"a": 1}, indent=True)
            ('application/json', '{\n "a": 1\n}')
        """

        return (media_type, simplejson.dumps(obj, **params))

    def decode(content_type, bytes):

        """
        Decode a JSON bytestring using ``simplejson.loads()``.

            >>> JSONCodec.decode('application/json', '{"a": 1}')
            {'a': 1}
        """

        return simplejson.loads(bytes)

DEFAULT_REGISTER['application/json'] = JSONCodec
DEFAULT_REGISTER['text/javascript'] = JSONCodec
DEFAULT_REGISTER.alias('json', 'application/json')
DEFAULT_REGISTER.alias('json-js', 'text/javascript')


class XMLCodec(Codec):

    """Default XML codec, using ``lxml.objectify``."""

    def encode(media_type, etree, **params):

        ur"""
        Encode an lxml ``ElementTree`` using ``lxml.etree.tostring()``.

        By default, the output will include an XML prolog, and will be
        utf-8-encoded. This can be overridden by passing ``xml_declaration``
        (``True`` or ``False``, default ``True``) and ``encoding`` (default
        ``'utf-8'``) keywords.

        See http://lxml.de/api/lxml.etree-module.html#tostring for a detailed
        overview of available options.

            >>> tree = lxml.etree.fromstring('<obj><attr>value</attr></obj>')
            >>> tree.find('attr').text = u"vålúè"
            >>> XMLCodec.encode('application/xml', tree)
            ('application/xml', "<?xml version='1.0' encoding='utf-8'?>\n<obj><attr>v\xc3\xa5l\xc3\xba\xc3\xa8</attr></obj>")
        """

        params.setdefault('xml_declaration', True)
        params.setdefault('with_tail', False)
        if params['xml_declaration']:
            params.setdefault('encoding', 'utf-8')

        return (media_type, lxml.etree.tostring(etree, **params))

    def decode(content_type, bytes):

        """
        Decode an XML bytestring to a Python object, using ``lxml.objectify``.

        For more information on these objects, see
        http://lxml.de/objectify.html.

            >>> doc = XMLCodec.decode('application/xml', '<obj><attr>value</attr></obj>')
            >>> doc # doctest: +ELLIPSIS
            <Element obj at 0x...>
            >>> doc.tag
            'obj'
            >>> doc.attr
            'value'
        """

        return lxml.objectify.fromstring(bytes)

DEFAULT_REGISTER['application/xml'] = XMLCodec
DEFAULT_REGISTER.alias('xml', 'application/xml')
