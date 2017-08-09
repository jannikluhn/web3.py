class BaseMiddleware(object):
    def process_request(self, request_id, request):
        return request

    def process_response(self, request_id, response):
        return response
