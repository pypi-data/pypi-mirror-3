"""Test setup for integration and functional tests.

When we import PloneTestCase and then call setupPloneSite(), all of
Plone's products are loaded, and a Plone site will be created. This
happens at module level, which makes it faster to run each test, but
slows down test runner startup.
"""
from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

from zope.interface import alsoProvides

from monet.mapsviewlet.interfaces import IMonetMapsLayer

@onsetup
def setup_product():
    """Set up the package and its dependencies.

    The @onsetup decorator causes the execution of this body to be
    deferred until the setup of the Plone site testing layer. We could
    have created our own layer, but this is the easiest way for Plone
    integration tests.
    """

    # Load the ZCML configuration for the example.tests package.
    # This can of course use <include /> to include other packages.

    fiveconfigure.debug_mode = True
    import Products.Maps
    import monet.mapsviewlet
    zcml.load_config('configure.zcml', Products.Maps)
    zcml.load_config('configure.zcml', monet.mapsviewlet)
    fiveconfigure.debug_mode = False

    # We need to tell the testing framework that these products
    # should be available. This can't happen until after we have loaded
    # the ZCML. Thus, we do it here. Note the use of installPackage()
    # instead of installProduct().
    # This is *only* necessary for packages outside the Products.*
    # namespace which are also declared as Zope 2 products, using
    # <five:registerPackage /> in ZCML.

    # We may also need to load dependencies, e.g.:
    #   ztc.installPackage('borg.localrole')

    ztc.installProduct('Maps')
    ztc.installPackage('monet.mapsviewlet')

# The order here is important: We first call the (deferred) function
# which installs the products we need for this product. Then, we let
# PloneTestCase set up this product on installation.

setup_product()
ptc.setupPloneSite(products=['monet.mapsviewlet','Products.Maps'])

class TestCase(ptc.PloneTestCase):
    """We use this base class for all the tests in this package. If
    necessary, we can put common utility or setup code in here. This
    applies to unit test cases.
    """


class FunctionalTestCase(ptc.FunctionalTestCase):
    """We use this class for functional integration tests that use
    doctest syntax. Again, we can put basic common utility or setup
    code in here.
    """

#    def setUp(self):
#        super(FunctionalTestCase, self).setUp()
#        from zope.component import provideAdapter
#        from plone.app.layout.globals.portal import PortalState
#        from zope.interface import Interface
#        provideAdapter(PortalState, adapts=(Interface, Interface),
#                       provides=Interface, name="plone_portal_state")

    def afterSetUp(self):
        
        self.portal.portal_membership.addMember('contributor1',
                                                'secret',
                                                ('Member', 'Contributor', 'Reviewer'), [])
        self.portal.portal_membership.addMember('contributor2',
                                                'secret',
                                                ('Member', 'Contributor', 'Reviewer'), [])
        self.portal.portal_membership.addMember('contributor',
                                                'secret',
                                                ('Member', 'Editor'), [])
        self.logout()
        alsoProvides(self.portal.REQUEST, IMonetMapsLayer)
        self.request = self.portal.REQUEST

    def goTo(self, context):
        self.request.set('ACTUAL_URL', context.absolute_url())
        #self.request.set('VIRTUAL_URL', '')
        #self.request.set('URL', '')


    def createPage(self, name):
        self.portal.invokeFactory(id=name, type_name='Document')
        page = self.portal[name]
        self.portal.portal_workflow.doActionFor(page, 'publish')
        return page

    def getMember(self):
        return self.portal.portal_membership.getAuthenticatedMember()


