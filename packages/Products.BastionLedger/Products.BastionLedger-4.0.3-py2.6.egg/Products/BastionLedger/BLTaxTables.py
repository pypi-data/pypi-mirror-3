#
#    Copyright (C) 2008-2009  Corporation of Balclutha. All rights Reserved.
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
import AccessControl, types
from Products.ZCatalog.ZCatalog import ZCatalog, CatalogError
from AccessControl.Permissions import view, access_contents_information
from Permissions import OperateBastionLedgers, ManageBastionLedgers
from DateTime import DateTime
from BLBase import BSimpleItem, BObjectManagerTree, ProductsDictionary
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.BastionBanking.ZCurrency import ZCurrency
from interfaces.tools import IBLControllerToolMultiple

from zope.interface import Interface, implements

# hmmm ensure converters for form submission - if it's not in the list - it's a string ...
index_types = {
    'DateIndex': 'date',
    'TextIndex':'text',
    'CurrencyIndex':'currency'}

class ITaxTable(Interface): pass
class ITaxTableRecord(Interface): pass

manage_addBLTaxTableRecordForm = PageTemplateFile('zpt/add_taxtablerec', globals())
def manage_addBLTaxTableRecord(self, rate, effective, code='', id='', REQUEST=None, **kw):
    """
    kw is a hash of additional dimensional data
    """
    if not id:
        id = self.generateId()

    # assemble our info from variety of sources - allowing many possible
    # invokation sources and techniques ...
    fields = {}
    if kw:
        fields.update(kw)

    if REQUEST and REQUEST.has_key('kw'):
        fields.update(REQUEST.kw)

    # only pass the stuff we have indexes for - the rest is rubbish!!
    dimensions = {}
    for key in self.dimensions():
        if fields.has_key(key):
            dimensions[key] = kw[key]

    self._setObject(id, BLTaxTableRecord(id, rate, effective, code, **dimensions))
    if REQUEST:
        REQUEST.RESPONSE.redirect('%s/%s/manage_main' % (REQUEST['URL3'], id))
    return id

def addBLTaxTableRecord(self, id, title=''):
    """
    Plone-friendly ctor
    """
    return manage_addBLTaxTableRecord(self, 0.0, DateTime(), id=id)

class BLTaxTableRecord(BSimpleItem):
    """
    A Catalogable record about a (tax) rate
    """
    meta_type = portal_type = 'BLTaxTableRecord'

    implements(ITaxTableRecord)

    __ac_permissions__ = BSimpleItem.__ac_permissions__ + (
        (access_contents_information, ('fields', 'tax', 'extras', 'taxIncluded')),
        (ManageBastionLedgers, ('manage_edit',)),
        )

    manage_main = PageTemplateFile('zpt/view_taxtablerec', globals())

    manage_options = (
        {'label':'Edit', 'action':'manage_main'},
        ) + BSimpleItem.manage_options

    def __init__(self, id, rate, effective, code, **kw):
        self.id = id
        self.rate = rate
        self.effective = effective
        self.code = code
        for k,v in kw.items():
            setattr(self, k, v)

    def title(self):
        return '%s - %s' % (self.effective.strftime('%Y/%m/%d'), self.code or self.rate)

    Title = Description = title

    def indexObject(self):
        self.aq_parent.catalog_object(self, '/'.join(self.getPhysicalPath()))

    def unindexObject(self):
        self.aq_parent.uncatalog_object('/'.join(self.getPhysicalPath()))

    def fields(self):
        """
        returns a list of the field names in the record
        """
        return filter(lambda x: not x.startswith('_') and x not in ('id', 'at_references'),
                      self.__dict__.keys())

    def extras(self):
	"""
	return a list of the additional fieldnames (asides from code, effective, rate...)
	"""
	return filter(lambda x: x not in ('rate', 'effective', 'code', 'creators', 
                                          'portal_type', 'workflow_history', 'modification_date'), self.fields())
	
    def manage_edit(self, effective, rate, code, kw={}, REQUEST=None):
        """
        edit tax table record attributes
        """
        self.rate = float(rate)
        if not isinstance(effective, DateTime):
	    effective = DateTime(effective)
        self.effective = effective
        self.code = code
        for k,v in kw.items():
            setattr(self, k, v)
        self.unindexObject()
        self.indexObject()
        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Updated')
            return self.manage_main(self, REQUEST)

    def tax(self, amount):
        """
        calculate the tax due on the amount
        """
        if self.has_key('amount'):
            barrier = self.amount
            if amount < barrier:
                return ZCurrency(amount.currency, 0)
            return (amount - barrier) * self.rate
        return amount * self.rate

    def taxIncluded(self, amount):
        """
        calculate the tax included in an amount
        """
        rate = self.rate / (1.0 + self.rate)
        if self.has_key('amount'):
            barrier = self.amount
            if amount < barrier:
                return ZCurrency(amount.currency, 0)
            return (amount - barrier) * rate
        return amount * rate

    def __cmp__(self, other):
        if not isinstance(other, BLTaxTableRecord): return -1

        if self.effective > other.effective: return 1
        if self.effective < other.effective: return -1

        if self.code > other.code: return 1
        if self.code < other.code: return -1
        
        for field in filter(lambda x: x not in ('effective', 'code'), self.fields()):
            mine = getattr(self, field, None)
            theirs = getattr(other, field, None)
            
            if mine > theirs: return 1
            if mine < theirs: return -1

        return 0

    def manage_afterAdd(self, item, container):
        """ unreferenceable """
        pass

    def manage_beforeDelete(self, item, container):
        """
        """
        self.unindexObject()

AccessControl.class_init.InitializeClass(BLTaxTableRecord)

manage_addBLTaxTableForm = PageTemplateFile('zpt/add_taxtable', globals())
def manage_addBLTaxTable(self, id, title='', dimensions=(), REQUEST=None):
    """
    """
    self._setObject(id, BLTaxTable(id, title, dimensions))
    if REQUEST:
        REQUEST.RESPONSE.redirect('%s/%s/manage_main' % (REQUEST['URL3'], id))
    return id


class BLTaxTable(BObjectManagerTree, ZCatalog):
    """
    A multi-dimensional table - implemented/extended via
    ZCatalog indexes

    All records are guaranteed to at least have an 'effective'
    date field and auto-selection is done on this ...
    """
    meta_type = portal_type = 'BLTaxTable'

    implements(ITaxTable, IBLControllerToolMultiple)

    __ac_permissions__ = ZCatalog.__ac_permissions__ + (
        (access_contents_information, ('getRate', 'getTableRecords', 'taxCodes',
                                       'fields', 'dimensions', 'field_type')),
        (OperateBastionLedgers, ('calculateTax', 'taxAmount',)),
        )
    
    manage_options = ZCatalog.manage_options

    def __init__(self, id, title, dimensions=()):
        """
        dimensions is a list of indexes tuples suitable for addIndex ...
        """
        ZCatalog.__init__(self, id)
        BObjectManagerTree.__init__(self, id, title)
        self.addIndex('effective', 'DateIndex')
        for d in dimensions:
            if len(d) > 2:
                self.addIndex(d[0], d[1], extra=d[2])
            else:
                self.addIndex(d[0], d[1])
            
    def all_meta_types(self):
        return [ ProductsDictionary('BLTaxTableRecord') ]

    def getRate(self, effective=None, **kw):
        """
        returns the latest rate for the 
        """
        recs = self.getTableRecords(effective or DateTime(), kw=kw)
        if recs:
            return max(recs).rate
        raise KeyError, kw

    def getTableRecords(self, effective=None, **kw):
        """
        returns the table record block closest to the effective date(s)
        """
        if type(effective) in (types.TupleType, types.ListType):
            range = 'minmax'
        else:
            range = 'max'

        recs = map(lambda x: x._unrestrictedGetObject(),
                   self.searchResults(effective={'query':effective or DateTime(),
                                                 'range':range,},
                                      REQUEST=kw))
        # do a block-return (and not upsetting any catalog sort order)
        if recs:
            max_date = max(recs).effective
            recs = filter(lambda x: x.effective == max_date, recs)

        return recs

    def fields(self):
        """
        returns a list of the field names any BLTaxTableRate contained
        therein should have
        """
        return self.indexes()

    def dimensions(self):
        """
        return the other dimension names within this table
        """
        return filter(lambda x: x != 'effective', self.indexes())

    def field_type(self, field):
        """
        return the form type necessary to coerce the field from the form
        """
        try:
            return index_types.get(self._catalog.indexes[field].meta_type, 'string')
        except:
            raise KeyError, field

    def taxCodes(self, effective=None):
        """
        returns a list of the (unique) tax codes defined/supported by this table
        """
        if effective:
            recs = self.getTableRecords(effective)
        else:
            recs = self.objectValues('BLTaxTableRecord')

        results = []
        for rec in recs:
            code = rec.code
            if code and code not in results:
                results.append(code)
        return results

    def calculateTax(self, effective, amount):
        """
        compute (possibly tiered) tax for a date
        """
        try:
            tiers = self.getTableRecords(effective, sort_on='amount', sort_order='asc')
        except CatalogError:
            # oh well, it's not tiered ...
            recs = self.getTableRecords(effective)
            if recs:
                return recs[0].tax(amount)
            return ZCurrency('%s 0.00' % amount.currency())

        tax = ZCurrency('%s 0.00' % amount.currency())

        for i in range(0, len(tiers)):
            if i == len(tiers) - 1 or amount <= tiers[i+1].amount:
                tax += tiers[i].tax(amount)
            else:
                if i == 0:
                    diff = tiers[i].amount
                else:
                    diff = tiers[i].amount - tiers[i-1].amount
                tax += diff * tiers[i].rate
        
        return tax

    def taxAmount(self, effective, amount):
        """
        for a tax-inclusive amount, say what is the tax component
        """
        try:
            tiers = self.getTableRecords(effective, sort_on='amount', sort_order='asc')
        except CatalogError:
            # oh well, it's not tiered ...
            recs = self.getTableRecords(effective)
            if recs:
                return recs[0].taxIncluded(amount)
            return ZCurrency('%s 0.00' % amount.currency())

        tax = ZCurrency('%s 0.00' % amount.currency())

        for i in range(0, len(tiers)):
            if i == len(tiers) - 1 or amount <= tiers[i+1].amount:
                tax += abs(tiers[i].taxIncluded(amount))
            else:
                if i == 0:
                    diff = tiers[i].amount
                else:
                    diff = tiers[i].amount - tiers[i-1].amount
                tax += diff * (1.0 - 1.0 / (1.0 + tiers[i].rate))
        
        return tax

AccessControl.class_init.InitializeClass(BLTaxTable)


def addTaxTable(ob, event):
    """
    fix up catalogs on copy/paste
    """
    ob.ZopeFindAndApply(ob,
                        obj_metatypes=['BLTaxTableRec'],
                        search_sub=0,
                        apply_path='/'.join(ob.getPhysicalPath()),
                        apply_func=ob.catalog_object)
