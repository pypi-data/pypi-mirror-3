from urecord import Record

from intessa.conneg.content_type import ContentType


class CodecRegister(dict):

    r"""
    A dictionary mapping media types to :class:`Codecs <Codec>`.

    Keys should be media types as bytestrings, and values should be
    :class:`Codec` subclasses (or at least match the decode/encode interface).

    As an example, start by defining a codec::

        >>> import simplejson
        >>> class JSONCodec(Codec):
        ...     def encode(media_type, obj, **params):
        ...         return (media_type, simplejson.dumps(obj, **params))
        ...     def decode(content_type, bytes):
        ...         return simplejson.loads(bytes)

    Create a register and add the codec to it::

        >>> reg = CodecRegister()
        >>> reg['application/json'] = JSONCodec
        >>> reg['application/json'] is JSONCodec
        True

    You can then encode and decode objects using the same method signatures as
    on individual codecs. The codec register will dispatch based on the media
    type provided::

        >>> reg.encode('application/json', {"a": 1})
        ('application/json', '{"a": 1}')
        >>> reg.encode('application/json', {"a": 1}, indent=True)
        ('application/json', '{\n "a": 1\n}')
        >>> reg.decode('application/json', '{"a": 1}')
        {'a': 1}

    Since full media types can be rather unwieldy, you can also register
    shorter aliases which will be resolved to their full counterparts first::

        >>> reg.alias('json', 'application/json')
        >>> reg.encode('json', {"a": 1})
        ('application/json', '{"a": 1}')

    Note that this only applies to encoding; for decoding, it's assumed that
    full content type headers will be provided. If an alias is used as the
    content type for a decode, a ``KeyError`` will be raised::

        >>> reg.decode('json', '{"a": 1}')  # doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        KeyError: 'json'
    """

    class _Alias(str):
        """Sentinel class to represent a short alias to a longer media type."""
        pass

    def alias(self, alias_name, media_type):
        self[alias_name] = self._Alias(media_type)

    def get_codec(self, media_type):

        """
        Resolve a media type or alias to a codec and media type.

            >>> reg = CodecRegister()
            >>> reg['application/json'] = 123
            >>> reg.alias('json', 'application/json')
            >>> reg.get_codec('json')
            ('application/json', 123)
            >>> reg.get_codec('application/json')
            ('application/json', 123)

        This method will even deal with multiple levels of indirection,
        considering the last name in the chain to be the full media type::

            >>> reg.alias('json2', 'json')
            >>> reg.get_codec('json2')
            ('application/json', 123)
            >>> reg.alias('json3', 'json2')
            >>> reg.get_codec('json3')
            ('application/json', 123)

        This method also takes full Content-Type headers; it will remove
        parameters before doing the lookup::

            >>> reg.get_codec('application/json; param=value')
            ('application/json', 123)
        """

        last_ref = ContentType(media_type).media_type
        codec = self[last_ref]
        while isinstance(codec, self._Alias):
            last_ref = codec
            codec = self[last_ref]
        return (last_ref, codec)

    def copy(self):
        """A ``copy()`` that will return :class:`CodecRegister` instances."""

        return type(self)(self.iteritems())

    def encode(self, media_type, obj, **params):
        media_type, codec = self.get_codec(media_type)
        encoded = codec.encode(media_type, obj, **params)
        if isinstance(encoded, str):
            return (media_type, encoded)
        return encoded

    def decode(self, content_type, bytes):
        if not isinstance(content_type, ContentType):
            content_type = ContentType(content_type)

        codec = self[content_type.media_type]
        if isinstance(codec, self._Alias):
            raise KeyError(content_type.media_type)

        return codec.decode(content_type, bytes)


class Codec(object):

    """
    A superclass for implementing codecs.

    This class should be considered abstract (:meth:`encode` and :meth:`decode`
    are unimplemented), but it has a metaclass which will make those methods
    static.

    Example::

        >>> import simplejson
        >>> class JSONCodec(Codec):
        ...     def encode(media_type, obj, **params):
        ...         return (media_type, simplejson.dumps(obj, **params))
        ...     def decode(content_type, bytes):
        ...         return simplejson.loads(bytes)
        >>> JSONCodec.encode('application/json', {"a": 1})
        ('application/json', '{"a": 1}')
        >>> JSONCodec.decode('application/json', '{"a": 1}')
        {'a': 1}

    Note that ``encode()`` and ``decode()`` do not take ``self``; the metaclass
    will make them static methods automatically. This allows you to register
    the classes directly on a :class:`CodecRegister`.
    """

    class __metaclass__(type):
        def __new__(mcls, name, bases, attrs):
            if 'decode' in attrs:
                attrs['decode'] = staticmethod(attrs['decode'])
            if 'encode' in attrs:
                attrs['encode'] = staticmethod(attrs['encode'])
            return super(mcls, mcls).__new__(mcls, name, bases, attrs)

    def encode(media_type, obj, **params):

        """
        Encode a Python object into the given media type.

        :param media_type:
            The desired ``type/subtype`` media type for the output.
        :param obj:
            The Python object to encode.
        :params: Any additional parameters for the encoder.
        :returns:
            A two-tuple of ``(content_type, bytes)``, where ``content_type``
            should be a ``str`` of the full ``Content-Type`` header (including
            parameters) and ``bytes`` a ``str`` of the encoded output.
        """

        raise NotImplementedError

    def decode(content_type, bytes):

        """
        Decode a bytestring to a Python object, given its content-type.

        :param intessa.conneg.ContentType content_type:
            The declared ``Content-Type`` header from the HTTP server.
        :param str bytes:
            A string of the content itself.
        :returns: A Python object.
        """

        raise NotImplementedError
