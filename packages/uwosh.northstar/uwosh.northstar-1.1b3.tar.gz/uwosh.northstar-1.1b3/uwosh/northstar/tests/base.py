from Testing.ZopeTestCase import installPackage
from Products.Five import zcml, fiveconfigure
from collective.testcaselayer.ptc import BasePTCLayer, ptc_layer
from StringIO import StringIO
from os.path import dirname, join
from PIL import Image
from Products.PloneTestCase import ptc
from Products.CMFCore.utils import getToolByName


class Layer(BasePTCLayer):
    """ basic layer for integration tests """

    def afterSetUp(self):
        # load zcml...
        fiveconfigure.debug_mode = True
        import uwosh.northstar
        zcml.load_config('configure.zcml', package=uwosh.northstar)
        # initialize packages...
        installPackage('uwosh.northstar', quiet=True)
        installPackage('plone.app.jquerytools', quiet=True)
        # quick-install...
        self.addProfile('plone.app.jquerytools:default')
        self.addProfile('uwosh.northstar:default')



ptc.setupPloneSite()
ptc.utils.setupCoreSessions()

class NorthStarTestCase(ptc.PloneTestCase):
    """ base class for integration tests """

    layer = Layer(bases=[ptc_layer])

    def afterSetUp(self):
        self.setRoles(('Manager',))