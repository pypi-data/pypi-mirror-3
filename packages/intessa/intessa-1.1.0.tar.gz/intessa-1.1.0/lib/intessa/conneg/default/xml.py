# -*- coding: utf-8 -*-

import lxml.etree
import lxml.objectify

from intessa.conneg.codec_base import Codec


class XMLCodec(Codec):

    """Default XML codec, using ``lxml.objectify``."""

    def encode(media_type, etree, **params):

        ur"""
        Encode an lxml ``ElementTree`` using ``lxml.etree.tostring()``.

        By default, the output will include an XML prolog, and will be
        utf-8-encoded. This can be overridden by passing ``xml_declaration``
        (``True`` or ``False``, default ``True``) and ``encoding`` (default
        ``'utf-8'``) keywords.

        See http://lxml.de/api/lxml.etree-module.html#tostring for a detailed
        overview of available options.

            >>> tree = lxml.etree.fromstring('<obj><attr>value</attr></obj>')
            >>> tree.find('attr').text = u"vålúè"
            >>> XMLCodec.encode('application/xml', tree)
            ('application/xml', "<?xml version='1.0' encoding='utf-8'?>\n<obj><attr>v\xc3\xa5l\xc3\xba\xc3\xa8</attr></obj>")
        """

        params.setdefault('xml_declaration', True)
        params.setdefault('with_tail', False)
        if params['xml_declaration']:
            params.setdefault('encoding', 'utf-8')

        return (media_type, lxml.etree.tostring(etree, **params))

    def decode(content_type, bytes):

        """
        Decode an XML bytestring to a Python object, using ``lxml.objectify``.

        For more information on these objects, see
        http://lxml.de/objectify.html.

            >>> doc = XMLCodec.decode('application/xml', '<obj><attr>value</attr></obj>')
            >>> doc # doctest: +ELLIPSIS
            <Element obj at 0x...>
            >>> doc.tag
            'obj'
            >>> doc.attr
            'value'
        """

        return lxml.objectify.fromstring(bytes)
