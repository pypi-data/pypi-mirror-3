import unittest, doctest

from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
ptc.setupPloneSite()
from base import Layer

import uwosh.northstar

optionflags = (doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS|doctest.REPORT_NDIFF)


def test_suite():
    suite = ztc.FunctionalDocFileSuite(
        'browser.txt',
        package='uwosh.northstar',
        optionflags=optionflags,
        test_class=ptc.FunctionalTestCase
    )
    suite.layer = Layer
    return suite
    

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
