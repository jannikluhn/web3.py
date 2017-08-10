from web3.manager import (
    RequestManager,
)
from web3.providers import (
    BaseProvider,
)
from web3.middleware import (
    BaseMiddleware,
)


class DummyMiddleware(BaseMiddleware):
    pass


class DummyProvider(BaseProvider):
    pass


def test_provider_property_setter_and_getter():
    provider_a = DummyProvider()
    provider_b = DummyProvider()

    middleware_classes = [DummyMiddleware]

    assert provider_a is not provider_b

    manager = RequestManager(provider_a, middleware_classes=middleware_classes)
    assert manager.provider is provider_a
    assert manager.middlewares[0].provider is provider_a

    manager.provider = provider_b

    assert manager.provider is provider_b
    assert manager.middlewares[0].provider is provider_b
