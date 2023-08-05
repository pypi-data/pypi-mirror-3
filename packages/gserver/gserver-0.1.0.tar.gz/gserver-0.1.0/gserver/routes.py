"""
	routes.py: Maintains routes, and their corresponding handlers,
			   for a `gserver` instance
"""

import re

from content_types import *

class Routes:
	"""Route, and handler, container used for a `gserver`"""
	def __init__(self):
		self._routes = {}
	
	def route(self, path, method='GET', content_type=TEXT.HTML):
		""" DECORATOR - Decorates a function as a route handler.

		Args:
			path:		The regex string used to match against requests
		Returns:		A decorator function
		"""
		regex = re.compile(path)

		def decorator(handler):
			def wrapper(env, resp, **kwargs):
				if kwargs:
					return handler(env, resp, **kwargs)
				else:
					return handler(env, resp)

			self._routes[regex] = wrapper	# Add the route to the collection
			wrapper.method = method
			wrapper.methods = method.split(',')
			wrapper.content_type = content_type

			return wrapper
		return decorator

	def route_json(self, path, method='GET'):
		return self.route(path, method=method, content_type=APPLICATION.JSON)

	def route_xml(self, path, method='GET'):
		return self.route(path, method=method, content_type=TEXT.XML)
	
	def get(self, path):
		"""Retrives a route matching the given path"""
		handler = None
		handler_args = None

		for key in self._routes.iterkeys():
			match = key.match(path)
			if match:
				handler_args = match.groupdict()
				handler = self._routes[key]
				break

		return handler, handler_args
