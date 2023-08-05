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
from collections import namedtuple
from urlparse import parse_qs
from datetime import datetime
from traceback import print_exc
from sys import stderr, stdout, exc_info
import json

#from gevent.pywsgi import WSGIServer as gWSGIServer
from gevent.wsgi import WSGIServer as gWSGIServer
from gevent.pool import Pool

from content_types import *

'''_______________________________variables__________________________________'''
__author__		= "Justin Wilson"
__copyright__	= "Copyright 2011, Justin Wilson"
__credits__		= ["Justin Wilson", "Eber Irigoyen", "Corey McKinnon"]
__license__		= "Simplified BSD License"
__version__		= "0.1.0"
__maintainer__	= "Justin Wilson"
__email__		= "justinwilson1 at gmail dot com"
__status__		= "Alpha"

status_codes = BaseHTTPRequestHandler.responses

'''________________________________helpers___________________________________'''
def log_error(err):
	'''Logs the given exception, and it's corresponding stacktrace'''
	# TODO(jwilson): Implement logging to output to a real location
	#				 OR if using *nix just redirect stderr to desired location
	#				 and nothing below needs to change.
	stderr.write('[Error] - %s\n'% (err,))
	print_exc(6)

def status(code):
	''' Get the HTTP status for the given code '''
	return "{0} {1}".format(code, status_codes[200][0])

def parse_qd(env):
	''' Parses either the query-string, or post data, and returns a dictionary
		of key/list
	'''
	method = env.get('REQUEST_METHOD')
	key = 'qs' if method == 'GET' else 'post_data'

	return env.get(key)

def parse_vals(env, *args):
	''' Parses either the query-string, or post data, and returns the
		values as a tuple
	'''
	data = parse_qd(env)
	default = [None,]

	return tuple([data.get(key, default)[0] for key in args])

def get_json(body, callback):
	''' Converts the body to JSON and returns the result, wrapping it in the
		callback when provided
	'''
	result, err = None, None

	try:
		result = json.dumps(body)
	except TypeError, e:
		err = e
	else:
		if callback:
			result = "{0}({1})".format(callback[0], result)

	return result, err

def error_handler(env, resp, code, exception=None, content_type=TEXT.HTML):
	''' Handler used to log the given exception, if given, and return
		an error message to be sent to the response.
	'''

	if exception is not None:
		log_error(exception)

	resp(status(code), content_type)

	if content_type == APPLICATION.JSON:
		return '{{ "error": {0} }}'.format(code)
	else:
		return 'error: {0}'.format(code)

def handle_route(env, resp, route, kwargs):
	body = None										# response body
	query_data = parse_qs(env.get('QUERY_STRING'))	# query string
	callback = query_data.pop('callback', None)		# callback values
	env['qs'] = query_data

	#if route.method == 'POST':
	if env.get('REQUEST_METHOD') == 'POST':
		form_vals = env['wsgi.input'].read()
		env['post_data'] = parse_qs(form_vals)

	try:
		if kwargs:
			body = route(env, resp, **kwargs)
		else:
			body = route(env, resp)
	except:
		e = exc_info()[1]
		return error_handler(env, resp, 500, e, route.content_type)

	if route.content_type == APPLICATION.JSON:
		body, err = get_json(body, callback)
		if err:
			return error_handler(env, resp, 500, err, APPLICATION.JSON)

	resp(status(200), route.content_type)
	return body

def _print_start_msg(addr, port):
	print('[gserver] {0} - listening on {1}:{2}'
			.format(datetime.today(), addr, port))

'''________________________________server____________________________________'''
class WSGIServer:
	def __init__(self, addr, port, routes, **kwargs):
		self._routes = routes
		self._port = port
		self._addr = addr if addr else '127.0.0.1'
		self._server = gWSGIServer( (addr, port),
									    self._app_handler,
									    **kwargs )
	
	def _print_start_msg(self):
		print('[gserver] {0} - listening on {1}:{2}'
				.format(datetime.today(), self._addr, self._port))

	def start(self):
		_print_start_msg(self._addr, self._port)
		self._server.start()

	def stop(self):
		_print_start_msg(self._addr, self._port)
		self._server.stop()

	def serve_forever(self):
		_print_start_msg(self._addr, self._port)
		self._server.serve_forever()
	
	def _app_handler(self, env, resp):
		path = env.get('PATH_INFO')
		method = env.get('REQUEST_METHOD')
		route, kwargs = self._routes.get(path)

		if not route:
			yield error_handler(env, resp, 404)
		elif method != route.method and method not in route.methods:
			yield error_handler(env, resp, 501, content_type=route.content_type)
		else:
			yield handle_route(env, resp, route, kwargs)
