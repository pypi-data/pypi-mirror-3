#
# To run the ZChecker on all skins in this instance type
#
#   $ python zcheck.py [-q]
#


import os, sys
from unittest import TestSuite, makeSuite

from zope import testrunner

# Suppress DeprecationWarnings, we really don't want any in these tests
import warnings
warnings.simplefilter('ignore', DeprecationWarning, append=1)

from Testing import ZopeTestCase
from Testing.ZopeTestCase import _print

ZopeTestCase.installProduct('PlacelessTranslationService')
ZopeTestCase.installProduct('ZChecker')

from Products.BastionLedger.tests import LedgerTestCase


class TestSkins(LedgerTestCase.LedgerTestCase):
    # Note: This looks like a unit test but isn't

    def afterSetUp(self):
        factory = self.portal.manage_addProduct['ZChecker']
        factory.manage_addZChecker('zchecker')
        self.verbose = not '-q' in sys.argv

    def testSkins(self):
        '''Runs the ZChecker on skins'''
        dirs = self.portal.portal_skins.objectValues()
        for dir in dirs:
            # filter out certain skin layers
            #print self._skinpath(dir)
            if self._skinpath(dir) in ['portal_skins/bastionledger']:
                results = self.portal.zchecker.checkObjects(dir.objectValues())
                for result in results:
                    self._report(result)
        if self.verbose:
            _print('\n')

    def testZMI(self):
	''' WAM trying this ...'''
	pass

    def _report(self, result):
        msg = result['msg']
        obj = result['obj']
        if msg:
            if self.verbose:
                _print('\n')
            _print('------\n%s\n' % self._skinpath(obj))
            for line in msg:
                _print('%s\n' % line)
        else:
            if self.verbose:
                _print('.')

    def _skinpath(self, obj):
        path = obj.absolute_url(1)
        path = path.split('/')
        return '/'.join(path[1:])

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestSkins))
    return suite

if __name__ == '__main__':
    sys.argv = ['test']
    testrunner.run_internal()
else:
    test_suite()
