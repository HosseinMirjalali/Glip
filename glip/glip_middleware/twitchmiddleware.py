class TwitchMiddleware:
    """
    A middleware working on Twitch-related views. This includes checking user token, refreshing it, and then getting a
    new token if needed.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        #  self.context_response = {
        #  "msg": {"warning": "This is a warning from twitchmiddleware."}
        #  }

    def __call__(self, request):

        # print(request.path)
        # print(request.headers['Host'])
        # print(request.headers['Accept-Language'])
        # print(request.META['REQUEST_METHOD'])
        # print(request.META['HTTP_USER_AGENT'])

        response = self.get_response(request)

        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        print(f"view name: {view_func.__name__}")
        pass

    def process_exception(self, request, exception):
        pass

    def process_template_response(self, request, response):
        pass
