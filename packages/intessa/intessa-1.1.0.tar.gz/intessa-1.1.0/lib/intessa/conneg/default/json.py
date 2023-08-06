import simplejson

from intessa.conneg.codec_base import Codec


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
