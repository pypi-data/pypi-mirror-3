Changelog
=========

.. currentmodule:: gserver


Release 0.1a0
-------------

Initial commit

Release 0.1a1
-------------

*Fixed* - If a regex group was optional (0 or more), and the argument was not
specified, the handler would receive the keyword as ``None``, overriding any default value
*Feature* - JSON routes can now return either a ``dict`` or ``string``

Release 0.1a2
-------------

*Feature* - Added support for streaming. (specified when creating WSGI server)

Release 0.1a3
-------------

*Update* - Added a ``handler`` function to ``wsgi.py`` when all you need is just a handler
           another container, like Gunicorn, uWSGI, etc.
           Moved package info (__version__, etc., from ``wsgi.py`` to the package ``__init.py__``
