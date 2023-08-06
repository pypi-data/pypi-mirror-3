# -*- coding: utf-8 -*-

import re

from urecord import Record

from intessa.conneg import ContentType
from intessa.conneg.default import DEFAULT_REGISTER
from intessa.utils.caseless_dict import CaselessDictionary


class Response(Record('api',
                      # The essence of an HTTP response:
                      'status_code',
                      'headers',
                      'content',
                      'codec_register')):

    """
    An HTTP response, created by calling an :class:`intessa.api.API`.

    The following attributes all need to be set when constructing a response.

    .. py:attribute:: api

        The :class:`intessa.api.API` instance which created this Response.

    .. py:attribute:: status_code

        An integer representing the HTTP status code of the response.

    .. py:attribute:: headers

        A case-insensitive dictionary (or dict-like object) containing header
        names and values.

    .. py:attribute:: content

        A bytestring (i.e. ``str`` instance) containing the body of the
        response.

    You may optionally set the following:

    .. py:attribute:: codec_register

        An instance of :class:`intessa.conneg.codec_base.CodecRegister`, to be
        used for decoding this response. Defaults to
        :data:`~intessa.conneg.default.DEFAULT_REGISTER`.

    All the other attributes are dynamically created by the class itself.
    """

    def __new__(cls, api, status_code, headers, content,
                codec_register=DEFAULT_REGISTER):
        headers = CaselessDictionary(headers)
        return super(cls, cls).__new__(cls, api=api,
                                       status_code=status_code,
                                       headers=headers, content=content,
                                       codec_register=codec_register)

    def __repr__(self):
        if 'content-type' in self.headers:
            mimetype = self.headers['content-type'].split(';')[0]
            return '<intessa.Response[%d, %s]>' % (self.status_code, mimetype)
        return '<intessa.Response[%d]>' % (self.status_code,)

    @property
    def type(self):

        """
        A :class:`intessa.conneg.ContentType` for this response.

        Use this to implement conditional handling of various types.

        :raises: ``AttributeError`` if no Content-Type header was given.

        Example::

            >>> resp = Response(None, 200,
            ...     {'content-type': 'text/html; charset=utf-8'},
            ...     '<html></html>')
            >>> resp.type
            ContentType('text/html; charset=utf-8')
            >>> resp.type.media_type
            'text/html'
            >>> resp.type.params['charset']
            'utf-8'
        """

        if 'content-type' not in self.headers:
            raise AttributeError("Response does not have a content type")
        return ContentType(self.headers['content-type'])

    @property
    def value(self):

        ur"""
        The content of this HTTP response, decoded into a Python object.

        This method uses the :attr:`codec_register` to decode responses. An
        object is retrieved simply by passing the content type and content
        bytestring into ``codec_register.decode()``.

        Note that the object will be decoded once per access; store a reference
        to the returned object if you wish to use it more than once.

            >>> json = Response(None, 200,
            ...     {'content-type': 'application/json'},
            ...     '{"a": 1}')
            >>> json.value
            {'a': 1}

            >>> text = Response(None, 200,
            ...     {'content-type': 'text/plain; charset=utf-8'},
            ...     'H\xc3\xa9llo W\xc3\xb6rld')
            >>> text.value
            u'H\xe9llo W\xf6rld'
        """

        return self.codec_register.decode(self.type, self.content)


class ResponseException(Exception):

    """
    Raiseable responses (for non-successful HTTP responses).

    On the one hand, these exceptions can be used in exactly the same way as
    :class:`~intessa.response.Response`:

        >>> response = Response(api=None, status_code=403,
        ...     headers={'content-type': 'application/json'},
        ...     content='{"error": "Forbidden"}')
        >>> exc = ResponseException(response)
        >>> exc
        <intessa.Error[403, application/json]>
        >>> exc.value
        {'error': 'Forbidden'}

    However, the main use of response exceptions is for raising and subsequent
    pattern matching using ``except`` statements:

        >>> try:
        ...     raise exc
        ... except ResponseException['4xx'], captured:
        ...     print "Captured!"
        Captured!

    In this case, for example, you can capture ``4xx``, ``40x`` and ``403``;
    the class hierarchy will be dynamically created and cached on
    :class:`ResponseException` itself:

        >>> isinstance(exc, ResponseException['4xx'])
        True
        >>> isinstance(exc, ResponseException['40x'])
        True
        >>> isinstance(exc, ResponseException['403'])
        True

    The class is aliased as ``intessa.Error`` for the sake of convenience:

        >>> import intessa
        >>> intessa.Error['403'] is intessa.ResponseException['403']
        True
    """

    exception_class_cache = {}

    class __metaclass__(type):

        def __getitem__(cls, status_code):
            status_code = str(status_code)
            if re.match(r'^[0-9]xx$', status_code):
                return cls.make_exception_class(status_code, parent=cls)
            elif re.match(r'^[0-9][0-9]x$', status_code):
                parent = cls.make_exception_class(status_code[:1] + 'xx', parent=cls)
                return cls.make_exception_class(status_code, parent=parent)
            elif re.match(r'^[0-9][0-9][0-9]$', status_code):
                parent1 = cls.make_exception_class(status_code[:1] + 'xx', parent=cls)
                parent2 = cls.make_exception_class(status_code[:2] + 'x', parent=parent1)
                return cls.make_exception_class(status_code, parent=parent2, final=True)
            raise KeyError("Not a valid status code pattern: %r" % (status_code,))

        def make_exception_hierarchy(cls, status):
            """Build the exception hierarchy for a given (full) status code."""

            status = str(status)
            if not re.match(r'^[0-9]{3}$', status):
                raise ValueError("Invalid status code format: %r" % (status,))

            matching_codes = [status[:1] + 'xx',
                              status[:2] + 'x',
                              status[:3]]
            return reduce(
                lambda parent, code: cls.make_exception_class(code, parent=parent),
                matching_codes, cls)

        def make_exception_class(cls, code, parent=None, final=False):
            """Create the exception class for a given status code pattern."""

            if code in cls.exception_class_cache:
                return cls.exception_class_cache[code]

            name = '%s[%s]' % (cls.__name__, code)

            if parent is None:
                parent = cls
            bases = (parent,)

            attrs = {}
            if final:
                attrs = {'__new__': Exception.__new__}

            exc_class = type(name, bases, attrs)
            cls.exception_class_cache[code] = exc_class
            return exc_class

    def __new__(cls, response):
        status = str(response.status_code)
        return cls[status](response)

    def __repr__(self):
        if 'content-type' in self.headers:
            mimetype = self.headers['content-type'].split(';')[0]
            return '<intessa.Error[%d, %s]>' % (self.status_code, mimetype)
        return '<intessa.Error[%d]>' % (self.status_code,)

    def __init__(self, response):
        self.response = response

    def __getattr__(self, attr):
        return getattr(self.response, attr)
