import unittest
import doctest

from zope import interface
from zope import component
from zope.component import testing

from horae.core.interfaces import IWorkdays


class Workdays(object):
    interface.implements(IWorkdays)

    def workdays(self):
        return range(0, 6)


def timeawareSetUp(doctest):
    testing.setUp(doctest)
    component.provideUtility(Workdays(), IWorkdays)


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'timeaware.txt',
            setUp=timeawareSetUp, tearDown=testing.tearDown,
            ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
