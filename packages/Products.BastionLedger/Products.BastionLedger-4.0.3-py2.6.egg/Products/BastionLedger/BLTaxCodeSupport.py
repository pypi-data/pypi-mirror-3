#
#    Copyright (C) 2009  Corporation of Balclutha. All rights Reserved.
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
import types
from Products.CMFCore.utils import getToolByName
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

class BLTaxCodeSupport:

    tax_codes = {}

    manage_taxcodes = PageTemplateFile('zpt/tax_codes', globals())

    def availableTaxTableIds(self):
        all = getToolByName(self, 'portal_bastionledger').objectIds('BLTaxTable')
        return filter(lambda x: x not in self.tax_codes.keys(), all)

    def availableTaxTables(self):
        all = getToolByName(self, 'portal_bastionledger').objectValues('BLTaxTable')
        return filter(lambda x: x.getId() not in self.tax_codes.keys(), all)
        
    def taxTable(self, id):
        return getToolByName(self, 'portal_bastionledger')._getOb(id)

    def allTaxCodes(self, table_id, effective=None):
        return self.taxTable(table_id).taxCodes(effective)
    
    def manage_delTaxGroups(self, ids=[], REQUEST=None):
        """
        """
        codes = dict(self.tax_codes)

        for id in ids:
            del codes[id]

        self.tax_codes = codes

        if REQUEST:
            REQUEST.set('management_view', 'Tax Groups')
            return self.manage_taxcodes(self, REQUEST)

    def manage_addTaxGroup(self, id, REQUEST=None):
        """
        """
        codes = dict(self.tax_codes)
        
        if not self.tax_codes.has_key(id):
            codes[id] = []

        self.tax_codes = codes
        
        if REQUEST:
            REQUEST.set('management_view', 'Tax Groups')
            return self.manage_taxcodes(self, REQUEST)

    def manage_addTaxCodes(self, id, codes, REQUEST=None):
        """
        """
        if not self.tax_codes.has_key(id):
            self.manage_addTaxGroup(id)

        if type(codes) == types.StringType:
            codes = [codes]

        for code in codes:
            if not code in self.tax_codes[id]:
                self.tax_codes[id].append(code)
        if REQUEST:
            REQUEST.set('management_view', 'Tax Groups')
            return self.manage_taxcodes(self, REQUEST)

    def manage_editTaxCodes(self, tax_codes={}, REQUEST=None):
        """
        """
        codes = {}
        for k in self.tax_codes.keys():
            codes[k] = tax_codes.get(k,[])
        self.tax_codes = codes
        if REQUEST:
            REQUEST.set('management_view', 'Tax Groups')
            return self.manage_taxcodes(self, REQUEST)

