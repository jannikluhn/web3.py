from __future__ import absolute_import

import codecs

from cytoolz.functoolz import (
    compose,
    curry,
    complement,
)

from eth_utils import (
    to_list,
    to_dict,
    is_integer,
    is_null,
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
def apply_formatters_to_dict(formatters, value):
    for key, item in value.items():
        if key in formatters:
            yield key, formatters[key](item)
        else:
            yield key, item


block_number_formatter = apply_formatter_if(hex, is_integer)

is_not_null = complement(is_null)


TRANSACTION_FORMATTERS = {
    'blockNumber': apply_formatter_if(hex_to_integer, is_not_null),
    'transactionIndex': apply_formatter_if(hex_to_integer, is_not_null),
    'nonce': hex_to_integer,
    'gas': hex_to_integer,
    'gasPrice': hex_to_integer,
    'value': hex_to_integer,
    'from': bytes_to_ascii,
    'to': bytes_to_ascii,
    'hash': bytes_to_ascii,
}


transaction_formatter = apply_formatters_to_dict(TRANSACTION_FORMATTERS)


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
        'eth_getStorageAt': compose(
            apply_formatter_at_index(hex, 1),
            apply_formatter_at_index(block_number_formatter, 2),
        ),
    }
    result_formatters = {
        'eth_gasPrice': hex_to_integer,
        'eth_hashrate': hex_to_integer,
        'eth_blockNumber': hex_to_integer,
        'eth_accounts': apply_formatter_to_iterable(bytes_to_ascii),
        'eth_getBlockTransactionCountByHash': hex_to_integer,
        'eth_getBlockTransactionCountByNumber': hex_to_integer,
        'eth_coinbase': bytes_to_ascii,
        'eth_getCode': bytes_to_ascii,
        'eth_getTransactionByHash': apply_formatter_if(transaction_formatter, is_not_null),
    }
