Changelog
=========

.. currentmodule:: gserver

Release 0.1a5
-------------

*BugFix*  - Broke the ``callback`` functionality, during JSON requests, with the 0.1a4 release

Release 0.1a4
-------------

*Feature* - Added ``exceptions.py`` so that you can throw errors from handlers.
            This is much like Djangos raise Http404.
            Currently only 404's are implemented.

            Added ``request.py`` to wrap gevents WSGI ``Environment`` and
            ``start_response`` variables and provide additional functionality
            (adding cookies, redirects..)

            Added more comments

Release 0.1a3
-------------

*Update* - Added a ``handler`` function to ``wsgi.py`` when all you need is just a handler
           another container, like Gunicorn, uWSGI, etc.
           Moved package info (__version__, etc., from ``wsgi.py`` to the package ``__init.py__``

Release 0.1a2
-------------

*Feature* - Added support for streaming. (specified when creating WSGI server)

Release 0.1a1
-------------

*Fixed* - If a regex group was optional (0 or more), and the argument was not
specified, the handler would receive the keyword as ``None``, overriding any default value
*Feature* - JSON routes can now return either a ``dict`` or ``string``

Release 0.1a0
-------------

Initial commit
