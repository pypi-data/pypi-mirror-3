"""
    routes.py: Maintains routes, and their corresponding handlers,
               for a `gserver` instance
"""

import re

from content_types import *

HTTP_METHODS = [ "OPTIONS", "GET", "HEAD", "POST", "PUT", "DELETE", "TRACE", "CONNECT" ]

'''________________________________Routes____________________________________'''

class Routes(object):
    """ Route, and handler, container used for a `gserver` """
    def __init__(self):
        self._routes = {}
        self._before_funcs = ()
        self._after_funcs = ()

    def before(self, fn):
        """ Sets a function to be called prior to the route being invoked.
            Functions signature should be `fn(Request)` 

            (can be used to set things like a logged in user prior to invoking the route)
        """
        self._before_funcs = (fn,) + self._before_funcs
    
    def after(self, fn):
        """ Sets a function to be called after the route being invoked.
            Functions signature should be `fn(Request)` 

            (can be used to set things like a logged in user prior to invoking the route)
        """
        self._after_funcs = (fn,) + self._after_funcs
    
    def route(self, path, method='GET', content_type=TEXT.HTML):
        """ DECORATOR - Decorates a function as a route handler.

        Args:
            path:       The regex string used to match against requests
        Returns:        A decorator function
        """
        regex = re.compile(path)

        def decorator(handler):
            def wrapper(req, **kwargs):
                if content_type is not None:
                    h, v = content_type
                    req.add_header(h, v)

                if self._before_funcs:
                    for fn in self._before_funcs:
                        fn(req)

                if kwargs:
                    resp = handler(req, **kwargs)
                else:
                    resp = handler(req)

                if self._after_funcs:
                    for fn in self._after_funcs:
                        fn(req)

                return resp

            self._routes[regex] = wrapper   # Add the route to the collection
            wrapper.method = method
            if method == "*":
                wrapper.methods = HTTP_METHODS
            else:
                wrapper.methods = method.split(',')
            wrapper.content_type = content_type

            return wrapper
        return decorator

    def route_json(self, path, method='GET'):
        """ Registers a route with `application-json` for the content-type """
        return self.route(path, method=method, content_type=APPLICATION.JSON)

    def route_xml(self, path, method='GET'):
        """ Registers a route with `text-xml` for the content-type """
        return self.route(path, method=method, content_type=TEXT.XML)
    
    def get(self, path):
        """ Retrives a route matching the given path """
        handler = None
        handler_args = None

        for key in self._routes.iterkeys():
            match = key.match(path)
            if match:
                handler_args = match.groupdict()                                                                         
                for k,v in handler_args.items():
                    if v is None: del handler_args[k]

                handler = self._routes[key]
                break

        return handler, handler_args
