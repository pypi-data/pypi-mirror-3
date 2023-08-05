# Define a common PloneTemplatesTestCase base class for use in all

from Products.PloneTestCase import PloneTestCase

# These must install cleanly
PloneTestCase.installProduct('PloneTemplates')

# Set up the Plone site used for the test fixture. The PRODUCTS are the products
# to install in the Plone site (as opposed to the products defined above, which
#  are all products available to Zope in the test fixture)
PRODUCTS = ['PloneTemplates']
PloneTestCase.setupPloneSite(products=PRODUCTS)


class PloneTemplatesTestCase(PloneTestCase.PloneTestCase):
    """Standard test case."""

