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
from unittest import TestCase, TestSuite, makeSuite
from haufe.hrs.configuration import generateParser, OptionLookup
from haufe.hrs.configuration import util

dirname = os.path.dirname(os.path.abspath(__file__))

class ConfigurationTests(TestCase):

    def _generateParser(self, name):
        return generateParser(os.path.join(dirname, name))

    def testParseModel(self):
        parser = self._generateParser('model') 

    def testParseNonExistingModelDirectory(self):
        self.assertRaises(ValueError, generateParser, 'non-existing-model-dir')

    def testOptionLookupWithDefaults(self):
        parser = self._generateParser('model') 
        parser.add_file(os.path.join(dirname, 'empty-config.ini'))
        opts = parser.parse()
        OL = OptionLookup(opts)
        self.assertEqual(OL.get('cms.path'), '/foo/bar') 
        self.assertRaises(KeyError, OL.get, 'cms.checkout_path')
        self.assertEqual(OL.get('cms.port'), 42)

    def testOptionLookupWithConfigurationFile(self):
        parser = self._generateParser('model') 
        parser.add_file(os.path.join(dirname, 'example-config.ini'))
        opts = parser.parse()
        OL = OptionLookup(opts)
        self.assertEqual(OL.get('cms.path'), '/a/b/c') 
        self.assertEqual(OL.get('cms.checkout_path'), '/foo/bar')
        self.assertEqual(OL.get('cms.port'), 777)
        self.assertEqual(OL.get('cms.databases.db1'), 'n/a')

    def testOptionLookupWithConfigurationFileWithDomain(self):
        parser = self._generateParser('model') 
        parser.add_file(os.path.join(dirname, 'example-config.ini'))
        opts = parser.parse()
        OL = OptionLookup(opts, 'cms')
        self.assertEqual(OL.get('path'), '/a/b/c') 
        self.assertEqual(OL.get('checkout_path'), '/foo/bar')
        self.assertEqual(OL.get('port'), 777)
        self.assertEqual(OL.get('databases.db1'), 'n/a')
        self.assertEqual(OL.has('gibt.es.nicht'), False)

    def testOptionLookupWithConfigurationFileWithDomainAndFullName(self):
        parser = self._generateParser('model') 
        parser.add_file(os.path.join(dirname, 'example-config.ini'))
        opts = parser.parse()
        OL = OptionLookup(opts, 'cms')
        self.assertEqual(OL.get('cms.path'), '/a/b/c') 
        self.assertEqual(OL.get('cms.checkout_path'), '/foo/bar')
        self.assertEqual(OL.get('cms.port'), 777)
        self.assertEqual(OL.get('cms.databases.db1'), 'n/a')
        self.assertEqual(OL.has('cms.gibt.es.nicht'), False)


    def testOptionLookupWithNonExistingKeys(self):
        parser = self._generateParser('model') 
        parser.add_file(os.path.join(dirname, 'example-config.ini'))
        opts = parser.parse()
        OL = OptionLookup(opts)
        self.assertRaises(KeyError, OL.get,'gibt.es.nicht')

    def testWithConcurrentConfigurations(self):
        parser = self._generateParser('model') 
        # settings in -config2.ini must shadown the ones from -config.ini
        parser.add_file(os.path.join(dirname, 'example-config.ini'))
        parser.add_file(os.path.join(dirname, 'example-config2.ini'))
        opts = parser.parse()
        OL = OptionLookup(opts)
        self.assertEqual(OL.get('cms.path'), '/foo') 
        self.assertEqual(OL.get('cms.checkout_path'), '/bar')
        self.assertEqual(OL.get('cms.port'), 888)

    def testWithMixCaseKeys(self):
        parser = self._generateParser('model') 
        # settings in -config2.ini must shadown the ones from -config.ini
        parser.add_file(os.path.join(dirname, 'example-config3.ini'))
        opts = parser.parse()
        OL = OptionLookup(opts)
        self.assertEqual(OL.get('cms.Path'), '/foo') 
        self.assertEqual(OL.get('cms.CheckoutPath'), '/bar')

    def testWithMixCaseKeys(self):
        parser = self._generateParser('model') 
        # settings in -config2.ini must shadown the ones from -config.ini
        parser.add_file(os.path.join(dirname, 'example-config3.ini'))
        opts = parser.parse()
        OL = OptionLookup(opts)
        self.assertEqual(OL.get('cms.MixedCaseParameter'), 99) 
        self.assertEqual(OL.get('cms.Underscore_in_Parameter'), 'underscore') 


class UtilTests(TestCase):

    def testExpandFull(self):
        cwd = os.getcwd()
        self.assertEqual(util.expand_full('foo/bar'), os.path.join(cwd, 'foo/bar'))
        self.assertEqual(util.expand_full('/foo/bar'),  '/foo/bar')
        os.environ['FOO'] = '/tmp'
        self.assertEqual(util.expand_full('$FOO/foo/bar'),  '/tmp/foo/bar')




def test_suite():
    return TestSuite((
        makeSuite(ConfigurationTests),
        makeSuite(UtilTests),
        ))

if __name__ == '__main__':
    unittest.main()


