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
