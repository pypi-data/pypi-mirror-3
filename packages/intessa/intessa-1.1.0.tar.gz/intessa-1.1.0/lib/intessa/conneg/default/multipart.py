import collections

import poster.encode

from intessa.conneg.codec_base import Codec
from intessa.conneg.content_type import ContentType
from intessa.conneg.streaming import StreamingBody


class FileLikeGeneratorWrapper(object):

    """
    Wraps a generator to provide a file-like (read-only) interface.

        >>> def alphabet():
        ...     yield "ABCDEFGHIJKL"
        ...     yield "MNOPQRS"
        ...     yield "TU"
        ...     yield "VWXYZ"
        >>> g = alphabet()
        >>> fh = FileLikeGeneratorWrapper(g)
        >>> fh.read(2)
        'AB'
        >>> fh.read(6)
        'CDEFGH'
        >>> fh.read(2)
        'IJ'
        >>> fh.read()
        'KLMNOPQRSTUVWXYZ'
        >>> fh.read()
        ''

    This only contains a :meth:`read` method, and its main use is to wrap the
    generator returned by ``poster.encode.multipart_encode()`` with an
    httplib-friendly interface.
    """

    def __init__(self, generator):
        self.generator = generator
        self.buffer = collections.deque()

    @property
    def _buffer_length(self):
        return sum(map(len, self.buffer))

    def _finish(self):
        try:
            return ''.join(self.buffer)
        finally:
            self.buffer.clear()

    def close(self):
        self.buffer.clear()
        self.generator.close()

    def read(self, bytes=None):
        if bytes is None:
            for string in self.generator:
                self.buffer.append(string)
            return self._finish()
        else:
            while self._buffer_length < bytes:
                try:
                    chunk = self.generator.next()
                    self.buffer.append(chunk)
                except StopIteration:
                    return self._finish()
            if self._buffer_length == bytes:
                return self._finish()
            elif self._buffer_length > bytes:
                string = ''.join(self.buffer)
                try:
                    return string[:bytes]
                finally:
                    self.buffer.clear()
                    self.buffer.append(string[bytes:])


class MultipartFormCodec(Codec):

    """
    Codec for multipart HTML forms (i.e. file uploads).
    """

    def encode(media_type, params):

        """
        Encode given params as multipart/form-data.

        Rather than returning a bytestring as a response (as most other codecs
        do), this codec will return a
        :class:`~intessa.conneg.streaming.StreamingBody` instance. This means
        for large file uploads, files will be streamed from disk in manageable
        chunks rather than being loaded into memory all at once.

            >>> MultipartFormCodec.encode('multipart/form-data', {'key': 'value'}) # doctest: +ELLIPSIS
            (ContentType('multipart/form-data; boundary=...'), <StreamingBody(...)>)

        The provided data is passed directly to
        ``poster.encode.multipart_encode()``; consult the `poster docs`_ for
        more information.

        .. _`poster docs`: http://atlee.ca/software/poster/
        """

        datagen, headers = poster.encode.multipart_encode(params)
        length = int(headers['Content-Length'])
        fp = FileLikeGeneratorWrapper(datagen)
        c_type = ContentType(headers['Content-Type'])
        return (c_type, StreamingBody(fp, length))

    def decode(c_type, bytes):
        """Decode a multipart form (not yet implemented)."""

        raise NotImplementedError
