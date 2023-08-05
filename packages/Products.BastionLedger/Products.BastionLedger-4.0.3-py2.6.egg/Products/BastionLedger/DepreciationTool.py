#
#    Copyright (C) 2008-20111  Corporation of Balclutha. All rights Reserved.
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

from Acquisition import aq_parent, aq_inner, aq_base
from Products.CMFCore.ActionInformation import ActionInformation
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.permissions import View

from AccessControl.class_init import InitializeClass

from OFS.PropertyManager import PropertyManager
from OFS.SimpleItem import SimpleItem

from zope.interface import implements

from Products.BastionBanking.ZCurrency import ZCurrency

from Permissions import OperateBastionLedgers
from interfaces.tools import IBLControllerTool

def manage_addDepreciationTool(self, id='depreciation_tool', REQUEST=None):
    """
    """
    self._setObject(id, DepreciationTool())
    if REQUEST:
        REQUEST.RESPONSE.redirect('%s/%s/manage_main' % (REQUEST['URL3'], id))
        
class DepreciationTool(UniqueObject, PropertyManager, SimpleItem, ActionProviderBase):
    """
    Jurisdictionalised depreciation methods and their supporting calculators
    """
    implements(IBLControllerTool)

    id = 'depreciation_tool'
    meta_type = 'DepreciationTool'

    portal_type = 'BLTool'

    icon = 'misc_/BastionLedger/blquill'
    
    __ac_permissions__ = PropertyManager.__ac_permissions__ + (
        (View, ('depreciation_methods',)),
	(OperateBastionLedgers, ('depreciationFunction', 'prime_costMethod',
                                 'diminishing_rateMethod')),
        ) + SimpleItem.__ac_permissions__ + ActionProviderBase.__ac_permissions__

    _actions = ()


    manage_options = ActionProviderBase.manage_options + \
                     PropertyManager.manage_options + \
                     SimpleItem.manage_options

    def __init__(self): pass

    def Description(self):
	return self.__doc__

    def depreciation_methods(self):
        """
        hmmm - these need to be backed up as jurisdiction-related policies calculable from the
        BLAsset data ...
        """
        return ['Diminishing Value', 'Prime Cost',]

    def depreciationFunction(self, method):
        """
        return the depreciation function for this method type
        """
        if method in ('Diminishing Value',):
            return self.diminishing_rateMethod
        elif method in ('Prime Cost',):
            return self.prime_costMethod
        raise NotImplementedError, method

    def prime_costMethod(self, asset, date_range):
        """
        prime cost depreciation - straight line
        """
        return self.diminishing_rateMethod(asset, date_range)


    def diminishing_rateMethod(self, asset, date_range, multiplier=1.0):
        """
        calculate diminishing rate depreciation based upon effective date
        """
        min_dt = min(date_range)
        max_dt = max(date_range)
        end_dt = asset.purchase_date + 365 * asset.effective_life

        if end_dt < min_dt or asset.purchase_date > max_dt:
            return ZCurrency('%s 0.00' % asset.purchase_price.currency())

        prorated_days = (max_dt - max(min_dt, asset.purchase_date)) / 365

        return asset.totalCost() * prorated_days * multiplier / asset.effective_life

InitializeClass(DepreciationTool)


