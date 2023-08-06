"""Utilities for creating and manipulating HTTP ``Accept`` headers."""

from intessa.conneg import ContentType, DEFAULT_REGISTER


def make_accept_header(spec, codec_register=DEFAULT_REGISTER):

    """
    Build an accept header.

    Works on single strings:

        >>> make_accept_header('text/html')
        'text/html'

    Works on iterables of strings:

        >>> make_accept_header(('text/html', 'application/json'))
        'text/html,application/json'

    Works on iterables of type/quality pairs:

        >>> make_accept_header((('text/html', 0.7), ('application/json', 0.9)))
        'text/html;q=0.7,application/json;q=0.9'

    And mixed input:

        >>> make_accept_header((('text/html', 0.7), 'application/json'))
        'text/html;q=0.7,application/json'

    Also works on aliases defined on the codec register. Set up an alias:

        >>> from intessa.conneg.default import DEFAULT_REGISTER
        >>> reg = DEFAULT_REGISTER.copy()
        >>> reg.alias('app_json', 'application/json')

    And then use it on its own, or in lists:

        >>> make_accept_header('app_json', reg)
        'application/json'
        >>> make_accept_header(('app_json', 'text/html'), reg)
        'application/json,text/html'
        >>> make_accept_header((('app_json', 0.2), 'text/html'), reg)
        'application/json;q=0.2,text/html'
    """

    def resolve_media_type(mt):
        try:
            return codec_register.get_codec(mt)[0]
        except KeyError:
            return ContentType(mt).media_type

    if isinstance(spec, basestring):
        return resolve_media_type(spec)

    output = []
    for c_type in spec:
        if isinstance(c_type, basestring):
            output.append(resolve_media_type(c_type))
        else:
            media_type = resolve_media_type(c_type[0])
            quality = c_type[1]
            output.append('%s;q=%.1f' % (media_type, quality))
    return ','.join(output)
