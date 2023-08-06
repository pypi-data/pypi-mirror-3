import unittest
import interlude
from zope.testing import doctest
from Testing import ZopeTestCase as ztc
from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
ptc.setupPloneSite(extension_profiles=['slc.autocategorize:default'],)

import slc.autocategorize

class TestCase(ptc.PloneTestCase):
    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            zcml.load_config('configure.zcml',
                             slc.autocategorize)
            fiveconfigure.debug_mode = False

        @classmethod
        def tearDown(cls):
            pass

optionflags = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS | 
               doctest.NORMALIZE_WHITESPACE
               )

def test_suite():
    return unittest.TestSuite([
        ztc.FunctionalDocFileSuite(
            'README.txt', 
            package='slc.autocategorize',
            test_class=TestCase, 
            globs=dict(interact=interlude.interact),
            optionflags=optionflags
            ),
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

