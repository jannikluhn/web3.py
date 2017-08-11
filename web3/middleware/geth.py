from __future__ import absolute_import

import codecs

from cytoolz.functoolz import (
    curry,
    identity,
)

from eth_utils import (
    to_list,
    to_dict,
    is_integer,
)

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


@curry
@to_list
def apply_formatter_at_index(formatter, at_index, value):
    if at_index + 1 > len(value):
        raise IndexError(
            "Not enough values in iterable to apply formatter.  Got: {0}. "
            "Need: {1}".format(len(value), at_index)
        )
    for index, item in enumerate(value):
        if index == at_index:
            yield formatter(item)
        else:
            yield item


@curry
def apply_formatter_if(formatter, condition, value):
    if condition(value):
        return formatter(value)
    else:
        return value


@curry
@to_dict
def apply_formatters_to_dict(formatters, value, default_formatter=identity):
    for key, item in value.items():
        formatter = formatters.get(key, default_formatter)
        yield key, formatter(item)


block_number_formatter = apply_formatter_if(hex, is_integer)


class GethFormattingMiddleware(BaseFormatterMiddleware):
    request_formatters = {
        'eth_getBalance': apply_formatter_at_index(block_number_formatter, 1),
        'eth_getCode': apply_formatter_at_index(block_number_formatter, 1),
        'eth_getBlockTransactionCountByNumber': apply_formatter_at_index(
            block_number_formatter,
            1,
        ),
        'eth_getBlockTransactionCountByHash': apply_formatter_at_index(
            block_number_formatter,
            1,
        ),
    }
    result_formatters = {
        'eth_gasPrice': hex_to_integer,
        'eth_hashrate': hex_to_integer,
        'eth_blockNumber': hex_to_integer,
        'eth_accounts': apply_formatter_to_iterable(bytes_to_ascii),
        'eth_getBlockTransactionCountByHash': hex_to_integer,
        'eth_getBlockTransactionCountByNumber': hex_to_integer,
    }
