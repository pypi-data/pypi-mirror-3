""":mod:`irclog.tests` --- Unit tests
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. data:: MODULES

   The modules to test.

"""
import doctest
import unittest
import irclog.archive
import irclog.web


MODULES = irclog.archive, \
          irclog.web


def suite():
    """Adapts doctests to :mod:`unittest` interface.

    :returns: an adopted :class:`unittest.TestSuite` object

    """
    suite = unittest.TestSuite()
    for mod in MODULES:
        suite.addTest(doctest.DocTestSuite(mod))
    return suite

