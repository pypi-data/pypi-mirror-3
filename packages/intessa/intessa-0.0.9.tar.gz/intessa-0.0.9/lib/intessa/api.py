from functools import wraps

import requests
from urecord import Record
from urlobject import URLObject, encode_component

from conneg.accept import make_accept_header
from conneg.default import DEFAULT_REGISTER
from http import requests_http_backend
from utils.caseless_dict import CaselessDictionary

__all__ = ['API']


def replaces_url(meth):
    """Wrap a method on :class:`API` to return a new API with a new URL."""

    @wraps(meth)
    def wrapper(self, *args, **kwargs):
        url = meth(self, *args, **kwargs)
        # If the method is already reflexive, return the result directly.
        if isinstance(url, type(self)):
            return url
        # _replace() is defined by urecord.
        return self._replace(url=url)
    return wrapper


# We're using Record here for efficiency and immutability.
class API(Record('url', 'http')):

    """
    Represents a remote HTTP-accessible resource (and operations thereon).

    Example usage::

        >>> api = API(u'https://graph.facebook.com/')
        >>> api
        <intessa.API(u'https://graph.facebook.com/')>

    Build paths using attribute access or subscription syntax::

        >>> api[u'19292868552']
        <intessa.API(u'https://graph.facebook.com/19292868552')>
        >>> api.cocacola
        <intessa.API(u'https://graph.facebook.com/cocacola')>
        >>> api[u'btaylor'][u'picture']
        <intessa.API(u'https://graph.facebook.com/btaylor/picture')>

    Perform requests and receive :class:`responses <intessa.response.Response>`
    by calling the object::

        >>> api[u'19292868552']()  # doctest: +SKIP
        <intessa.Response[200, text/javascript]>

    """

    def __new__(cls, url, http=requests_http_backend):
        if not isinstance(url, URLObject):
            url = URLObject.parse(url)
        return super(API, cls).__new__(cls, url, http)

    def __repr__(self):
        return '<intessa.API(%r)>' % (unicode(self),)

    def __unicode__(self):
        return unicode(self.url)

    def __eq__(self, other):
        return unicode(self) == other

    def __hash__(self):
        return hash(unicode(self.url))

    @replaces_url
    def __add__(self, other):

        """
        Simple string concatenation is reflexive.

            >>> API(u'http://example.com/') + u'foo'
            <intessa.API(u'http://example.com/foo')>
        """

        return unicode(self) + other

    @replaces_url
    def __and__(self, params):

        """
        Add parameters to this URL.

        Accepts pairs or dictionaries:

            >>> API(u'http://example.com/') & ('a', 'b')
            <intessa.API(u'http://example.com/?a=b')>
            >>> API(u'http://example.com/') & {'a': 'b'}
            <intessa.API(u'http://example.com/?a=b')>

        Multiple additions of the same parameter will keep all of them, in the
        order they were specified:

            >>> API(u'http://example.com/') & ('a', 'b') & ('a', 'c')
            <intessa.API(u'http://example.com/?a=b&a=c')>
        """

        return self.url & params

    @replaces_url
    def __or__(self, params):

        """
        Add parameters to this URL, replacing existing parameters.

        Accepts pairs or dictionaries:

            >>> API(u'http://example.com/') | ('a', 'b')
            <intessa.API(u'http://example.com/?a=b')>
            >>> API(u'http://example.com/') | {'a': 'b'}
            <intessa.API(u'http://example.com/?a=b')>

        Multiple additions of the same parameter will replace old values:

            >>> API(u'http://example.com/') | ('a', 'b') | ('a', 'c')
            <intessa.API(u'http://example.com/?a=c')>
        """

        return self.url | params

    @replaces_url
    def __getattr__(self, attr):

        """
        Dynamic attribute access adds path components to the current URL.

            >>> API(u'http://example.com/').users
            <intessa.API(u'http://example.com/users')>
        """

        return self[attr]

    @replaces_url
    def __getitem__(self, item):

        """
        Subscription syntax is overridden to extend or modify the current URL.

        Example usage::

            >>> api = API(u'http://example.com/')

        In the simplest case, add a path component::

            >>> api['foo']
            <intessa.API(u'http://example.com/foo')>
            >>> api['foo']['bar']
            <intessa.API(u'http://example.com/foo/bar')>

        Replace the whole path by prefixing with a '/'::

            >>> api['foo']['bar']['/baz']
            <intessa.API(u'http://example.com/baz')>

        Add or modify a fragment identifier::

            >>> api['#foo']
            <intessa.API(u'http://example.com/#foo')>
            >>> api['#foo']['#bar']
            <intessa.API(u'http://example.com/#bar')>

        Add or modify a file extension::

            >>> api['foo']['.json']
            <intessa.API(u'http://example.com/foo.json')>
            >>> api['foo']['.json']['.xml']
            <intessa.API(u'http://example.com/foo.xml')>

        Adding a file extension to a non-leaf node will add an 'index'
        component::

            >>> api['.json']
            <intessa.API(u'http://example.com/index.json')>

        Any necessary escaping will be taken care of::

            >>> api['foo bar baz']
            <intessa.API(u'http://example.com/foo%20bar%20baz')>
            >>> api['#foo bar#baz']
            <intessa.API(u'http://example.com/#foo%20bar%23baz')>
            >>> api['foo']['.js o%n']
            <intessa.API(u'http://example.com/foo.js%20o%25n')>
        """

        if not isinstance(item, basestring):
            item = unicode(item)

        # Replace whole path with a new one.
        if item.startswith('/'):
            return self.url.with_path(item[1:])

        # Add/replace fragment identifier.
        if item.startswith('#'):
            return self.url.with_fragment(item[1:])

        # Add/replace file extension. Add an 'index' path component if current
        # path is not a leaf node.
        if item.startswith('.'):
            if self.url.endswith('/'):
                return self['index'][item]
            return self._with_file_ext(item[1:])

        # Standard case of adding a path component.
        return self.url / item

    @replaces_url
    def _with_file_ext(self, file_ext):

        """
        Add/replace a file extension on this URL.

        Example::

            >>> API(u'http://example.com/foo')._with_file_ext('.json')
            <intessa.API(u'http://example.com/foo.json')>

        The leading period is optional::

            >>> API(u'http://example.com/foo')._with_file_ext('json')
            <intessa.API(u'http://example.com/foo.json')>

        Existing file extensions will be replaced::

            >>> API(u'http://example.com/foo.json')._with_file_ext('xml')
            <intessa.API(u'http://example.com/foo.xml')>

        This method only works on leaf nodes::

            >>> API(u'http://example.com/foo/')._with_file_ext('json')
            Traceback (most recent call last):
                ...
            ValueError: Cannot add a file extension to directories.

        """

        if self.url.endswith('/'):
            raise ValueError("Cannot add a file extension to directories.")

        # 'https://example.com/foo/bar/baz.xyz' => 'baz.xyz'
        leaf_node = self.url.path_list()[-1]
        # 'baz.xyz' => 'baz'
        base = leaf_node.rsplit('.', 1)[0]

        if not file_ext.startswith('.'):
            file_ext = '.' + file_ext

        return self.url.parent() / (base + file_ext)

    def __call__(self, *args, **kwargs):

        """
        Perform an HTTP request and return a :class:`~intessa.response.Response`.

        :param data:
            A Python object representing the body of the request.

            There are several valid values this parameter can take:

            *   A bytestring, with a ``Content-Type`` header (given in
                ``headers``).
            *   A file-like object, with ``Content-Type`` and
                ``Content-Length`` headers.
            *   Any other Python object, with the ``type`` parameter provided.

            In the first two instances, it will be sent as-is. In the second,
            it will first be encoded to a bytestring, using the codec for the
            specified type.

        :param type:
            The Internet media type with which the ``data`` argument should be
            encoded. This will be used as a lookup type against the
            ``codec_register``.

        :param codec_register:
            A :class:`~intessa.conneg.codec_base.CodecRegister` to use for
            encoding the request body and decoding the response. Defaults to
            :data:`~intessa.conneg.default.DEFAULT_REGISTER`.

        :param accept:
            A specification of acceptable response types, which will be turned
            into an HTTP ``Accept`` header.

            This argument can be a string representing a media type (see:
            :class:`~intessa.conneg.content_type.ContentType`), a list of such
            strings, or a list of ``(media_type, quality)`` pairs, where
            ``quality`` is a floating-point number. See the documentation for
            :func:`~intessa.conneg.accept.make_accept_header` for examples of
            how this argument is turned into an ``Accept`` header.

        :param headers:
            A dictionary of raw HTTP headers to send.

        Note that if a non-successful response is returned, an instance of
        :class:`intessa.Error` will be *raised*.
        """

        method = kwargs.pop('method', 'GET')
        accept = kwargs.pop('accept', None)
        headers = CaselessDictionary(kwargs.pop('headers', {}))

        if accept is not None:
            headers['Accept'] = make_accept_header(accept)

        if 'data' in kwargs:
            data = kwargs.pop('data')
            if method == 'GET':
                method = 'POST'
            if ((isinstance(data, str) and 'content-type' in headers) or
                (hasattr(data, 'read') and
                 'content-type' in headers and
                 'content-length' in headers)):
                kwargs['data'] = data
            elif 'type' not in kwargs:
                raise TypeError("Request data provided with no content type information")
            else:
                codec_register = kwargs.pop('codec_register', DEFAULT_REGISTER)
                headers['content-type'], kwargs['data'] = codec_register.encode(
                    kwargs.pop('type'), data)

        kwargs['headers'] = headers
        return self.http(self, method, self.url, *args, **kwargs)

    def _post(self, *args, **kwargs):
        """Shim for issuing POST requests."""

        kwargs.setdefault('method', 'POST')
        return self(*args, **kwargs)

    def _put(self, *args, **kwargs):
        """Shim for issuing PUT requests."""

        kwargs.setdefault('method', 'PUT')
        return self(*args, **kwargs)

    def _delete(self, *args, **kwargs):
        """Shim for issuing DELETE requests."""

        kwargs.setdefault('method', 'DELETE')
        return self(*args, **kwargs)
