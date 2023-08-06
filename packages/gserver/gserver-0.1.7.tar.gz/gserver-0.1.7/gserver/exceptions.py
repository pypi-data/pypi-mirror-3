class HttpError(BaseException):
    """ Base gserver Http exception """
    def __init__(self, code):
        self.code = code

class Http403(HttpError):
    """ Exception used to respond with a 403, instead of a success and data """
    def __init__(self):
        super(Http403, self).__init__(403)

class Http404(HttpError):
    """ Exception used to respond with a 404, instead of a success and data """
    def __init__(self):
        super(Http404, self).__init__(404)

class Http405(HttpError):
    """ Exception used to respond with a 405, instead of a success and data """
    def __init__(self):
        super(Http405, self).__init__(405)

class ResponseStartedError(Exception):
    """ Exceptions used to indicate that a response has already been started
        (response code, and possible headers, have already been written to the stream)
    """
    def __init__(self):
        super("Response already in progress")
