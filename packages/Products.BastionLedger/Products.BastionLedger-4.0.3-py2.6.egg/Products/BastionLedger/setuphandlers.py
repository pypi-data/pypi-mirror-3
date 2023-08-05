#
#    Copyright (C) 2002-2009  Corporation of Balclutha. All rights Reserved.
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#    AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#    IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
#    ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
#    LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
#    CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
#    GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
#    HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
#    LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
#    OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

import transaction, os
from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName

from Products.BastionLedger.CMFAccount import CMFAccount
from Products.BastionLedger import BLShareholderLedger

from DateTime import DateTime
from Products.BastionBanking.ZCurrency import ZCurrency



CURRENCY='GBP'


def install(context):                                       
    portal = context.getSite()

    bltool = getToolByName(portal, 'portal_bastionledger', None)

    # hmmm - getting called from uninstall steps ...
    if bltool is None:
        return

    # add some naf tax tables so nothing breaks ...
    addTT = bltool.manage_addProduct['BastionLedger'].manage_addBLTaxTable

    if not getattr(aq_base(bltool), 'company_tax', None):
        addTT('company_tax', 'Company Tax Rates')
        # say 30% corporate tax rate ...
        bltool.company_tax.manage_addProduct['BastionLedger'].manage_addBLTaxTableRecord(0.30, DateTime('1970/01/01'))
    if not getattr(aq_base(bltool), 'sales_tax', None):
        addTT('sales_tax', 'Sales Tax Rates')
        # say 10% sales tax rate ...
        bltool.sales_tax.manage_addProduct['BastionLedger'].manage_addBLTaxTableRecord(0.10, DateTime('1970/01/01'))
    # a bumbling tiered personal tax rate that unfortunately probably won't be the correct
    # currency ...
    if not getattr(aq_base(bltool), 'personal_tax', None):
        addTT('personal_tax', 'Personal Tax Rates',(('amount', 'CurrencyIndex', {'base_currency':CURRENCY}),))
        last_year = DateTime('%s/01/01' % DateTime().strftime('%Y'))
        addRate = bltool.personal_tax.manage_addProduct['BastionLedger'].manage_addBLTaxTableRecord
        addRate(0.1, last_year, amount=ZCurrency('%s 10,000.00' % CURRENCY))
        addRate(0.2, last_year, amount=ZCurrency('%s 20,000.00' % CURRENCY))
        addRate(0.3, last_year, amount=ZCurrency('%s 30,000.00' % CURRENCY))
        addRate(0.4, last_year, amount=ZCurrency('%s 40,000.00' % CURRENCY))

    # add our clonable ledger - but don't stomp on anything ...
    if not getattr(aq_base(bltool), 'Ledger', None):
        print 'BastionLedger: generating %s General' % CURRENCY
        bltool.manage_generateLedger(CURRENCY, "%s/charts/General.z" % os.path.dirname(__file__))
