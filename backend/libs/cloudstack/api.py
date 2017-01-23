class CloudStack(object):
    def __init__(self, api_url, authenticator):
        self.api_url = api_url
        self.authenticator = authenticator

    def open(self, **kwargs):
        self.authenticator.open(self,kwargs)

    def __getattr__(self, name):
        def function_handler(*args, **kwargs):
            return self.authenticator.do_request(name, kwargs)
        return function_handler