from Products.PloneTestCase.PloneTestCase import PloneTestCase
from zope.testing import doctestunit
from zope.component import testing, getMultiAdapter
from Testing import ZopeTestCase as ztc
from cStringIO import StringIO
import zope.app.publisher.browser
from Products.Five.testbrowser import Browser
from base import NorthStarTestCase
from zope.publisher.browser import TestRequest
from uwosh.northstar.actions import MailerAction


class TestActions(NorthStarTestCase):
    """
    """

    def test_mailer_action_parses_to(self):
        pass


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestActions))
    
    return suite