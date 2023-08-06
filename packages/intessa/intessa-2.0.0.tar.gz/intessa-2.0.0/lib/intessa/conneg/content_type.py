"""This module contains representations of internet media type strings."""

import email.message
import mimetypes

import odict

# Load the default MIME types database.
if not mimetypes.inited:
    mimetypes.init()
if hasattr(mimetypes, '_db'):
    DEFAULT_MIMETYPES_DB = mimetypes._db
else:
    DEFAULT_MIMETYPES_DB = mimetypes.guess_extension.im_self

__all__ = ['ContentType']


class ContentType(str):

    """
    An HTTP ``Content-Type`` header.

    This is a subclass of ``str``, not ``unicode``, in accordance with RFC 2616
    (http://www.ietf.org/rfc/rfc2616), which states that only US-ASCII is to be
    used in Content-Type headers.

    Create a header from a bytestring::

        >>> c_type = ContentType('text/html; charset=utf-8')
        >>> c_type
        ContentType('text/html; charset=utf-8')

    Access the media type on its own::

        >>> c_type.media_type
        'text/html'

    And the parameters, as an ordered dictionary::

        >>> c_type.params
        odict([('charset', 'utf-8')])
    """

    def __repr__(self):
        return 'ContentType(%r)' % (self._normalize(),)

    def __str__(self):
        return self._normalize()

    def __eq__(self, other):

        """
        Determine equality, preserving order and ignoring whitespace.

            >>> ContentType('text/html') == 'text/html'
            True
            >>> ContentType('text/html; k=v') == 'text/html; k=v'
            True
            >>> ContentType('text/html; a=1; b=2') == 'text/html; b=2; a=1'
            False
            >>> ContentType('text/html  ; a=1 ; b=2') == 'text/html; a=1; b=2'
            True
        """

        self_parsed = self._parse(self)
        other_parsed = self._parse(str(other))
        return self_parsed == other_parsed

    @staticmethod
    def _parse(string):

        """
        Parse a Content-Type header using ``email.message.Message``.

        :returns: ``[('type/subtype', ''), ('param1', 'value1'), ...]``.
        """

        msg = email.message.Message()
        msg.add_header('Content-Type', string)
        return msg.get_params()

    def _normalize(self):

        """
        Normalize whitespace in this Content-Type header.

        Example::

            >>> ContentType('text/html;a=1;b=2')._normalize()
            'text/html; a=1; b=2'
            >>> ContentType('text/html  ;  a=1    ;  b=2')._normalize()
            'text/html; a=1; b=2'
        """

        params = '; '.join('='.join(pair) for pair in self.params.iteritems())
        return '%s; %s' % (self.media_type, params)

    @property
    def media_type(self):

        """
        Just the ``type/subtype`` pair of this content type.

            >>> ContentType('text/html; charset=utf-8').media_type
            'text/html'
        """

        return self._parse(self)[0][0]

    @property
    def params(self):

        """
        An ordered dict of the ``key=value`` parameters of this header.

            >>> ContentType('text/html; charset=utf-8').params
            odict([('charset', 'utf-8')])
            >>> ContentType('text/html; charset=utf-8').params['charset']
            'utf-8'
            >>> ContentType('text/html; charset=utf-8; boundary=xxx').params
            odict([('charset', 'utf-8'), ('boundary', 'xxx')])

        Note that each time you access this attribute a new dictionary will be
        created; modifications are unrecommended and will not persist.
        """

        return odict.odict(self._parse(self)[1:])

    def guess_extensions(self, db=DEFAULT_MIMETYPES_DB):

        """
        Return a list of likely file extensions for this media type.

        :keyword db: An instance of ``mimetypes.MimeTypes``; if unspecified,
                     will use the global default.
        :returns: A list of bytestrings, which will be empty if no matches were
                  found.

        Example::

            >>> ContentType('text/html').guess_extensions()
            ['.html', '.htm']
            >>> ContentType('application/x-will-not-match').guess_extensions()
            []
        """

        return db.guess_all_extensions(self.media_type) or []

    def guess_extension(self, db=DEFAULT_MIMETYPES_DB):
        """
        Return a likely file extension for this media type, or ``None``.

        :keyword db: An instance of ``mimetypes.MimeTypes``; if unspecified,
                     will use the global default.
        :returns: A single bytestring or ``None``.

        Example::

            >>> ContentType('text/html').guess_extension()
            '.html'
            >>> ContentType('application/x-will-not-match').guess_extension()
        """

        return db.guess_extension(self.media_type)
