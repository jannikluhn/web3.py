import pytest

from web3.manager import (
    RequestManager,
)


def test_setProvider_api_deprecation():
    manager = RequestManager(None)

    with pytest.warns(DeprecationWarning):
        manager.setProvider(None)
