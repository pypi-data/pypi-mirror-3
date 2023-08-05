from Globals import package_home
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.tests.utils import MockMailHost
from Products.Five import fiveconfigure, zcml
from Products.MailHost.interfaces import IMailHost
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup
from Testing import ZopeTestCase as ztc
from cStringIO import StringIO
from zope.component._api import getUtility
from zope.interface.declarations import alsoProvides
import os


@onsetup
def setup_product():
    """Set up the package and its dependencies.

    The @onsetup decorator causes the execution of this body to be
    deferred until the setup of the Plone site testing layer. We could
    have created our own layer, but this is the easiest way for Plone
    integration tests.
    """

    fiveconfigure.debug_mode = True
    import Products.SimpleReference
    zcml.load_config('configure.zcml', Products.SimpleReference)
    fiveconfigure.debug_mode = False

    ztc.installPackage('Products.SimpleReference')


setup_product()
ztc.installProduct('RichDocument')
ptc.setupPloneSite(products=['Products.RichDocument',
                             'Products.SimpleReference'])


class TestBase:

    def write_file(self, contents):
        """debugging function to save a contents directly into a file"""
        fd = open(os.path.join(os.path.dirname(__file__),
                               'data', 'test.html'), 'w')
        fd.write(contents)
        fd.close()

    def get_error(self, idx=0):
        """Small helper function to get errors from errorlog"""
        return self.portal.error_log.getLogEntries()[idx]

    def patches(self):

        ztc.utils.setupCoreSessions(self.app)

        # Show every exception except redirects
        self.portal.error_log._ignored_exceptions = ('Redirect',)

        # Use MockMailHost
        mockhost = MockMailHost('MailHost')
        self.portal._delObject('MailHost')
        self.portal._setObject('MailHost', mockhost)

        sm = self.portal.getSiteManager()
        sm.registerUtility(mockhost, provided=IMailHost)

        # Be sure we use MockMailHost
        self.failUnless(isinstance(self.portal.MailHost, MockMailHost))
        self.failUnless(isinstance(getUtility(IMailHost), MockMailHost))
        self.failUnless(isinstance(getToolByName(self.portal, 'MailHost'),
                                   MockMailHost))

        self.portal.MailHost.reset()

    def read(self, name):
        path = os.path.join(package_home(globals()), 'data')
        data = None
        item = os.path.join(path, name)

        if os.path.isfile(item):
            fp = open(item, 'rb')
            data = StringIO(fp.read())
            fp.close()

        return data


class TestCase(ptc.PloneTestCase, TestBase):
    """We use this base class for all the tests in this package. If
    necessary, we can put common utility or setup code in here. This
    applies to unit test cases.
    """

    def afterSetUp(self):
        super(TestCase, self).afterSetUp()

        # Execute patches from TestBase
        self.patches()


class FunctionalTestCase(ptc.FunctionalTestCase, TestBase):
    """We use this class for functional integration tests that use
    doctest syntax. Again, we can put basic common utility or setup
    code in here.
    """

    def afterSetUp(self):
        # Execute patches from TestBase
        self.patches()

        roles = ('Member', 'Contributor')
        self.portal.portal_membership.addMember('contributor',
                                                'secret',
                                                roles, [])
