import unittest
from zope.testing import doctest
from zope.app.testing import functional
from megrok.z3cform.base.tests import FunctionalLayer


def test_suite():
    readme = functional.FunctionalDocFileSuite(
        '../README.txt',
        optionflags=(doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE),
        )
    readme.layer = FunctionalLayer
    suite = unittest.TestSuite()
    suite.addTest(readme)
    return suite
