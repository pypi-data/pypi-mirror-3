# -*- coding: utf-8 -*-

import cgi
import urllib

import intessa.vendor.multidict as multidict

from intessa.conneg.codec_base import Codec
from intessa.conneg.content_type import ContentType


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
        encoder = lambda s: s.encode(encoding, errors)
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
        ``intessa.vendor.multidict.MultiDict`` with bytestrings:

            >>> form_type = ContentType('application/x-www-form-urlencoded')
            >>> SimpleFormCodec.decode(form_type, 'a=b&c=d')
            MultiDict([('a', 'b'), ('c', 'd')])

        If a charset is given, the input is decoded using it, returning a
        ``UnicodeMultiDict`` instead:

            >>> utf8_form_type = ContentType(
            ...     'application/x-www-form-urlencoded; charset=utf-8')
            >>> SimpleFormCodec.decode(utf8_form_type, 'h%C3%A9llo=w%C3%B8rld')
            UnicodeMultiDict([(u'h\xe9llo', u'w\xf8rld')])

        The ``intessa.vendor.multidict.MultiDict`` class was vendorized from
        WebOb, as the original bytes/unicode split has been removed from WebOb
        1.2.
        """

        pairs = cgi.parse_qsl(bytes)
        multi_dict = multidict.MultiDict(pairs)
        if 'charset' in c_type.params:
            encoding = c_type.params['charset']
            multi_dict = multidict.UnicodeMultiDict(multi_dict,
                                                    encoding=encoding,
                                                    decode_keys=True)
        return multi_dict
