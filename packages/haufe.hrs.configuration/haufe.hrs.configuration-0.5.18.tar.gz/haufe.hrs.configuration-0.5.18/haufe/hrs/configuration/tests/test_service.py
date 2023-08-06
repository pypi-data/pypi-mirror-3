# -*- encoding: iso-8859-15 -*-

#################################################################
# haufe.hrs.configuration - a pseudo-hierarchical configuration
# management infrastructure
# (C) 2008, Haufe Mediengruppe, Freiburg
#################################################################


"""
Tests for haufe.hrs.configuration module
"""

import os
import unittest
from zope.interface.verify import verifyClass
from unittest import TestCase, TestSuite, makeSuite
from haufe.hrs.configuration.service import ConfigurationService
from haufe.hrs.configuration.interfaces import IConfigurationService
from haufe.hrs.configuration.util import DEFAULT_MARKER
from pkg_resources import resource_filename

class ServiceTests(TestCase):

    def _makeOne(self):
        return ConfigurationService(watch=False)

    def testVerifyInterface(self):
        verifyClass(IConfigurationService, ConfigurationService)

    def testService(self):
        service = self._makeOne()
        service.registerModel(resource_filename('haufe.hrs.configuration','tests/model/cms.ini'))
        service.registerModel(resource_filename('haufe.hrs.configuration','tests/model/toolbox.ini'))
        service.loadConfiguration(resource_filename('haufe.hrs.configuration','tests/example-config.ini'))

        self.assertEqual(service.get('path', 'cms'), '/a/b/c') 
        self.assertEqual(service.get('checkout_path', 'cms'), '/foo/bar')
        self.assertEqual(service.get('port', 'cms'), 777)
        self.assertEqual(service.get('databases.db1', 'cms'), 'n/a')

    def testGetConfiguration(self):
        service = self._makeOne()
        service.registerModel(resource_filename('haufe.hrs.configuration','tests/model/cms.ini'))
        service.registerModel(resource_filename('haufe.hrs.configuration','tests/model/toolbox.ini'))
        service.loadConfiguration(resource_filename('haufe.hrs.configuration','tests/example-config.ini'))
        got = service.getConfiguration()
        expected = {'cms.path' : '/a/b/c',
                    'cms.checkout_path' : '/foo/bar',
                    'cms.port' : 777,
                    'cms.databases.db1' : 'n/a',
                    'cms.databases.db2' : DEFAULT_MARKER,
                    'toolbox.active' : 0,
                    'cms.MixedCaseParameter' : 99,
                    'cms.Underscore_in_Parameter' : 'underscore',
                   }
        self.assertEqual(got, expected)

    def testGetConfigurationForDomain(self):
        service = self._makeOne()
        service.registerModel(resource_filename('haufe.hrs.configuration', 'tests/model/cms.ini'))
        service.registerModel(resource_filename('haufe.hrs.configuration', 'tests/model/toolbox.ini'))
        service.loadConfiguration(resource_filename('haufe.hrs.configuration', 'tests/example-config.ini'))
        got = service.getConfigurationForDomain('toolbox')
        expected = {'toolbox.active' : 0}
        self.assertEqual(got, expected)

    def testServiceAndReload(self):
        service = self._makeOne()
        service.registerModel(resource_filename('haufe.hrs.configuration', 'tests/model/cms.ini'))
        service.registerModel(resource_filename('haufe.hrs.configuration', 'tests/model/toolbox.ini'))
        service.loadConfiguration(resource_filename('haufe.hrs.configuration', 'tests/example-config.ini'))
        self.assertEqual(service.get('path', 'cms'), '/a/b/c')                
        service.reload()
        self.assertEqual(service.get('path', 'cms'), '/a/b/c') 

def test_suite():
    return TestSuite((
        makeSuite(ServiceTests),
        ))

if __name__ == '__main__':
    unittest.main()


