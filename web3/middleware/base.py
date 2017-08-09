class BaseMiddleware(object):
    provider = None

    def __init__(self, provider):
        self.provider = provider

    def process_request(self, request_id, request):
        return request

    def process_response(self, request_id, response):
        return response
