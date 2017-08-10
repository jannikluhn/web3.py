import copy
import uuid

from web3.manager import (
    RequestManager,
)
from web3.providers import (
    BaseProvider,
)
from web3.middleware import (
    BaseMiddleware,
)


class BaseDummyMiddleware(BaseMiddleware):
    key = None

    def process_request(self, method, params, request_id):
        params.append(self.key)
        method = "|".join((method, self.key))
        return method, params

    def process_result(self, result, request_id):
        result['middlewares'].append(self.key)
        return result


class MiddlwareA(BaseDummyMiddleware):
    key = 'middleware-A'


class MiddlwareB(BaseDummyMiddleware):
    key = 'middleware-B'


class DummyProvider(BaseProvider):
    def make_request(self, method, params):
        return {'result': {
            'method': method,
            'params': params,
            'middlewares': [],
        }}


def test_provider_property_setter_and_getter():
    provider = DummyProvider()

    middleware_classes = [MiddlwareA, MiddlwareB]

    manager = RequestManager(provider, middleware_classes=middleware_classes)
    middleware_a, middleware_b = manager.middlewares
    response = manager.request_blocking('init', ['init'], 'id-12345')

    assert response['method'] == 'init|middleware-A|middleware-B'
    assert response['params'] == ['init', 'middleware-A', 'middleware-B']
    assert response['middlewares'] == ['middleware-B', 'middleware-A']
