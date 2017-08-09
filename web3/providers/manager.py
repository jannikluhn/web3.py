import uuid
import warnings

from cytoolz import (
    compose,
    partial,
)

from web3.utils.compat import (
    spawn,
)


class RequestManager(object):
    def __init__(self, provider, middleware_classes=None):
        if middleware_classes is None:
            middleware_classes = tuple()

        self.pending_requests = {}
        self.middleware_classes = middleware_classes
        self.provider = provider

    _provider = None

    @property
    def provider(self):
        return self._provider

    @provider.setter
    def provider(self, value):
        self._provider = value
        self.middlewares = tuple(
            middleware_class(value)
            for middleware_class
            in self.middleware_classes
        )

    def setProvider(self, provider):
        warnings.warn(DeprecationWarning(
            "The `setProvider` API has been deprecated.  You should update your "
            "code to directly set the `manager.provider` property."
        ))
        self.provider = provider

    #
    # Middleware
    #
    middlewares = None

    def _process_request(self, request_id, request):
        """
        `raw_method` and `raw_params` are the original values for the RPC
        request.  Each middleware may modify these in arbitrary ways.  The
        `request_id` is a unique value for the given request which will be
        passed in with the response as well
        """
        return compose(*(
            partial(middleware.process_request, request_id=request_id)
            for middleware
            in reversed(self.middlewares)
        ))(request)

    def _process_response(self, request_id, response):
        return compose(*(
            partial(middleware.process_request, request_id=request_id)
            for middleware
            in self.middlewares
        ))(response)

    #
    # Provider requests and response
    #
    def _get_request_id(self):
        request_id = uuid.uuid4()
        return request_id

    def request_blocking(self, raw_method, raw_params, request_id=None):
        """
        Make a synchronous request using the provider
        """
        if request_id is None:
            request_id = self._get_request_id()

        method, params = self._process_request(request_id, (raw_method, raw_params))
        raw_response = self.provider.make_request(method, params)
        response = self._process_response(request_id, raw_response)

        if "error" in response:
            raise ValueError(response["error"])

        return response['result']

    def request_async(self, raw_method, raw_params):
        request_id = self._get_request_id()
        self.pending_requests[request_id] = spawn(
            self.request_blocking,
            raw_method=raw_method,
            raw_params=raw_params,
            request_id=request_id,
        )
        return request_id

    def receive_blocking(self, request_id, timeout=None):
        try:
            request = self.pending_requests.pop(request_id)
        except KeyError:
            raise KeyError("Request for id:{0} not found".format(request_id))
        else:
            response = request.get(timeout=timeout)

        if "error" in response:
            raise ValueError(response["error"])

        return response['result']

    def receive_async(self, request_id, *args, **kwargs):
        raise NotImplementedError("Callback pattern not implemented")
