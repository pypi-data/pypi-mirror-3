"""
Code responsible for low-level HTTP interactions.

At the moment this just contains the default HTTP backend for
:class:`intessa.API`, based on the requests_ library for Python.

.. _requests: http://python-requests.org/
"""

from requests import request, exceptions

from intessa.conneg.default import DEFAULT_REGISTER
from intessa.response import Response, ResponseException


def requests_http_backend(api, method, url, *args, **kwargs):
    """Shim over ``requests.request`` to return :class:`Responses <intessa.response.Response>`."""

    codec_register = kwargs.pop('codec_register', DEFAULT_REGISTER)
    http_response = request(method, url, *args, **kwargs)

    if not http_response.status_code and http_response.error:
        if isinstance(http_response.error, exceptions.Timeout):
            raise http_response.error.args[0]
        raise http_response.error

    response = Response(api=api,
                        status_code=http_response.status_code,
                        headers=http_response.headers,
                        content=http_response.content,
                        codec_register=codec_register)

    if (response.status_code // 100) != 2:
        raise ResponseException(response)
    return response
