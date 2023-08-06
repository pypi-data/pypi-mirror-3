"""
    wsgi.py: Wrapper around gevent.pywsgi
    
    Provides a WSGI JSON searching service for products.

    This service can be run behind a WSGI compliant server
        (preferably Nginx, or Apache).

    Alternatively, though not recommended, it can also be deployed
    behind IIS using the following:
        http://code.google.com/p/isapi-wsgi/
"""

from BaseHTTPServer import BaseHTTPRequestHandler
from datetime import datetime
from traceback import print_exc
from sys import stderr, stdout, exc_info
from types import GeneratorType
try:
    from ujson import encode as json_dumps
except ImportError:
    from json import dumps as json_dumps

from gevent.pywsgi import WSGIServer as pywsgi_server
from gevent.wsgi import WSGIServer as wsgi_server
#from gevent.pool import Pool

from . content_types import *
from . request import Request
from . exceptions import HttpError, ResponseStartedError

'''________________________________helpers___________________________________'''

def _body_wrap(content_type):
    def normal(data):
        return data
    def json(data):
        j_data, e = get_json(data)
        if e: log_error(e)
        return j_data

    if content_type is APPLICATION.JSON:
        return json
    else:
        return normal

def _err():
    err = None
    info = exc_info()
    if info and len(info) > 1:
        err = info[1]
    return err
    
def _poll(req, content_type, body):
    fn = _body_wrap(content_type)
    first = ''
    
    # need to pull the first result to catch any headers that have been set
    try: first = fn(body.next())
    except:
        log_error(_err())
        req.start_response(code=500)
    else:
        req.start_response()
        yield first

        for b in body:
            try:    yield fn(b)
            except: log_error(_err())

def log_error(err):
    """ Logs the given exception, and it's corresponding stacktrace """
    # TODO(jwilson): Implement logging to output to a real location
    #                OR if using *nix just redirect stderr to desired location
    #                and nothing below needs to change.
    stderr.write('[Error] - %s\n'% (err,))
    print_exc(6)

def get_json(body, callback=None):
    """ Converts the `body` to JSON, except when `body` is a str and returns the
        result, wrapping it in the callback when provided.
    """
    result, err = '', None

    try:
        if isinstance(body, str):
            result = body
        else:
            result = json_dumps(body)
    except TypeError, e:
        err = e
    else:
        if callback:
            result = "{0}({1})".format(callback[0], result)

    return result, err

def error_handler(req, code, err=None, content_type=TEXT.HTML):
    """ Handler used to log the given exception, if given, and return
        an error message to be sent to the response.
    """

    if err is not None:
        log_error(err)

    req.start_response(code=code)

    if content_type == APPLICATION.JSON:
        return '{{ "error": {0} }}'.format(code)
    else:
        return 'error: {0}'.format(code)

def handle_route(req, route, kwargs):
    """ Handler used to process routes.
        Supports: Yielding (polling) of routes
                  JSON dumping when `Content-Type` is JSON
                  gevent Queues
    """

    try:
        body = route(req, **kwargs)
    except ResponseStartedError, err:
        log_error(err)
    except HttpError, err:
        return error_handler(req, err.code, None, route.content_type)
    except:
        return error_handler(req, 500, _err(), route.content_type)
    else:
        if isinstance(body, GeneratorType):
            return _poll(req, route.content_type, body)
        elif route.content_type is APPLICATION.JSON:
            body, err = get_json(body, req.callback)# get content
            if err:                                 # error immediatly
                return error_handler(req, 500, err, route.content_type)

        req.start_response()
        return body

def get_handler(routes):
    """ Gets a WSGI compatible handler """
    def handler(env, resp):
        path = env.get('PATH_INFO')
        method = env.get('REQUEST_METHOD')
        route, kwargs = routes.get(path)
        req = Request(env, resp)

        if not route:
            return error_handler(req, 404)
        elif method != route.method and method not in route.methods:
            return error_handler(req, 501, content_type=route.content_type)
        else:
            return handle_route(req, route, kwargs)
    return handler

'''________________________________server____________________________________'''

class WSGIServer:
    def __init__(self, addr, routes, **kwargs):
        """ Creates a new WSGIServer using either the gevent underlying wsgi/pywsgi.
            
            When passing in the argument `enable_streaming` the gevent pywsgi
            server is created, to enable polling. Otherwise the faster
            libevent-http is used.
            (*libevent does not support SSL, streaming or pipelining*)
        """
        self._routes = routes
        self._port = addr[1]
        self._addr = addr[0] if addr[0] else '127.0.0.1'

        if kwargs.pop('enable_streaming', False):
            wsgi = pywsgi_server
        else:
            wsgi = wsgi_server

        self._server = wsgi(addr, get_handler(routes), **kwargs)
    
    def _print_start_msg(self):
        print('[gserver] {0} - listening on {1}:{2}'
                .format(datetime.today(), self._addr, self._port))

    def start(self):
        """ Starts serving """
        self._print_start_msg()
        self._server.start()

    def stop(self):
        """ Stops serving """
        self._server.stop()

    def serve_forever(self):
        """ Listens for incoming requests """
        self._print_start_msg()
        self._server.serve_forever()

