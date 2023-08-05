"""
Code responsible for low-level HTTP interactions.

At the moment this just contains the default HTTP backend for
:class:`intessa.API`, based on the urllib3_ library for Python.

.. _urllib3: http://urllib3.readthedocs.org/
"""

import urllib3

from intessa.conneg.default import DEFAULT_REGISTER
from intessa.response import Response, ResponseException


class PoolManagerWithHTTPBackend(urllib3.PoolManager):

    """
    An extended ``urllib3.PoolManager`` with an intessa HTTP backend.

    This allows you to create your own custom pool, and then use its
    :meth:`intessa_http_backend` method as the ``http`` attribute on an
    :class:`~intessa.API`. By default, a global instance is created as
    :data:`DEFAULT_POOL_MANAGER` and this is used as the source of the default
    HTTP backend function.
    """

    def intessa_http_backend(self, api, method, url, *args, **kwargs):
        codec_register = kwargs.pop('codec_register', DEFAULT_REGISTER)
        if 'data' in kwargs:
            kwargs['body'] = kwargs.pop('data')

        # This will raise any socket errors if they occur, but non-2xx
        # responses will still be passed through normally.
        http_response = self.urlopen(method, url, *args, **kwargs)
        response = Response(api=api,
                            status_code=http_response.status,
                            headers=http_response.headers,
                            content=http_response.data,
                            codec_register=codec_register)

        if (response.status_code // 100) != 2:
            raise ResponseException(response)
        return response

DEFAULT_POOL_MANAGER = PoolManagerWithHTTPBackend()
urllib3_http_backend = DEFAULT_POOL_MANAGER.intessa_http_backend
