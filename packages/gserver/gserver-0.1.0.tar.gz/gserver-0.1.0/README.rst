gserver 0.1.0
=============

Simple wrapper around `gevent`_ that provides a basic routing engine
and JSON/JSONP handling.

Here's a simple usage example::

	from gserver import Routes
	from gserver.wsgi import WSGIServer, parse_vals

	routes = Routes()
	route = routes.route
	route_json = routes.route_json

	@route('^/example/$')
	def example(env, resp):
		return "hello"

	@route_json('^/example/(?P<name>\w+)/$', method='GET,POST')
	def example_name(env, resp, name=None):
		query_age, query_height = parse_vals(env, 'age', 'height')

		return { 'name': name,
				 'age': query_age,
				 'height': query_height }

	if __name__ == "__main__":
		server = WSGIServer('', 9191, routes, log=None)
		server.serve_forever()


get gserver
===========

Install `gevent`_, and it's dependencies `greenlet`_ and `libevent`_

Download the latest release from `Python Package Index`_ 
or clone `the repository`_

More documentation is on it's way *(check the* `site`_ *for updates)*

Provide any feedback and issues on the `bug tracker`_, that should be coming soon.


.. _gevent: http://www.gevent.org
.. _greenlet: http://codespeak.net/py/0.9.2/greenlet.html
.. _libevent: http://monkey.org/~provos/libevent/
.. _site: https://bitbucket.org/juztin/gserver
.. _the repository: https://bitbucket.org/juztin/gserver
.. _bug tracker: https://bitbucket.org/juztin/gserver
.. _Python Package Index: http://pypi.python.org/pypi/gserver
