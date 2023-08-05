# -*- coding: utf-8 -*-

from intessa.conneg.codec_base import Codec
from intessa.conneg.content_type import ContentType


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
