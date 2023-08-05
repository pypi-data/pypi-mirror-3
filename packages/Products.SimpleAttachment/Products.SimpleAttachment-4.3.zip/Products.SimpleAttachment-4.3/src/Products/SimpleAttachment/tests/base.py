from Products.PloneTestCase import ptc
from Products.Five import zcml, fiveconfigure
from Products.Five.testbrowser import Browser
from collective.testcaselayer.ptc import BasePTCLayer, ptc_layer


ptc.installProduct('SimpleAttachment', quiet=True)
ptc.installProduct('RichDocument', quiet=True)
ptc.setupPloneSite(products=['SimpleAttachment', 'RichDocument'])


class Layer(BasePTCLayer):
    """ basic layer for testing """

    def afterSetUp(self):
        # load zcml for this package...
        fiveconfigure.debug_mode = True
        from Products import SimpleAttachment
        zcml.load_config('configure.zcml', package=SimpleAttachment)
        fiveconfigure.debug_mode = False

layer = Layer(bases=[ptc_layer])


class IntegrationTestCase(ptc.PloneTestCase):
    """ base class for integration tests """

    layer = layer


class FunctionalTestCase(ptc.FunctionalTestCase):
    """ base class for functional tests """

    layer = layer

    def getBrowser(self, loggedIn=True):
        """ instantiate and return a testbrowser for convenience """
        browser = Browser()
        if loggedIn:
            user = ptc.default_user
            pwd = ptc.default_password
            browser.addHeader('Authorization', 'Basic %s:%s' % (user, pwd))
        return browser
