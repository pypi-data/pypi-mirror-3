"""
    Request.py: Wrapper around gevent environment and start_response
    
"""

from BaseHTTPServer import BaseHTTPRequestHandler
from urlparse import parse_qs

from . content_types import *
from . exceptions import ResponseStartedError

'''_______________________________variables__________________________________'''


status_codes = BaseHTTPRequestHandler.responses

'''________________________________helpers___________________________________'''

def _headers(headers, cookies):
    result = []
    for k,v in headers.items():
        result.append((k, v))
    for c in cookies:
        result.append(("Set-Cookie", c))
    return result

def status(code):
    """ Get the HTTP status for the given code """ 
    return "{0} {1}".format(code, status_codes[200][0])

def parse_vals(data, *args):
    """ Parses either the query-string, or post data, and returns the
        values as a tuple
    """
    default = [None,]
    return tuple([data.get(key, default)[0] for key in args])

'''________________________________Request___________________________________'''

class Request(object):
    """ Wraps the WSGI/gevent `Environment` and `start_response`
        and add some common functionality
    """

    def __init__(self, env, resp):
        """ Initializes a new Request wrapper

        Args:
            env:        gevent `Environment` object
            resp:       gevent `start_response` function
        """
        self._resp = resp
        self._resp_started = False
        self._resp_code = None

        query_data      = parse_qs(env.get('QUERY_STRING')) # query string
        self.callback   = query_data.pop("callback") if "callback" in query_data else None
        self.query_data = query_data
        self.form_vals  = {}
        self.form_data  = {}
        self.method     = env.get('REQUEST_METHOD')

        if self.method == 'POST':
            self.form_vals  = env['wsgi.input'].read()
            self.form_data  = parse_qs(self.form_vals)

        self._headers   = {}
        self._cookies   = []
        self.env        = env

    def get(self, key):
        """ Returns an environment value for the given key

            (same as `environment.get(key)`
        """
        return self.env.get(key)

    def add(self, key, value):
        """ Adds/Sets an environment key|value
        
            (same as `environment[key] = value)
        """
        self.env[key] = value

    def header(self, key, value=None):
        """ Gets/Sets a header key/value

        Args:
            key:    The header to set
            value:  (optional) - The value for the header
        Returns:    None, when a value is provided, otherwise the value of the current header
        """
        result = None
        if value is None:
            if key in self._headers:
                result = self._headers[key]
        else:
            self._headers[key] = value

        return result

    def add_header(self, key, value):
        """ Adds a header for the response """
        return self.header(key, value)

    def add_cookie(self, key, value, path='/', expires=None, http_only=True, secure=False):
        """ Adds a `Set-Cookie` header to the response """
        cookie = "{0}={1}; Path={2}".format(key, value, path)
        if expires:
            cookie += "; Expires="+expires
        if http_only:
            cookie += "; HttpOnly"
        if secure:
            cookie += "; Secure"
        self._cookies.append(cookie)
    
    def redirect(self, url):
        """ Adds a `Location` header to the response and updates the status-code to 302 """
        self._resp_code = 302
        self.add_header("Location", url)

    def start_response(self, code=200):
        """ Starts the response:
            Writes status-code and headers

            Should only be called from gserver internally
        """
        if self._resp_started:
            raise ResponseStartedError()

        if self._resp_code:
            code = self._resp_code

        self._resp_started = True
        self._resp(status(code), _headers(self._headers, self._cookies))
