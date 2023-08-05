import os
import stat


class StreamingBody(object):

    """
    A simple class to implement streaming request bodies with lengths.

        >>> from cStringIO import StringIO
        >>> sb = StreamingBody(StringIO("ABCD"), 4)
        >>> sb  # doctest: +ELLIPSIS
        <StreamingBody(<cStringIO.StringI object at 0x...>, 4)>
        >>> len(sb)
        4

    Features automatic length-checking on files:

        >>> sb = StreamingBody(open('file.txt'))  # doctest: +SKIP
        >>> sb  # doctest: +SKIP
        <StreamingBody(<open file 'file.txt', mode 'r' at 0x...>, 111)>
    """

    def __init__(self, body, length=None):
        self.body = body

        if length is None and hasattr(self.body, 'fileno'):
            try:
                body_stat = os.fstat(self.body.fileno())
                if stat.S_ISREG(body_stat.st_mode):
                    length = body_stat.st_size
            except OSError:
                length = None
        if length is None:
            raise TypeError("Needs a `length` argument (cannot stat: %r)" %
                            self.body)
        self.length = length

    def __repr__(self):
        return '<StreamingBody(%r, %d)>' % (self.body, self.length)

    def __len__(self):
        return self.length

    def __getattr__(self, attr):
        return getattr(self.body, attr)
