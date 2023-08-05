from Products.PloneTestCase.PloneTestCase import PloneTestCase
from zope.testing import doctestunit
from zope.component import testing, getMultiAdapter
from Testing import ZopeTestCase as ztc
from cStringIO import StringIO
import zope.app.publisher.browser
from Products.Five.testbrowser import Browser
from base import NorthStarTestCase
from zope.publisher.browser import TestRequest
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.interface import alsoProvides

class TestWorkflowActions(NorthStarTestCase):
    """
    """

    def test_adding_workflow(self):
        """
        pw = self.portal.portal_workflow
        req = TestRequest(form={
            'clone-from-workflow' : 'folder_workflow',
            'workflow-name' :  'new workflow',
            'form.actions.add' : 'True'
        })
        alsoProvides(req, IAttributeAnnotatable)
        
        view = getMultiAdapter((self.portal, req), name=u'northstar-add-new-workflow')
        view()
        
        self.failUnless('new-workflow' in self.pw.listWorkflows())"""
        pass

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestWorkflowActions))
    
    return suite