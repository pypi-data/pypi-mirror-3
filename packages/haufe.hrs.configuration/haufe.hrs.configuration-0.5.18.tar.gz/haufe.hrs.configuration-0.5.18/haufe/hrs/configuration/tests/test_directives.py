#################################################################
# haufe.hrs.configuration - a pseudo-hierarchical configuration
# management infrastructure
# (C) 2008, Haufe Mediengruppe, Freiburg
#################################################################


"""
Test ZCML directives
"""

import os
import unittest

import zope.component
from zope.configuration import xmlconfig
from zope.component.testing import PlacelessSetup

from pkg_resources import resource_filename, get_provider

class DirectivesTest(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(DirectivesTest, self).setUp()
        provider = get_provider('haufe.hrs.configuration')
        os.environ['TESTING'] = '1'
        os.environ['PACKAGE_ROOT'] = provider.egg_root
        gsm = zope.component.getGlobalSiteManager()
        zcml = file(resource_filename('haufe.hrs.configuration', "tests/example.zcml")).read()
        self.context = xmlconfig.string(zcml)
        super(DirectivesTest, self).setUp()

    def tearDown(self):
        super(DirectivesTest, self).tearDown()
        del os.environ['TESTING']

    def testSimple(self):
        pass

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(DirectivesTest),
        ))

if __name__ == '__main__':
    unittest.main()
