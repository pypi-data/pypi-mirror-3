""":mod:`irclog.version` --- Version info
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

#: (:class:`tuple`) The version numbers in tuple e.g. ``(1, 2, 3)``.
VERSION_INFO = (0, 2, 0)

#: (:class:`basestring`) The version string e.g. ``'1.2.3'``.
VERSION = '.'.join(str(v) for v in VERSION_INFO)

