from __future__ import absolute_import

import codecs

from cytoolz.functoolz import (
    curry
)

from eth_utils import to_list

from .formatting import (
    BaseFormatterMiddleware,
)


def hex_to_integer(value):
    return int(value, 16)


def bytes_to_ascii(value):
    return codecs.decode(value, 'ascii')


@curry
@to_list
def apply_formatter_to_iterable(formatter, value):
    for item in value:
        yield formatter(item)


class GethFormattingMiddleware(BaseFormatterMiddleware):
    request_formatters = {
    }
    result_formatters = {
        'eth_gasPrice': hex_to_integer,
        'eth_hashrate': hex_to_integer,
        'eth_blockNumber': hex_to_integer,
        'eth_accounts': apply_formatter_to_iterable(bytes_to_ascii),
    }
