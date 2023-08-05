#
#    Copyright (C) 2002-2011  Corporation of Balclutha. All rights Reserved.
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

from App.ImageFile import ImageFile

import CMFAccount, BLInventory, Ledger, BLLedger, BLSubsidiaryLedger
import BLShareholderLedger, BLOrderBook
import BLPayroll
import BLEntry, BLAccount, BLSubsidiaryAccount, BLTransaction, BLSubsidiaryTransaction
import BLTransactionTemplate, BLEntryTemplate
import BLProcess, FSBLProcess, BLReport
import BLForecaster, BLAssetRegister, BLQuoteManager
import BLTaxTables, BLAssociations

from AccessControl.Permissions import view_management_screens

try:
    from Products.BastionHosting.Permissions import add_bastionframeworks
except:
    add_bastionframeworks = 'Add BastionFrameworks'

from Permissions import ManageBastionLedgers, OperateBastionLedgers, AddBastionLedgers

from Products.GenericSetup import EXTENSION
from Products.GenericSetup import profile_registry
from Products.CMFPlone.interfaces import IPloneSiteRoot



# plone stuff
from Products.CMFCore import utils as coreutils
from config import *

from utils import registerLedgerDirectory
registerLedgerDirectory(SKINS_DIR, GLOBALS)

import LedgerTool, AccountPropertiesTool, PeriodEndTool, DepreciationTool, \
    LedgerControllerTool

def initialize(context):
    context.registerClass(Ledger.Ledger,
                          constructors = (Ledger.manage_addLedgerForm,
                                          Ledger.manage_addLedger),
                          #visibility=None,
                          icon='www/bastionledger.gif',
                          permission=AddBastionLedgers,
                          )
    context.registerClass(BLLedger.BLLedger,
                          constructors = (BLLedger.manage_addBLLedgerForm,
                                          BLLedger.manage_addBLLedger,),
                          visibility=None,
                          icon='www/blledger.gif',
                          permission=ManageBastionLedgers,
                          )
    context.registerClass(BLOrderBook.BLOrderBook,
                          constructors = (BLOrderBook.manage_addBLOrderBookForm,
                                          BLOrderBook.manage_addBLOrderBook),
                          visibility=None,
                          icon='www/blorderbook.gif',
                          permission=ManageBastionLedgers,
                          )
    context.registerClass(BLOrderBook.BLOrderAccount,
                          constructors = (BLOrderBook.manage_addBLOrderAccountForm,
                                          BLOrderBook.manage_addBLOrderAccount),
                          visibility=None,
                          icon='www/blorderaccount.gif',
                          permission=OperateBastionLedgers,
                          )
    context.registerClass(BLOrderBook.BLOrderItem,
                          constructors = (BLOrderBook.manage_addBLOrderItemForm,
                                          BLOrderBook.manage_addBLOrderItem),
                          visibility=None,
                          icon='www/blpart.gif',
                          permission=OperateBastionLedgers,
                          )
    context.registerClass(BLOrderBook.BLOrder,
                          constructors = (BLOrderBook.manage_addBLOrderForm,
                                          BLOrderBook.manage_addBLOrder),
                          visibility=None,
                          icon='www/blorder.gif',
                          permission=OperateBastionLedgers,
                          )
    context.registerClass(BLOrderBook.BLCashBook,
                          constructors = (BLOrderBook.manage_addBLCashBookForm,
                                          BLOrderBook.manage_addBLCashBook),
                          visibility=None,
                          icon='www/blsubsidiaryledger.gif',
                          permission=OperateBastionLedgers,
                          )
    context.registerClass(BLOrderBook.BLCashOrder,
                          constructors = (BLOrderBook.manage_addBLCashOrderForm,
                                          BLOrderBook.manage_addBLCashOrder),
                          visibility=None,
                          icon='www/blorder.gif',
                          permission=OperateBastionLedgers,
                          )
    context.registerClass(BLAccount.BLAccount,
                          constructors = (BLAccount.manage_addBLAccountForm,
                                          BLAccount.manage_addBLAccount),
                          visibility=None,
                          icon='www/blaccount.gif',
                          permission=ManageBastionLedgers,
                          )
    context.registerClass(BLInventory.BLInventory,
                          constructors = (BLInventory.manage_addBLInventoryForm,
                                          BLInventory.manage_addBLInventory),
                          visibility=None,
                          icon='www/blinventory.gif',
                          permission=OperateBastionLedgers,
                          )
    context.registerClass(BLInventory.BLPart,
                          constructors = (BLInventory.manage_addBLPartForm,
                                          BLInventory.manage_addBLPart),
                          visibility=None,
                          icon='www/blpart.gif',
                          permission=OperateBastionLedgers,
                          )
    context.registerClass(BLInventory.BLPartFolder,
                          constructors = (BLInventory.manage_addBLPartFolderForm,
                                          BLInventory.manage_addBLPartFolder),
                          visibility=None,
                          icon='www/blinventory.gif',
                          permission=OperateBastionLedgers,
                          )
    context.registerClass(BLSubsidiaryLedger.BLSubsidiaryLedger,
                          constructors = (BLSubsidiaryLedger.manage_addBLSubsidiaryLedgerForm,
                                          BLSubsidiaryLedger.manage_addBLSubsidiaryLedger),
                          visibility=None,
                          icon='www/blsubsidiaryledger.gif',
                          permission=ManageBastionLedgers,
                          )
    context.registerClass(BLSubsidiaryAccount.BLSubsidiaryAccount,
                          constructors = (BLSubsidiaryAccount.manage_addBLSubsidiaryAccountForm,
                                          BLSubsidiaryAccount.manage_addBLSubsidiaryAccount),
                          visibility=None,
                          icon='www/blaccount.gif',
                          permission=OperateBastionLedgers,
                          )
    context.registerClass(BLTransactionTemplate.BLTransactionTemplate,
                          constructors = (BLTransactionTemplate.manage_addBLTransactionTemplateForm,
                                          BLTransactionTemplate.manage_addBLTransactionTemplate),
                          icon='www/bltransaction_tpl.gif',
                          visibility=None,
                          permission=OperateBastionLedgers,
                          )
    context.registerClass(BLTransaction.BLTransaction,
                          constructors = (BLTransaction.manage_addBLTransactionForm,
                                          BLTransaction.manage_addBLTransaction),
                          icon='www/bltransaction.gif',
                          visibility=None,
                          permission=OperateBastionLedgers,
                          )
    context.registerClass(BLSubsidiaryTransaction.BLSubsidiaryTransaction,
                          constructors = (BLSubsidiaryTransaction.manage_addBLSubsidiaryTransactionForm,
                                          BLSubsidiaryTransaction.manage_addBLSubsidiaryTransaction),
                          icon='www/bltransaction.gif',
                          visibility=None,
                          permission=OperateBastionLedgers,
                          )
    context.registerClass(BLEntry.BLEntry,
                          constructors = (BLEntry.manage_addBLEntryForm,
                                          BLEntry.manage_addBLEntry),
                          visibility=None,
                          icon='www/blentry.gif',
                          permission=OperateBastionLedgers,
                          )
    context.registerClass(BLSubsidiaryEntry.BLSubsidiaryEntry,
                          constructors = (BLSubsidiaryEntry.manage_addBLSubsidiaryEntryForm,
                                          BLSubsidiaryEntry.manage_addBLSubsidiaryEntry),
                          visibility=None,
                          icon='www/blentry.gif',
                          permission='Add BastionLedger Objects',
                          )
    context.registerClass(BLEntryTemplate.BLEntryTemplate,
                          constructors = (BLEntryTemplate.manage_addBLEntryTemplateForm,
                                          BLEntryTemplate.manage_addBLEntryTemplate),
                          visibility=None,
                          icon='www/entry_template.gif',
                          permission=OperateBastionLedgers,
                          )
    context.registerClass(BLPayroll.BLPayroll,
                          constructors = (BLPayroll.manage_addBLPayrollForm,
                                          BLPayroll.manage_addBLPayroll),
                          visibility=None,
                          icon='www/blpayroll.gif',
                          permission='Add BastionLedger Objects',
                          )
    context.registerClass(BLPayroll.BLTimesheet,
                          constructors = (BLPayroll.manage_addBLTimesheetForm,
                                          BLPayroll.manage_addBLTimesheet),
                          visibility=None,
                          icon='www/bltimesheet.gif',
                          permission=view_management_screens,
                          )
    context.registerClass(BLPayroll.BLTimesheetSlot,
                          constructors = (BLPayroll.manage_addBLTimesheetSlotForm,
                                          BLPayroll.manage_addBLTimesheetSlot),
                          visibility=None,
                          icon='www/timesheetslot.gif',
                          permission=OperateBastionLedgers,
                          )
    context.registerClass(BLPayroll.BLEmployee,
                          constructors = (BLPayroll.manage_addBLEmployeeForm,
                                          BLPayroll.manage_addBLEmployee),
                          visibility=None,
                          icon='www/blemployee.gif',
                          permission=OperateBastionLedgers,
                          )
    context.registerClass(BLPayroll.BLEmployeeEntryTemplate,
                          constructors = (BLPayroll.manage_addBLEmployeeEntryTemplateForm,
                                          BLPayroll.manage_addBLEmployeeEntryTemplate),
                          visibility=None,
                          icon='www/entry_template.gif',
                          permission=view_management_screens,
                          )
    context.registerClass(BLProcess.BLProcess,
                          constructors = (BLProcess.manage_addBLProcessForm,
                                          BLProcess.manage_addBLProcess),
                          visibility=None,
                          icon='www/blprocess.gif',
                          permission=ManageBastionLedgers,
                          )
    context.registerClass(BLShareholderLedger.BLAllocation,
                          constructors = (BLShareholderLedger.manage_addBLAllocationForm,
                                          BLShareholderLedger.manage_addBLAllocation),
                          visibility=None,
                          icon='www/blshare.gif',
                          permission=ManageBastionLedgers,
                          )
    context.registerClass(BLShareholderLedger.BLShareDefinition,
                          constructors = (BLShareholderLedger.manage_addBLShareDefinitionForm,
                                          BLShareholderLedger.manage_addBLShareDefinition),
                          visibility=None,
                          icon='www/blshare.gif',
                          permission=ManageBastionLedgers,
                          )
    context.registerClass(BLShareholderLedger.BLShareholder,
                          constructors = (BLShareholderLedger.manage_addBLShareholderForm,
                                          BLShareholderLedger.manage_addBLShareholder),
                          visibility=None,
                          icon='www/blshareholder.gif',
                          permission=OperateBastionLedgers,
                          )
    context.registerClass(BLShareholderLedger.BLShareholderLedger,
                          constructors = (BLShareholderLedger.manage_addBLShareholderLedgerForm,
                                          BLShareholderLedger.manage_addBLShareholderLedger),
                          visibility=None,
                          icon='www/blshareholderledger.gif',
                          permission=ManageBastionLedgers,
                          )
    context.registerClass(BLShareholderLedger.BLDividendAdvice,
                          constructors = (BLShareholderLedger.manage_addBLDividendAdvice,),
                          visibility=None,
                          icon='www/bldividendadvice.gif',
                          permission=ManageBastionLedgers,
                          )
    context.registerClass(CMFAccount.CMFAccount,
                          constructors = (CMFAccount.manage_addCMFAccountForm,
                                          CMFAccount.manage_addCMFAccount),
                          visibility=None,
                          icon='www/blaccount.gif',
                          permission=ManageBastionLedgers,
                          )
    context.registerClass(BLReport.BLReport,
                          constructors = (BLReport.manage_addBLReportForm,
                                          BLReport.manage_addBLReport),
                          visibility=None,
                          icon='www/blreport.gif',
                          permission=OperateBastionLedgers,
                          )
    context.registerClass(BLForecaster.BLForecaster,
                          constructors = (BLForecaster.manage_addBLForecaster,),
                          visibility=None,
                          icon='www/blforecaster.gif',
                          permission=ManageBastionLedgers,
                          )
    context.registerClass(BLForecaster.BLForecast,
                          constructors = (BLForecaster.manage_addBLForecastForm,
                                          BLForecaster.manage_addBLForecast),
                          visibility=None,
                          icon='www/forecast.gif',
                          permission=OperateBastionLedgers,
                          )
    context.registerClass(BLAssetRegister.BLAssetRegister,
                          constructors = (BLAssetRegister.manage_addBLAssetRegisterForm,
                                          BLAssetRegister.manage_addBLAssetRegister),
                          visibility=None,
                          icon='www/blassetregister.gif',
                          permission=ManageBastionLedgers,
                          )
    context.registerClass(BLAssetRegister.BLAsset,
                          constructors = (BLAssetRegister.manage_addBLAssetForm,
                                          BLAssetRegister.manage_addBLAsset),
                          visibility=None,
                          icon='www/blasset.gif',
                          permission=OperateBastionLedgers,
                          )
    context.registerClass(BLQuoteManager.BLQuoteManager,
                          constructors = (BLQuoteManager.manage_addBLQuoteManagerForm,
                                          BLQuoteManager.manage_addBLQuoteManager),
                          visibility=None,
                          icon='www/blquotemgr.gif',
                          permission=OperateBastionLedgers,
                          )
    context.registerClass(BLQuoteManager.BLQuote,
                          constructors = (BLQuoteManager.manage_addBLQuoteForm,
                                          BLQuoteManager.manage_addBLQuote),
                          visibility=None,
                          icon='www/blquote.gif',
                          permission=OperateBastionLedgers,
                          )

    context.registerClass(BLTaxTables.BLTaxTableRecord,
                          constructors = (BLTaxTables.manage_addBLTaxTableRecordForm,
                                          BLTaxTables.manage_addBLTaxTableRecord),
                          visibility=None,
                          icon='www/bltaxtablerec.gif',
                          permission=OperateBastionLedgers,
                          )
    context.registerClass(BLTaxTables.BLTaxTable,
                          constructors = (BLTaxTables.manage_addBLTaxTableForm,
                                          BLTaxTables.manage_addBLTaxTable),
                          visibility=None,
                          icon='www/bltaxtable.gif',
                          permission=OperateBastionLedgers,
                          )
    context.registerClass(BLAssociations.BLAssociation,
                          constructors = (BLAssociations.manage_addBLAssociationForm,
                                          BLAssociations.manage_addBLAssociation),
                          visibility=None,
                          icon='www/bltaxtablerec.gif',
                          permission=OperateBastionLedgers,
                          )
    context.registerClass(BLAssociations.BLAssociationsFolder,
                          constructors = (BLAssociations.manage_addBLAssociationsFolder,),
                          visibility=None,
                          icon='skins/bastionledger_images/blassociation.gif',
                          permission=ManageBastionLedgers,
                          )
    context.registerClass(PeriodEndTool.PeriodEndTool,
                          constructors = (PeriodEndTool.manage_addPeriodEndTool,),
                          visibility=None,
                          icon='www/blquill.gif',
                          permission=ManageBastionLedgers,
                          )
    context.registerClass(DepreciationTool.DepreciationTool,
                          constructors = (DepreciationTool.manage_addDepreciationTool,),
                          visibility=None,
                          icon='www/blquill.gif',
                          permission=ManageBastionLedgers,
                          )

    coreutils.registerIcon(BLPayroll.BLPaySlip, 'www/blpayslip.gif', GLOBALS)
    coreutils.registerIcon(BLShareholderLedger.BLShareholderLedger, 'www/blshareholderledger.gif', GLOBALS)
    coreutils.registerIcon(FSBLProcess.FSBLEntryTemplate, 'www/fsblentry_tpl.gif', GLOBALS)
    coreutils.registerIcon(FSBLProcess.FSBLTransactionTemplateView, 'www/fsbltransaction_tpl.gif', GLOBALS)
    coreutils.registerIcon(FSBLProcess.FSBLTransactionTemplateViewSurrogate, 'www/fsbltransaction_tpl.gif', GLOBALS)

    context.registerHelp()
    coreutils.ContentInit(PROJECTNAME + ' Content',
                          content_types = [],
                          extra_constructors = (Ledger.addBastionLedger,
                                                BLAccount.addBLAccount,
                                                BLAssetRegister.manage_addBLAssetRegister,
                                                BLAssetRegister.addBLAsset,
                                                BLAssociations.addBLAssociation,
                                                BLEntryTemplate.addBLEntryTemplate,
                                                BLForecaster.manage_addBLForecaster,
                                                BLInventory.addBLInventory,
                                                BLInventory.addBLPartFolder,
                                                BLInventory.addBLPart,
                                                BLOrderBook.addBLOrderBook,
                                                BLOrderBook.addBLOrderAccount,
                                                BLOrderBook.addBLOrder,
                                                BLOrderBook.addBLCashOrder,
                                                BLOrderBook.addBLCashBook,
                                                BLPayroll.addBLPayroll,
                                                BLPayroll.addBLEmployee,
                                                BLPayroll.manage_addBLTimesheetSlot,
                                                BLProcess.manage_addBLProcess,
                                                BLQuoteManager.manage_addBLQuoteManager,
                                                BLShareholderLedger.addBLShareholderLedger,
                                                BLShareholderLedger.addBLShareholder,
                                                BLShareholderLedger.manage_addBLShareDefinition,
                                                BLShareholderLedger.manage_addBLAllocation,
                                                BLSubsidiaryAccount.addBLSubsidiaryAccount,
                                                BLSubsidiaryLedger.addBLSubsidiaryLedger,
                                                BLSubsidiaryTransaction.addBLSubsidiaryTransaction,
                                                BLTaxTables.manage_addBLTaxTable,
                                                BLTaxTables.addBLTaxTableRecord,
                                                BLTransaction.addBLTransaction,
                                                ),
                          permission = OperateBastionLedgers,
                          fti = [],).initialize(context)

    coreutils.ToolInit('Ledger Tool',
                   tools=(LedgerTool.LedgerTool, 
                          AccountPropertiesTool.AccountPropertiesTool,
                          LedgerControllerTool.LedgerControllerTool),
                   icon='tool.gif').initialize(context)

    try:
        profile_registry.registerProfile('default',
                                         PROJECTNAME,
                                         'bastionledger',
                                         'profiles/default',
                                         PROJECTNAME,
                                         EXTENSION,
                                         IPloneSiteRoot)
    except KeyError:
        # duplicate entry ...
        pass


misc_ = {}
for icon in ('blaccount', 'blentry', 'entry_template', 'blorderbook', 'payable', 'bltransaction', 'bltransaction_tpl',
             'bastionledger', 'blinventory', 'blorder', 
             'chart', 'blledger', 'orderitem', 'blpayroll', 'blprocess', 'bltimesheet', 'timesheetslot',
             'orders', 'bfolder', 'folder',
             'blemployee', 'blorderaccount', 'blpart', 'blsubsidiaryledger', 
             'allocation', 'blshareholder', 'blshareholderledger', 'blshare', 'bank',
             'fsprocess', 'fsblentry_tpl', 'fsbltransaction_tpl', 'blquill',
             'bldividendadvice', 'accountdata', 'dispatchable', 'blpayslip', 'hist_ledger', 'period', 'blreport',
             'blforecaster', 'forecast', 'blasset', 'blassetregister', 'blquotemgr', 'blquote',
             'bltaxtable', 'bltaxtablerec', 'blcontroller'):
    misc_[icon] = ImageFile('www/%s.gif' % icon, GLOBALS)


from AccessControl import ModuleSecurityInfo

#
# we want some stuff in the python operator module to be usable ...
#
ModuleSecurityInfo('operator').declarePublic('add')

ModuleSecurityInfo('Products').declarePublic('BastionLedger')

ModuleSecurityInfo('Products.BastionLedger').declarePublic('Exceptions')
ModuleSecurityInfo('Products.BastionLedger.Exceptions').declarePublic('LedgerError')
ModuleSecurityInfo('Products.BastionLedger.Exceptions').declarePublic('PostingError')
ModuleSecurityInfo('Products.BastionLedger.Exceptions').declarePublic('AlreadyPostedError')
ModuleSecurityInfo('Products.BastionLedger.Exceptions').declarePublic('UnpostedError')
ModuleSecurityInfo('Products.BastionLedger.Exceptions').declarePublic('OrphanEntryError')
ModuleSecurityInfo('Products.BastionLedger.Exceptions').declarePublic('IncorrectAmountError')
ModuleSecurityInfo('Products.BastionLedger.Exceptions').declarePublic('FXAmountError')
ModuleSecurityInfo('Products.BastionLedger.Exceptions').declarePublic('UnbalancedError')
ModuleSecurityInfo('Products.BastionLedger.Exceptions').declarePublic('InvalidTransition')
ModuleSecurityInfo('Products.BastionLedger.Exceptions').declarePublic('UnexpectedTransition')
ModuleSecurityInfo('Products.BastionLedger.Exceptions').declarePublic('InvalidState')
ModuleSecurityInfo('Products.BastionLedger.Exceptions').declarePublic('MissingAssociation')
ModuleSecurityInfo('Products.BastionLedger.Exceptions').declarePublic('InvalidPeriodEnd')
ModuleSecurityInfo('Products.BastionLedger.Exceptions').declarePublic('DepreciationError')
ModuleSecurityInfo('Products.BastionLedger.Exceptions').declarePublic('ProcessError')

ModuleSecurityInfo('Products.BastionLedger').declarePublic('utils')
ModuleSecurityInfo('Products.BastionLedger.utils').declarePublic('floor_date')
ModuleSecurityInfo('Products.BastionLedger.utils').declarePublic('ceiling_date')
ModuleSecurityInfo('Products.BastionLedger.utils').declarePublic('month_beginning_date')
ModuleSecurityInfo('Products.BastionLedger.utils').declarePublic('month_ending_date')
ModuleSecurityInfo('Products.BastionLedger.utils').declarePublic('assert_currency')
ModuleSecurityInfo('Products.BastionLedger.utils').declarePublic('lastXDays')
ModuleSecurityInfo('Products.BastionLedger.utils').declarePublic('lastXMonthEnds')
ModuleSecurityInfo('Products.BastionLedger.utils').declarePublic('lastXMonthBegins')

# trying to give '' access permission to BLLedger's so we don't get context UnauthorizedBinding errors ...
#ModuleSecurityInfo('Products.BastionLedger').declarePublic('BLLedger')
#ModuleSecurityInfo('Products.BastionLedger.BLLedger').declarePublic('BLLedger')

ModuleSecurityInfo('Products.BastionLedger').declarePublic('BLEntry')
ModuleSecurityInfo('Products.BastionLedger.BLEntry').declarePublic('manage_addBLEntry')
ModuleSecurityInfo('Products.BastionLedger.BLEntry').declarePublic('BLEntry')

ModuleSecurityInfo('Products.BastionLedger').declarePublic('BLTransaction')
ModuleSecurityInfo('Products.BastionLedger.BLTransaction').declarePublic('manage_addBLTransaction')

ModuleSecurityInfo('Products.BastionLedger').declarePublic('BLSubsidiaryEntry')
ModuleSecurityInfo('Products.BastionLedger.BLSubsidiaryEntry').declarePublic('manage_addBLSubsidiaryEntry')
ModuleSecurityInfo('Products.BastionLedger.BLSubsidiaryEntry').declarePublic('BLSubsidiaryEntry')

ModuleSecurityInfo('Products.BastionLedger').declarePublic('BLSubsidiaryTransaction')
ModuleSecurityInfo('Products.BastionLedger.BLSubsidiaryTransaction').declarePublic('manage_addBLSubsidiaryTransaction')

ModuleSecurityInfo('Products.BastionLedger').declarePublic('BLPayroll')
ModuleSecurityInfo('Products.BastionLedger.BLPayroll').declarePublic('select_day_of_week')

ModuleSecurityInfo('Products.BastionLedger').declarePublic('BLOrderBook')
ModuleSecurityInfo('Products.BastionLedger.BLOrderBook').declarePublic('orderForm')
ModuleSecurityInfo('Products.BastionLedger.BLOrderBook').declarePublic('manage_addBLOrderAccount')
ModuleSecurityInfo('Products.BastionLedger.BLOrderBook').declarePublic('manage_addBLOrder')
ModuleSecurityInfo('Products.BastionLedger.BLOrderBook').declarePublic('manage_addBLOrderItem')

ModuleSecurityInfo('Products.BastionLedger').declarePublic('BLPayroll')
ModuleSecurityInfo('Products.BastionLedger.BLPayroll').declarePublic('manage_addBLEmployee')
ModuleSecurityInfo('Products.BastionLedger.BLPayroll').declarePublic('manage_addBLTimesheet')

ModuleSecurityInfo('Products.BastionLedger').declarePublic('BLShareholderLedger')
ModuleSecurityInfo('Products.BastionLedger.BLShareholderLedger').declarePublic('manage_addBLDividendAdvice')

ModuleSecurityInfo('Products.BastionLedger').declarePublic('BLReport')
#ModuleSecurityInfo('Products.BastionLedger.BLReport').declareProtected(OperateBastionLedgers, 'manage_addBLReport')
ModuleSecurityInfo('Products.BastionLedger.BLReport').declarePublic(OperateBastionLedgers, 'manage_addBLReport')


ModuleSecurityInfo('email').declarePublic('Utils')
ModuleSecurityInfo('email.Utils').declarePublic('getaddresses')
ModuleSecurityInfo('email.Utils').declarePublic('parseaddr')
ModuleSecurityInfo('email.Utils').declarePublic('formataddr')
