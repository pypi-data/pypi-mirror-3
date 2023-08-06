from Testing import ZopeTestCase

# Let Zope know about the two products we require above-and-beyond a basic
# Plone install (PloneTestCase takes care of these).
ZopeTestCase.installProduct('Relations')
ZopeTestCase.installProduct('PloneOntology')

# Import PloneTestCase - this registers more products with Zope as a side effect
from Products.PloneTestCase.PloneTestCase import PloneTestCase
from Products.PloneTestCase.PloneTestCase import FunctionalTestCase
from Products.PloneTestCase.PloneTestCase import setupPloneSite

# Set up a Plone site, and apply the Relations and PloneOntology extension
# profiles to make sure they are installed.
setupPloneSite(products=('Relations', 'PloneOntology'))

class PloneOntologyTestCase(PloneTestCase):
    """Base class for integration tests for the 'PloneOntology' product.
    """

    def tearDown(self):
        self.portal.portal_classification._p_deactivate() # Drop _v_relcache
        super(PloneOntologyTestCase, self).tearDown()

class PloneOntologyFunctionalTestCase(FunctionalTestCase):
    """Base class for functional integration tests for the 'PloneOntology' product.
    """

    def tearDown(self):
        self.portal.portal_classification._p_deactivate() # Drop _v_relcache
        super(PloneOntologyFunctionalTestCase, self).tearDown()
