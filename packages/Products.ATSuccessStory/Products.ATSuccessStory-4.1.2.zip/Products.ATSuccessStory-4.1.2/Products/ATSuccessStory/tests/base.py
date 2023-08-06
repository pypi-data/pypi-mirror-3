"""Base testing infrastructure
"""

from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

from zope.schema.vocabulary import getVocabularyRegistry
from Products.ATSuccessStory.vocabularies import existingSSFolders

# These are traditional products (in the Products namespace). They'd
# normally be loaded automatically, but in tests we have to load them
# explicitly. This should happen at module level to make sure they are
# available early enough.

ztc.installProduct('ATSuccessStory')

@onsetup
def setup_atsuccessstory():
    """Set up the additional products required for the atsuccessstory product.

    The @onsetup decorator causes the execution of this body to be
    deferred until the setup of the Plone site testing layer.
    """

    # Load the ZCML configuration for the Products.ATSuccessStory package.
    # This includes the other products below as well.

    #fiveconfigure.debug_mode = True
    #import Products.ATSuccessStory
    #zcml.load_config('configure.zcml', Products.ATSuccessStory)
    #fiveconfigure.debug_mode = False
    #fiveconfigure.debug_mode = True
    #ztapi.provideUtility(IVocabulary, existingSSFolders, "atss.existing_folders")

    try:
        # Plone 3
        vr = getVocabularyRegistry()
        vr.register("atss.existing_folders", existingSSFolders)
    except:
        # Plone 4
        pass

    #self.portal.portal_quickinstaller.installProduct('ATSuccessStory')


# The order here is important: We first call the (deferred) function
# which installs the products we need for the Optilux package. Then, we
# let PloneTestCase set up this product on installation.

setup_atsuccessstory()
ptc.setupPloneSite(products=['ATSuccessStory'])

class ATSuccessStoryTestCase(ptc.PloneTestCase):
    """We use this base class for all the tests in this package. If
    necessary, we can put common utility or setup code in here.
    """

class ATSuccessStoryFunctionalTestCase(ptc.FunctionalTestCase):
    """We use this base class for all the tests in this package. If
    necessary, we can put common utility or setup code in here.
    """
