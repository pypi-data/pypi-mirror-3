#
# Example PloneTestCase
#


from Acquisition import aq_base
from Products.BastionLedger.tests.LedgerTestCase import LedgerTestCase, portal_name, \
     ledger_name, ledger_products


class TestLedgerTestCase(LedgerTestCase):
    '''
    Verify that our test harness is working
    '''

    def testPortalCreated(self):
        self.failUnless(hasattr(aq_base(self.app), portal_name))

    def testLedgerCreated(self):
        self.failUnless(hasattr(aq_base(self.portal), ledger_name))

    def testWorkflowToolCreated(self):
        """
        hmmm - workflow tool disappeared ...
        """
        self.failUnless(getattr(self.portal, 'portal_workflow', False))

    def testQuickInstalled(self):
        installed = map(lambda x: x['id'],
                        self.portal.portal_quickinstaller.listInstalledProducts())
        for product in ledger_products:
            self.failUnless(product in installed)



def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestLedgerTestCase))
    return suite

