import unittest
import sys
from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite

from Products.PloneTestCase.layer import onsetup


@onsetup
def setup_product():
    """
    Set up the package and its dependencies.
    """
    
    fiveconfigure.debug_mode = True
    import collective.phantasy
    zcml.load_config('configure.zcml', collective.phantasy)
    fiveconfigure.debug_mode = False    
    ztc.installProduct('SmartColorWidget')
    ztc.installPackage('collective.phantasy')    

setup_product()
ptc.setupPloneSite()


class TestCase(ptc.FunctionalTestCase):
    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            # doctests don't play nicely with ipython
            try :
                iphook = sys.displayhook
                sys.displayhook = sys.__displayhook__
            except:
                pass   

        @classmethod
        def tearDown(cls):
            pass




    
def test_suite():
    return unittest.TestSuite([
    
        doctestunit.DocTestSuite(
           module='collective.phantasy.atphantasy.content.skin',
           setUp=testing.setUp, tearDown=testing.tearDown),    
        # Integration tests
        ztc.FunctionalDocFileSuite(
            'integration.txt', package='collective.phantasy',
            test_class=TestCase),

        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
