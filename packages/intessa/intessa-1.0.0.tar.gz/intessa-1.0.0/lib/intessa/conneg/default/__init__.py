from intessa.conneg.codec_base import CodecRegister

from text import TextCodec
from json import JSONCodec
from forms import SimpleFormCodec
from multipart import MultipartFormCodec
from xml import XMLCodec


__all__ = ['DEFAULT_REGISTER', 'TextCodec', 'JSONCodec', 'SimpleFormCodec',
           'MultipartFormCodec', 'XMLCodec']


DEFAULT_REGISTER = CodecRegister()

DEFAULT_REGISTER['text/plain'] = TextCodec
DEFAULT_REGISTER.alias('text', 'text/plain')

DEFAULT_REGISTER['application/json'] = JSONCodec
DEFAULT_REGISTER['text/javascript'] = JSONCodec
DEFAULT_REGISTER.alias('json', 'application/json')
DEFAULT_REGISTER.alias('json-js', 'text/javascript')

DEFAULT_REGISTER['application/x-www-form-urlencoded'] = SimpleFormCodec
DEFAULT_REGISTER.alias('form', 'application/x-www-form-urlencoded')

DEFAULT_REGISTER['multipart/form-data'] = MultipartFormCodec
DEFAULT_REGISTER.alias('multipart', 'multipart/form-data')

DEFAULT_REGISTER['application/xml'] = XMLCodec
DEFAULT_REGISTER.alias('xml', 'application/xml')
