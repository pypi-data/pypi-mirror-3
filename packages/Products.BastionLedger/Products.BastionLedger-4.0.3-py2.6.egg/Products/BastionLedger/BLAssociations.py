#
#    Copyright (C) 2008-2011  Corporation of Balclutha. All rights Reserved.
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
import AccessControl
from Products.ZCatalog.ZCatalog import ZCatalog
from AccessControl.Permissions import view, access_contents_information, \
     view_management_screens
from Permissions import ManageBastionLedgers
from DateTime import DateTime
from BLBase import BSimpleItem, BObjectManagerTree, ProductsDictionary
from OFS.PropertyManager import PropertyManager
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from zope.interface import Interface, implements

#
# these are the minimally sufficient set of associations for the standard
# system/workflows to interoperate
#
DEPRECIATIONS = ('accum_dep', 'dep_exp')
ORDERS = ('freight', 'part_cogs', 'part_inc', 'part_inv', 'payables', 'order_payments', 'receivables','sales_tax',)
SHAREHOLDERS = ('dividend', 'dividend_payable', 'shareholders',)
PAYROLL = ('super_exp', 'wages', 'wages_exp', 'wages_pmt', 'wages_super', 'wages_tax',)
CASHFLOW_STMT = ('int_inc', 'int_exp', 'div_inc', 'div_exp', 'loans') # these aren't compulsory
YEAR_END = ('profit_loss', 'retained_earnings', 'tax_accr', 'tax_exp')

ASSOCIATIONS = ('bank_account', ) + DEPRECIATIONS + ORDERS + SHAREHOLDERS + PAYROLL + YEAR_END

manage_addBLAssociationForm = PageTemplateFile('zpt/add_association', globals())
def manage_addBLAssociation(self, id, ledger, accno, title='', description='', REQUEST=None):
    """
    """
    self._setObject(id, BLAssociation(id, title, description, ledger, accno))
    if REQUEST:
        REQUEST.RESPONSE.redirect('%s/%s/manage_main' % (REQUEST['URL3'], id))
    return id

class IAssociation(Interface): pass

def addBLAssociation(self, id, title=''):
    """
    Plone ctor
    """
    manage_addBLAssociation(self, id, 'Ledger', '1000', title)

class BLAssociation(PropertyManager, BSimpleItem):
    """
    A Catalogable record about a (tax) rate
    """
    meta_type = portal_type = 'BLAssociation'

    implements(IAssociation)

    __ac_permissions__ = BSimpleItem.__ac_permissions__ + (
        (access_contents_information, ('accounts',)),
        ) + PropertyManager.__ac_permissions__

    _properties = PropertyManager._properties + (
        {'id':'description', 'type':'text',   'mode':'w'},
        {'id':'ledger',      'type':'string', 'mode':'w'},
        {'id':'accno',       'type':'lines',  'mode':'w'},
        )

    manage_options = PropertyManager.manage_options + BSimpleItem.manage_options

    def __init__(self, id, title, description, ledger, accno):
        self.id = id
        self.title = title
        self.description = description
        self.ledger = ledger
        self._updateProperty('accno', accno)

    def title(self):
        return '%s - %s' % (self.ledger, self.accno)

    def indexObject(self):
        self.aq_parent.catalog_object(self, '/'.join(self.getPhysicalPath()))

    def unindexObject(self):
        self.aq_parent.uncatalog_object('/'.join(self.getPhysicalPath()))

    def accounts(self, bastionledger):
        """
        return the list of accounts that satisfy the association in the bastionledger
        """
        return bastionledger._getOb(self.ledger).searchObjects(accno=self.accno)


AccessControl.class_init.InitializeClass(BLAssociation)


def manage_addBLAssociationsFolder(self,id='associations', REQUEST=None):
    """
    """
    self._setObject(id, BLAssociationsFolder(id))
    if REQUEST:
        REQUEST.RESPONSE.redirect('%s/%s/manage_main' % (REQUEST['URL3'], id))
    return id

class BLAssociationsFolder(BObjectManagerTree, ZCatalog):
    """
    Implicit links between account(s) and things we want/need to associate
    """
    meta_type = portal_type = 'BLAssociationFolder'

    title = 'Associations'

    __ac_permissions__ = BObjectManagerTree.__ac_permissions__ + (
        (access_contents_information, ('accounts',)),
        (view_management_screens, ('manage_verify',)),
        ) + ZCatalog.__ac_permissions__

    manage_options = ZCatalog.manage_options[0:2] + (
        {'label':'View',   'action':''},
        {'label':'Verify', 'action':'manage_verify'},
        ) + ZCatalog.manage_options[2:]

    def __init__(self, id):
        """
        dimensions is a list of indexes tuples suitable for addIndex ...
        """
        ZCatalog.__init__(self, id)
        BObjectManagerTree.__init__(self, id, self.title)
        self.addIndex('id', 'FieldIndex')
        self.addIndex('ledger', 'FieldIndex')
        self.addIndex('accno', 'KeywordIndex')
        self.addColumn('id')

    def all_meta_types(self):
        return [ ProductsDictionary('BLAssociation') ]

    def accounts(self, association, bastionledger):
        """
        """
        return self._getOb(association).accounts(bastionledger)

    def manage_verify(self, associations=None, REQUEST=None):
        """
        """
        missing = []
        exists = self.objectIds('BLAssociation')
        for needed in associations or ASSOCIATIONS:
            if needed not in exists:
                missing.append(needed)
        if REQUEST:
            if missing:
                REQUEST.set('manage_tabs_message','missing: %s' % ','.join(missing))
            else:
                REQUEST.set('manage_tabs_message', 'OK')
            return self.manage_main(self, REQUEST)
        if missing:
            raise AttributeError, ','.join(missing)

    def get(self, tag):
        try:
            return self._getOb(tag)
        except:
            return None

    def searchObjects(self, **kw):
        return map(lambda x: x.getObject(),
                   self.searchResults(**kw))
    
    def _repair(self):
        # TODO - upgrade accno index from FieldIndex to KeyWordIndex ...
        pass

AccessControl.class_init.InitializeClass(BLAssociationsFolder)


