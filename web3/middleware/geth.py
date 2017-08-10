from __future__ import absolute_import

from .formatting import (
    BaseFormatterMiddleware,
)


def hex_to_integer(value):
    return int(value, 16)


class GethFormattingMiddleware(BaseFormatterMiddleware):
    request_formatters = {
    }
    result_formatters = {
        'eth_gasPrice': hex_to_integer,
    }
