# base test case classes
from Testing import ZopeTestCase
from Products.PloneTestCase import PloneTestCase

# These must install cleanly, ZopeTestCase will take care of the others
ZopeTestCase.installProduct('PressRoom')

# Set up the Plone site used for the test fixture. The PRODUCTS are the products
# to install in the Plone site (as opposed to the products defined above, which
# are all products available to Zope in the test fixture)
PRODUCTS = ['PressRoom',]

PloneTestCase.setupPloneSite(products=PRODUCTS)

class PressRoomTestCase(PloneTestCase.PloneTestCase):
    """Base class for integration tests for PressRoom. This may
    provide specific set-up and tear-down operations, or provide convenience
    methods.
    """
