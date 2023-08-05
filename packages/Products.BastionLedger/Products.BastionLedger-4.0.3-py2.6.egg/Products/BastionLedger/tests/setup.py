#
# Copyright (C) 2007-2010  Corporation of Balclutha. All rights Reserved.
#
# Permission to use, copy, modify, and distribute this software
# and its documentation for any purpose whatsoever is strictly
# prohibited without prior written consent of Corporation of Balclutha.
# 
#
# Corporation of Balclutha DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS
# SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS, IN NO EVENT SHALL Corporation of Balclutha BE LIABLE FOR
# ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
# WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
# ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.
#
from DateTime import DateTime
from Testing import ZopeTestCase
from Products.PloneTestCase.setup import SiteSetup, SiteCleanup, \
     portal_name, default_policy, default_products, default_base_profile, \
     default_extension_profiles, portal_name, USELAYER

ledger_products = ('ZScheduler', 'BastionBanking', 'BastionLedger')

for product in ledger_products:
    ZopeTestCase.installProduct(product)


# optionally try to install this ...
for product in ('BastionCurrencyTool', 'AMCharts'):
    ZopeTestCase.installProduct(product)


ledger_name = 'ledger'
ledger_owner = 'portal_owner'
default_user = ZopeTestCase.user_name

# ensure we quick_install our stuff ...
default_products += ledger_products

from Products.BastionLedger.BLGlobals import EPOCH
from Products.BastionLedger.utils import ceiling_date

def setupLedgerSite(id=portal_name,
                    policy=default_policy,
                    products=default_products,
                    quiet=True,
                    with_default_memberarea=1,
                    base_profile=default_base_profile,
                    extension_profiles=default_extension_profiles):
    '''Creates a Plone site and/or quickinstalls products into it.'''
    if USELAYER:
        quiet = 1
        cleanupLedgerSite(id)
    LedgerSiteSetup(id,
                    policy=policy,
                    products=products,
                    quiet=quiet,
                    with_default_memberarea=with_default_memberarea,
                    base_profile=base_profile,
                    extension_profiles=extension_profiles).run()

if USELAYER:
    from Products.PloneTestCase import layer
    setupLedgerSite = layer.onsetup(setupLedgerSite)

def cleanupLedgerSite(id):
    '''Removes a site.'''
    LedgerSiteCleanup(id).run()

if USELAYER:
    from Products.PloneTestCase import layer
    cleanupLedgerSite = layer.onteardown(cleanupLedgerSite)

class LedgerSiteSetup(SiteSetup):
    """
    set up Plone then add an RPMBuilder ...
    """

    def _setupPloneSite(self):
        SiteSetup._setupPloneSite(self)
        portal = getattr(self.app, self.id)

        # hmmm - why aren't we being quickinstalled????
        qi = portal.portal_quickinstaller
        if not qi.isProductInstalled('BastionLedger'):
            qi.installProduct('BastionLedger')

        # add our ledger
        portal.manage_addProduct['BastionLedger'].manage_addLedger(ledger_name, 'test ledger', 'GBP')

        ledger = getattr(portal,ledger_name)
        
        # add optional ledger stuff
        ledger.manage_addProduct['BastionLedger'].manage_addBLQuoteManager('quotes')
        ledger.quotes._updateProperty('orderbooks', ['Receivables'])
        ledger.quotes._updateProperty('base_currency', 'GBP')

        # we've not publicly released BastionCurrencyTool...
        try:
            qi.installProduct('BastionCurrencyTool')
            ct = portal.portal_currencies
            ct.automagic=True
            ct.base='GBP'
            ct._addQuote('AUD', 0.0, 0.0, 0.4000, EPOCH)
            ct._addQuote('AUD', 0.0, 0.0, 0.4000, DateTime() - 0.5)
        except:
            print "No Multicurrency tests"

class LedgerSiteCleanup(SiteCleanup):
    """
    hmmm don't really need this - yet ...
    """
    def run(self):
        SiteCleanup.run(self)
