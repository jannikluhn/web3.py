from __future__ import absolute_import

import codecs

from cytoolz.curried import (
    keymap,
    valmap,
)
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
    is_dict,
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


@curry
@to_list
def apply_formatter_to_array(formatter, value):
    for item in value:
        yield formatter(item)


block_number_formatter = apply_formatter_if(hex, is_integer)

is_not_null = complement(is_null)


# TODO: decide what inputs this allows.
TRANSACTION_PARAMS_FORMATTERS = {
    'value': hex,
    'gas': hex,
    'gasPrice': hex,
    'nonce': hex,
}


transaction_params_formatter = apply_formatters_to_dict(TRANSACTION_PARAMS_FORMATTERS)


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


LOG_ENTRY_FORMATTERS = {
    'blockHash': apply_formatter_if(bytes_to_ascii, is_not_null),
    'blockNumber': apply_formatter_if(hex_to_integer, is_not_null),
    'transactionIndex': apply_formatter_if(hex_to_integer, is_not_null),
    'logIndex': hex_to_integer,
    'address': bytes_to_ascii,
}


log_entry_formatter = apply_formatters_to_dict(LOG_ENTRY_FORMATTERS)


RECEIPT_FORMATTERS = {
    'blockHash': apply_formatter_if(bytes_to_ascii, is_not_null),
    'blockNumber': apply_formatter_if(hex_to_integer, is_not_null),
    'transactionIndex': apply_formatter_if(hex_to_integer, is_not_null),
    'transactionHash': bytes_to_ascii,
    'cumulativeGasUsed': hex_to_integer,
    'gasUsed': hex_to_integer,
    'contractAddress': apply_formatter_if(bytes_to_ascii, is_not_null),
    'logs': apply_formatter_to_array(log_entry_formatter),
}


receipt_formatter = apply_formatters_to_dict(RECEIPT_FORMATTERS)

BLOCK_FORMATTERS = {
    'gasLimit': hex_to_integer,
    'gasUsed': hex_to_integer,
    'size': hex_to_integer,
    'timestamp': hex_to_integer,
    'hash': bytes_to_ascii,
    'number': apply_formatter_if(hex_to_integer, is_not_null),
    'difficulty': hex_to_integer,
    'totalDifficulty': hex_to_integer,
    'transactions': apply_formatter_to_array(
        apply_formatter_if(transaction_formatter, is_dict)
    ),
}


block_formatter = apply_formatters_to_dict(BLOCK_FORMATTERS)


SYNCING_FORMATTERS = {
    'startingBlock': hex_to_integer,
    'currentBlock': hex_to_integer,
    'highestBlock': hex_to_integer,
    'knownStates': hex_to_integer,
    'pulledStates': hex_to_integer,
}


syncing_formatter = apply_formatters_to_dict(SYNCING_FORMATTERS)


TRANSACTION_POOL_CONTENT_FORMATTERS = {
    'pending': compose(
        keymap(bytes_to_ascii),
        valmap(transaction_formatter),
    ),
    'queued': compose(
        keymap(bytes_to_ascii),
        valmap(transaction_formatter),
    ),
}


transaction_pool_content_formatter = apply_formatters_to_dict(
    TRANSACTION_POOL_CONTENT_FORMATTERS
)


TRANSACTION_POOL_INSPECT_FORMATTERS = {
    'pending': keymap(bytes_to_ascii),
    'queued': keymap(bytes_to_ascii),
}


transaction_pool_inspect_formatter = apply_formatters_to_dict(
    TRANSACTION_POOL_INSPECT_FORMATTERS
)


class GethFormattingMiddleware(BaseFormatterMiddleware):
    request_formatters = {
        # Eth
        'eth_call': apply_formatter_at_index(transaction_params_formatter, 0),
        'eth_getBalance': apply_formatter_at_index(block_number_formatter, 1),
        'eth_getBlockByNumber': apply_formatter_at_index(block_number_formatter, 0),
        'eth_getBlockTransactionCountByNumber': apply_formatter_at_index(
            block_number_formatter,
            1,
        ),
        'eth_getBlockTransactionCountByHash': apply_formatter_at_index(
            block_number_formatter,
            1,
        ),
        'eth_getCode': apply_formatter_at_index(block_number_formatter, 1),
        'eth_getStorageAt': compose(
            apply_formatter_at_index(hex, 1),
            apply_formatter_at_index(block_number_formatter, 2),
        ),
        'eth_getTransactionByBlockNumberAndIndex': compose(
            apply_formatter_at_index(block_number_formatter, 0),
            apply_formatter_at_index(hex, 1),
        ),
        'eth_getTransactionByBlockHashAndIndex': apply_formatter_at_index(hex, 1),
        'eth_getTransactionCount': apply_formatter_at_index(block_number_formatter, 1),
        'eth_sendTransaction': apply_formatter_at_index(transaction_params_formatter, 0),
    }
    result_formatters = {
        # Eth
        'eth_accounts': apply_formatter_to_iterable(bytes_to_ascii),
        'eth_blockNumber': hex_to_integer,
        'eth_coinbase': bytes_to_ascii,
        'eth_estimateGas': hex_to_integer,
        'eth_gasPrice': hex_to_integer,
        'eth_getBlockByHash': block_formatter,
        'eth_getBlockByNumber': block_formatter,
        'eth_getBlockTransactionCountByHash': hex_to_integer,
        'eth_getBlockTransactionCountByNumber': hex_to_integer,
        'eth_getCode': bytes_to_ascii,
        'eth_getFilterChanges': apply_formatter_to_array(log_entry_formatter),
        'eth_getFilterLogs': apply_formatter_to_array(log_entry_formatter),
        'eth_getTransactionByBlockHashAndIndex': apply_formatter_if(
            transaction_formatter,
            is_not_null,
        ),
        'eth_getTransactionByBlockNumberAndIndex': apply_formatter_if(
            transaction_formatter,
            is_not_null,
        ),
        'eth_getTransactionByHash': apply_formatter_if(transaction_formatter, is_not_null),
        'eth_getTransactionCount': hex_to_integer,
        'eth_getTransactionReceipt': apply_formatter_if(
            receipt_formatter,
            is_not_null,
        ),
        'eth_hashrate': hex_to_integer,
        'eth_protocolVersion': hex_to_integer,
        'eth_sendRawTransaction': bytes_to_ascii,
        'eth_sendTransaction': bytes_to_ascii,
        'eth_syncing': apply_formatter_if(syncing_formatter, is_dict),
        # Network
        'net_version': hex_to_integer,
        'net_peerCount': hex_to_integer,
        # SHH
        'shh_version': hex_to_integer,
        # Transaction Pool
        'txpool_content': transaction_pool_content_formatter,
        'txpool_inspect': transaction_pool_inspect_formatter,
    }
