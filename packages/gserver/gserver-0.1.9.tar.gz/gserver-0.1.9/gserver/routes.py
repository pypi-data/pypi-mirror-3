"""
    routes.py: Maintains routes, and their corresponding handlers,
               for a `gserver` instance
"""

import re

from content_types import *

'''________________________________Routes____________________________________'''

class Routes(object):
    """ Route, and handler, container used for a `gserver` """
    def __init__(self, setup_func=None):
        self._routes = {}
        self._setup_func = setup_func

    def setup_func(self, fn):
        """ Sets a function to be called prior to the route being invoked.
            Functions signature should be `fn(Request)` 

            (can be used to set things like a logged in user prior to invoking the route)
        """
        self._setup_func = fn
    
    def route(self, path, method='GET', content_type=TEXT.HTML, setup_func=None):
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

                if self._setup_func:
                    self._setup_func(req)
                if setup_func:
                    setup_func(req)

                if kwargs:
                    return handler(req, **kwargs)
                else:
                    return handler(req)

            self._routes[regex] = wrapper   # Add the route to the collection
            wrapper.method = method
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
