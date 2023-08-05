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

# import stuff
import AccessControl, types, string, os, operator, logging
from AccessControl.Permissions import view_management_screens, manage_properties, \
     access_contents_information
from DateTime import DateTime
from Acquisition import aq_base
from OFS.userfolder import manage_addUserFolder
from AccessControl.User import BasicUser
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
from Products.BastionBanking.ZCurrency import ZCurrency
from Products.CMFCore.permissions import View

from utils import _mime_str, assert_currency
from BLGlobals import EPOCH
from BLBase import *
from BLReport import BLReport
# TODO - deprecate DatedFolder ...
from BLDatedFolder import BLDatedFolder
from BLSubsidiaryLedger import BLSubsidiaryLedger
from BLSubsidiaryAccount import BLSubsidiaryAccount
from BLEntry import BLEntry
from BLSubsidiaryEntry import BLSubsidiaryEntry
from BLEntryTemplate import BLEntryTemplate
from BLTransaction import BLTransaction
from BLProcess import manage_addBLProcess
from Permissions import ManageBastionLedgers, OperateBastionLedgers, setDefaultRoles
from Products.CMFCore import permissions
from BLAccount import BLAccounts, addBLAccount
from Exceptions import UnexpectedTransaction

from zope.interface import Interface, implements

LOG = logging.getLogger('BLPayroll')

# this is as per DateTime ...
_daymap     ={'sunday': 1,    'sun': 1,
              'monday': 2,    'mon': 2,
              'tuesday': 3,   'tues': 3,  'tue': 3,
              'wednesday': 4, 'wed': 4,
              'thursday': 5,  'thurs': 5, 'thur': 5, 'thu': 5,
              'friday': 6,    'fri': 6,
              'saturday': 7,  'sat': 7}

def select_day_of_week():
    return ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

    
manage_addBLPayrollForm = PageTemplateFile('zpt/add_payroll', globals()) 
def manage_addBLPayroll(self, id, controlAccount, timesheet_day='Friday', title='', REQUEST=None):
    """ adds a user container """
    try:
        # do some checking ...
        control = self.Ledger._getOb(controlAccount)
        assert control.meta_type =='BLAccount', "Incorrect Control Account Type - Must be strictly GL"
        #assert not getattr(aq_base(control), id, None),"A Subsidiary Ledger Already Exists for this account."
        self._setObject(id, BLPayroll(id, title, control, timesheet_day, control.base_currency))
    except:
        # TODO: a messagedialogue ..
        raise

    if REQUEST is not None:
        return self.manage_main(self, REQUEST)
    return id

def addBLPayroll(self, id, title='', REQUEST=None):
    """
    Plone Add
    """
    control = addBLAccount(self.Ledger, id, title)
    self.manage_addBLPayroll(id, control, title=title)
    return id

class ITimesheetSlot(Interface): pass
class IPaySlip(Interface): pass


class BLPayroll ( BLSubsidiaryLedger, BLDatedFolder, CalendarSupport ):
    """
    A simple payroll ledger incorporating automated scheduling of execution

    """
    meta_type = portal_type = 'BLPayroll'

    implements(ITimesheetSlot)
    
    __ac_permissions__ = BLSubsidiaryLedger.__ac_permissions__ + (
        (access_contents_information, ('select_timesheet_day', 'payroll_day',
                                       'payroll_daynumber', 'getDay',
                                       'isTimesheetsRequired', 'get_size',
                                       'superannuationEmployees', 'superannuationSum',
                                       'timesheet_daynumber', 'getTimesheet',
                                       'getTimesheetDay', 'getTimesheets', )),
        (view, ('getPayrollDay', 'select_day_of_week', 'getPayroll',
                'getTimesheetSlots')),
        (OperateBastionLedgers, ('manage_payrolls', 'manage_tax_certificates', 'is_run',
                                 'manage_config', 'manage_accounts', 'manage_payEmployees',
                                 'manage_timesheet', ) ),
        (ManageBastionLedgers, ('manage_edit',)),
        ) + BLDatedFolder.__ac_permissions__

    #dontAllowCopyAndPaste = 1
    account_types = ('BLEmployee',)
    
    manage_options = (
        {'label': 'Payroll',       'action': 'manage_payrolls',
         'help':('BastionLedger', 'payroll.stx') },
        {'label': 'View',          'action':'',},
        {'label': 'Config',        'action': 'manage_config' },
        #{'label': 'Extensions',    'action': 'manage_common_sheet' },
        {'label': 'Employees',     'action': 'manage_accounts' },
        ) + BLSubsidiaryLedger.manage_options[3:]

    manage_payrolls = manage_main = PageTemplateFile('zpt/view_payrolls', globals())
    manage_propertiesForm = PageTemplateFile('zpt/payroll_props', globals())

    try:
        manage_payrolls._setName('manage_payrolls')
    except: pass
    manage_config = BObjectManager.manage_main
    try:
        manage_config._setName('manage_config')
    except: pass
    
    #manage_main._setName('manage_main')
    
    def __init__(self, id, title, control, timesheet_day, currencies,
                 account_prefix='E', txn_prefix='P'):
        BLSubsidiaryLedger.__init__(self, id, title, control, currencies,
                                    1000000, account_prefix, 1, txn_prefix )

        self.timesheet_day = timesheet_day
        self.timesheets_required = 0


    def all_meta_types(self):
        """  """
        #return [ ProductsDictionary('BLEmployee'),
        #         ProductsDictionary('BLTransactionTemplate'),
        #         ProductsDictionary('BLTimesheetSlot'),
        #         ProductsDictionary('Page Template') ]
        return [ ProductsDictionary('BLEmployee'),
                 ProductsDictionary('BLSubsidiaryTransaction'),
                 ProductsDictionary('BLTimesheetSlot'),
                 ProductsDictionary('Script (Python)'),
                 ProductsDictionary('Page Template') ]
    
    def select_timesheet_day(self):
        """
        return the selection day - TODO? WFT ..
        """
        return select_timesheet_day()

    def payroll_day(self):
        """ the week day which the payroll will be run """
        return self.timesheet_day

    def payroll_daynumber(self):
        """
        maps timesheet day to Plone Calendar day
        """
        number = _daymap[self.timesheet_day.lower()] - 2 
        if number < 0:
            return number + 7
        return number

    def getDay(self, day):
        if day.Day() == self.timesheet_day:
            return '<a href="manage_main?date:date=%s"><strong>%s</strong></a>' % \
                   (day.strftime('%Y/%m/%d'), day.day())
        return day.day()

    def getPayroll(self, day):
        """
        returns a hash keyed on employee id of payroll transactions for the closest payroll date to day
        """
        day = self.getPayrollDay(day)

        entries = {}
        for txn in self.Transactions(effective_date={'query':[day+1, day-1] ,
                                                     'range':'min:max' }):
            if txn.title == 'Auto - Payable':
                employee_id = txn.objectValues('BLSubsidiaryEntry')[0].blAccount().getId()
                entries[employee_id] = txn
        return entries
        
    def getPayrollDay(self, date):
        # normalise and snap to grid ...
        day = DateTime(date.year(), date.month(), date.day())
        timesheet_day = self.timesheet_day
        while day.Day() != timesheet_day:
            day = day - 1
        return day

    def select_day_of_week(self):
        return select_day_of_week()

    def is_run(self, date=None, REQUEST=None):
        """
        returns whether or not the payroll has been run for this period
        """
        date = date or DateTime()
        # hmmm - this is set in BLTransactionTemplate ...
        txn_title = 'Auto - %s' % self.blp_employee_payable.title

        for txn in self.Transactions(effective_date={ 'query': [date + 1, date - 6], 'range' : 'minmax' }):
            if txn.title == txn_title:
                return True
        return False
    
    def manage_payEmployees(self, ids=[], effective=None, force=False, REQUEST=None):
        """
        generate and post the payroll txn by running the 'Payable' template
        """
        effective = effective or DateTime()
        LOG.debug( "BLPayroll::manage_payEmployees(%s)" % effective)

        if self.is_run(effective) and not force:
            if REQUEST is not None:
                REQUEST.set('manage_tabs_message', 'Payroll Already Run!')
                return self.manage_main(self, REQUEST)
            else:
                return

        employees = filter(lambda x,ids=ids: x.getId() in ids, self.accountValues())
        # filter non-timesheet approved employees ...
        if self.timesheets_required:
            employees = filter(lambda e,date=effective: e.getTimesheetStatus(date) == 'approved', employees)
    
        #
        # call our payroll transaction template (this also automatically posts)...
        # note that payslip processing requires a separate transaction per employee ...
        #
        payslip_id = effective.strftime('%Y-%m-%d')
        zero = self.zeroAmount()

        for employee in employees:
            txn = self.blp_employee_payable.generate(accounts=[employee], effective=effective)
            employee._setObject(payslip_id, BLPaySlip(payslip_id, payslip_id, txn.getId(), zero, zero, zero))

        if REQUEST is not None:
            REQUEST.set('manage_tabs_message', 'Payroll Processed!')
            return self.manage_main(self, REQUEST)


    def isTimesheetsRequired(self):
        if getattr(aq_base(self), 'timesheets_required', None):
            return self.timesheets_required
        else:
            self.timesheets_required = False
        return False

    def get_size(self):
        return 0


    def Xmanage_beforeDelete(self, item, container):
        BLSubsidiaryLedger.manage_beforeDelete(self, item, container)


    def manage_editTimesheetProps(self, timesheet_day, timesheets_required=False):
        """
        edit extended ledger props
        """
        self.timesheet_day = timesheet_day
        self.timesheets_required = timesheets_required
        
    def superannuationEmployees(self, start_date, end_date):
        """
        return lists of employee accounts with same super fund active within the
        specified date range
        """
        results = []
        employees = list(self.accountValues())
        employees.sort(lambda x,y: x.super_fund() <= y.super_fund())

        if employees:
            active_list = []
            fund = ''
            for employee in employees:
                employee_fund = employee.super_fund()
                if not employee_fund:
                    continue
                if active_list and employee_fund != fund:
                    results.append(active_list)
                    active_list = []
                fund = employee_fund
                active_list.append(employee)
            # append the last one ...
            if active_list:
                results.append(active_list)
        return results

    def superannuationSum(self, tag, employees, start_date, end_date):
        """
        helper to sum a bunch of employee's super contribution by tag (ie wages_super = company contribution)
        """
        return reduce(operator.add,
                      map(lambda x,tag=tag,start=start_date,end=end_date: x.sum(tag,[start,end]),
                          employees))

    def manage_tax_certificates(self, start, end, send=True, REQUEST=None):
        """
        prepare and mailout annual tax certificates to employees who've worked for you
        this year
        """
        try:
            mailhost = self.superValues(['Mail Host', 'Secure Mail Host'])[0]
        except:
            # TODO - exception handling ...
            if REQUEST:
                REQUEST.set('manage_tabs_message', 'No Mail Host Found')
                return self.manage_main(self, REQUEST)
            raise

        if not getattr(self, 'blemployee_tax_certificate', None) or \
               not getattr(self, 'blpayroll_payg_summary', None):
            return

        counter = 0
        reports = self.Reports
        id = end.strftime('%Y-%m-%d')

        title_date = end.strftime('%d %b %Y')

        if getattr(reports, 'payg-payment-summary-%s' %  id, None):
            reports._delObject('payg-payment-summary-%s' % id)
        reports._setObject('payg-payment-summary-%s' % id,
                           BLReport('payg-payment-summary-%s' % id,
                                    'PAYG payment summary %s' % title_date,
                                    end,
                                    self.blpayroll_payg_summary(startdate=start, enddate=end).encode('ascii', 'ignore')))

        subject =  '%s - Tax Certificate' % self.aq_parent.title
        payer_options = {'purpose':'Payer Tax Return Copy',
                         'startdate':start,
                         'enddate': end,
                         'message':"""Must be sent to the Taxation Office by the Payer along with the PAYG payment summary statement."""}
        personal_options = {'purpose':'Payee Personal Record Copy',
                            'startdate':start,
                            'enddate': end,
                            'message':"""This copy is to be kept by the Payee for the Payee's records only.  <b>Do not send this copy to the Taxation Office</b>."""}
        tax_office_options = {'purpose':'Payee Tax Return Copy',
                              'startdate':start,
                              'enddate': end,
                              'message':"""Must be sent to the Taxation Office by the Payee in accordance with the notes supplied with this certificate."""}

        # TODO - figure out which employees ...
        for employee in self.Accounts(status='open'):
            counter += 1

            if getattr(reports, 'tax_certificate-%s-%s' % (employee.getId(), id), None):
                reports._delObject('tax-certificate-%s-%s' % (employee.getId(), id))
            reports._setObject('tax-certificate-%s-%s' % (employee.getId(), id),
                               BLReport('tax-certificate-%s-%s' % (employee.getId(), id), 'Tax Cert - %s %s' % (employee.title, title_date),
                                        end, employee.blemployee_tax_certificate(**payer_options).encode('ascii', 'ignore')))
            
            if getattr(aq_base(employee), 'tax-certificate-%s' % id, None):
                employee._delObject('tax-certificate-%s' % id)
            tax_office_text = employee.blemployee_tax_certificate(**tax_office_options).encode('ascii', 'ignore')
            employee._setObject('tax-certificate-%s' % id,
                                BLReport('tax-certificate-%s' % id, 'Tax Certificate %s' % title_date,
                                         end, tax_office_text))
            if getattr(aq_base(employee), 'tax-certificate-copy-%s' % id, None):
                employee._delObject('tax-certificate-copy-%s' % id)
            personal_text = employee.blemployee_tax_certificate(**personal_options).encode('ascii', 'ignore')
            employee._setObject('tax-certificate-copy-%s' % id,
                                BLReport('tax-certificate-copy-%s' % id, 'Tax Certificate - COPY %s' % title_date,
                                         end, personal_text))
                
            if send:
                mailhost.send(_mime_str({'Subject':subject, 'From':self.email, 'To':employee.email,}, '',
                                        [('personal.html', 'text/html', personal_text),
                                         ('tax_office.html', 'text/html', tax_office_text)]),
                              [employee.email], self.email, subject)

        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Processed %i tax certificates' % counter)
            return self.manage_main(self, REQUEST)

    def timesheet_daynumber(self):
        return _daymap[self.timesheet_day.lower()]

    def getTimesheet(self, day):
        day = self.getTimesheetDay(day)
        try:
            return self.getEventsForDay(day)[0]
        except IndexError:
            # bugger - no record, best create one ...
            LOG.debug( "BLEmployeeTimesheetFolder::getTimesheet doing generateEventId ...")
            timesheet = BLTimesheet(_generateEventId(self), '', day, [], self.getTimesheetSlots())
            self._setObject(timesheet.getId(), timesheet)
            return timesheet
        except:
            raise
        
        raise KeyError, "not found for day: %s" % day

    def manage_timesheet(self, date, entries, REQUEST=None):
        """
        add/update timesheet records ...
        """
        timesheet = self.getTimesheet(date)
        timesheet.update(entries)
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(REQUEST['URL1'])


    def getTimesheetDay(self, date=DateTime()):
        """
        return the week day of the nearest previous timesheet posting day
        """
        # normalise and snap to grid ...
        day = DateTime(date.year(), date.month(), date.day())
        while day.Day() != self.timesheet_day:
            day = day - 1
        return day

    def getTimesheetSlots(self):
        """
        retrieve from Payroll parameters ...
        """
        slots = []
        if getattr(aq_base(self), 'Config', None):
            slots.extend(map(lambda x: x.__of__(self),
                             self.Config.objectValues('FSTimesheetSlot')))
        slots.extend(self.objectValues('BLTimesheetSlot'))
        return slots

    def getTimesheets(self, datemin, datemax):
        # query catalog ...
        #
        # we need to figure out the correct catalog query ...
        #
        return self.Accounts(meta_type='BLTimeSheet',
                             effective_date={'query':[datemin, datemax],
                                             'range':'minmax'})
    
AccessControl.class_init.InitializeClass(BLPayroll)


manage_addBLEmployeeForm = PageTemplateFile('zpt/add_employee', globals()) 
def manage_addBLEmployee(self, title, currency, start_day,
                         description='',uid='', pwd='', id='', type='', REQUEST=None):
    """ an employee """
    self = self.this()
    if not id:
        id = self.nextAccountId()
    
    type = type or self.controlAccount().type
    self._setObject(id, BLEmployee(id, title, description, type, currency, start_day))

    # make this user the owner ...
    employee = getattr(self, id)
    if uid:
        if not isinstance(uid, BasicUser):
            assert pwd, 'user password required'
            manage_addUserFolder(employee)
            acl_users = employee.acl_users
            acl_users.userFolderAddUser(uid, pwd, [], [])
            uid = employee.acl_users.getUser(uid).__of__(acl_users)
        employee.changeOwnership(uid)
        employee.manage_setLocalRoles(id, ['Owner'])

    bt = getToolByName(self, 'portal_bastionledger')
    if bt.hasTaxTable('personal_tax'):
        employee.manage_addTaxGroup('personal_tax')

    if REQUEST is not None:
        REQUEST.RESPONSE.redirect("%s/%s/manage_main" % (REQUEST['URL3'], id))
    else:
        return employee


def addBLEmployee(self, id, title=''):
    """ Plone Constructor """
    employee = manage_addBLEmployee(self,
                                    id=id,
                                    title=title,
                                    currency=self.currencies[0],
                                    start_day=DateTime())
    id = employee.getId()
    return id



class BLPaySlip(PortalContent):
    """
    encapsulate a payslip - which in turn saves a copy of a payroll transaction
    so it can be live isolated from any transaction purging regime
    """
    meta_type = portal_type = 'BLPaySlip'

    implements(IPaySlip)

    default_view = 'blemployee_payslip'

    __ac_permissions__ = (
        (view_management_screens, ('manage_main',)),
        (OperateBastionLedgers, ('valid_txn_id',)),
        (ManageBastionLedgers, ('calculate_running_totals',)),
        (access_contents_information, ('gross', 'net', 'tax', 'effective',
                                       'blTransaction')),
        ) + PortalContent.__ac_permissions__

    _properties = PortalContent._properties + (
        {'id':'txn_id',         'type':'string',   'mode':'w'},
        {'id':'gross_to_date',  'type':'currency', 'mode':'r'},
        {'id':'tax_to_date',    'type':'currency', 'mode':'r'},
        {'id':'net_to_date',    'type':'currency', 'mode':'r'},
    )
    
    manage_options = (
        {'label':'Payslip',    'action':'manage_main' },
        {'label':'Properties', 'action':'manage_propertiesForm',},
        {'label':'View',       'action':'' },
        ) + PortalContent.manage_options

    manage_main = PageTemplateFile('zpt/view_payslip', globals())

    def __init__(self, id, title, txn_id, gross_to_date, tax_to_date, net_to_date):
        PortalContent.__init__(self, id, title)
        self.txn_id = txn_id
        self.gross_to_date = gross_to_date
        self.tax_to_date = tax_to_date
        self.net_to_date = net_to_date

    def _updateProperty(self, name, value):
        PortalContent._updateProperty(self, name, value)
        if name == 'txn_id' and not self.valid_txn_id():
            raise UnexpectedTransaction, value

    def calculate_running_totals(self,starting_date=None):
        """
        go do our summated totals
        """
        employee = self.aq_parent
        if not starting_date:
            starting_date = employee.openingDate()
        txn = self.blTransaction()
        if txn:
            gross_id = self.Ledger.accountsForTag('wages_exp')[0].getId()
            self.gross_to_date = employee.sum(gross_id,
                                              [starting_date, txn.effective_date])
            self.net_to_date = employee.sum(employee.getId(),
                                            [starting_date, txn.effective_date])
            tax_id = self.Ledger.accountsForTag('wages_tax')[0].getId()
            self.tax_to_date = employee.sum(tax_id,
                                            [starting_date,txn.effective_date])
        else:
            self.gross_to_date = self.net_to_date = self.tax_to_date = self.zeroAmount()

    def effective(self):
        """
        """
        txn = self.blTransaction()
        if txn:
            return txn.effective_date
        return self.created()

    def gross(self):
        """
        """
        txn = self.blTransaction()
        if txn:
            gross_account = self.Ledger.accountsForTag('wages_exp')[0]
            try:
                return txn.entry(gross_account.getId()).absAmount()
            except:
                raise UnexpectedTransaction, '%s - %s' % (self.getId(), txn)
        return self.zeroAmount()

    def net(self):
        """
        """
        txn = self.blTransaction()
        if txn:
            try:
                return txn.entry(self.aq_parent.getId()).absAmount()
            except:
                raise UnexpectedTransaction, '%s - %s' % (self.getId(), txn)
        return self.zeroAmount()

    def tax(self):
        """
        """
        txn = self.blTransaction()
        if txn:
            tax_account = self.Ledger.accountsForTag('wages_tax')[0]
            try:
                return txn.entry(tax_account.getId()).absAmount()
            except:
                raise UnexpectedTransaction, '%s - %s' % (self.getId(), txn)
        return self.zeroAmount()

    def valid_txn_id(self):
        """
        hmmm - some of these are screwed ....

        but we're just checking that it looks like a payroll payment
        """
        txn = self.blTransaction()
        if not txn:
            return False
        # tax isn't compulsory ...
        #for tag in ('wages_tax', 'wages_exp'):
        for tag in ('wages_exp',):
            account = self.Ledger.accountsForTag(tag)[0]
            try:
                entry = txn.entry(account.getId())
            except:
                return False
        try:
            entry = txn.entry(self.aq_parent.getId())
            return True
        except:
            pass
        return False

    def __cmp__(self, other):
        """
        allow participation in objectItemsByDate ...
        """
        if isinstance(other, BLPaySlip):
            x = self.effective()
            y = other.effective()
            if x > y:
                return -1
            elif x < y:
                return 1
            return 0
        return 1

    def blTransaction(self):
        """
        return underlying transaction supporting this payslip, or None if not found - ie
        an old period txn etc etc 
        """
        try:
            return self.aq_parent.aq_parent._getOb(self.txn_id)
        except KeyError:
            return None
        
    def _repair(self):
        txn = getattr(aq_base(self), 'txn', None)
        if txn:
            txn_id = txn.aq_inner.id
            assert type(txn_id) == types.StringType, 'doh - non-string txn_id: %s' % type(txn_id)
            self.txn_id = txn_id   # don't use getId() ...
            delattr(self, 'txn')
        self.calculate_running_totals()

AccessControl.class_init.InitializeClass(BLPaySlip)


class BLEmployee(BLSubsidiaryAccount):

    meta_type = portal_type = 'BLEmployee'

    Basis = [ 'Hour', 'Day', 'Month', 'Year' ]
    
    __ac_permissions__ = BLSubsidiaryAccount.__ac_permissions__ + (
        (access_contents_information, ('blTransaction', 'entryTemplateValues',)),
        (view, ('super_fund', 'getTimesheetStatus', 'grossBreakDown', 'gross',
                'manage_edit_public')),
        (permissions.ModifyPortalContent, ('manage_deletePayslips',)),
        (view_management_screens, ('manage_details',)),
        (OperateBastionLedgers, ('manage_edit_private', 'setTimesheetsProcessed')),
        )

    def manage_options(self):
        options = [ {'label': 'Payslips',   'action': 'manage_main',
                     'help':('BastionLedger', 'employee.stx') },        
                    {'label': 'Deductions', 'action': 'manage_entries' } ]
        options.extend(BLSubsidiaryAccount.manage_options(self))
        return options

    manage_details = PageTemplateFile('zpt/edit_employee',   globals())
    manage_main = PageTemplateFile('zpt/view_payslips',   globals())

    def __init__(self, id, title, description, type, currency, start_day=DateTime(),
                 department='', email='', contact='', address='',  phone='',
                 salary=0, rate=0, basis='Hour', tax_num='', tax_code='',
                 accrued_leave=0.0, bank_acc='', dob=EPOCH, sick_days=0.0,
                 super_number='', super_details=''):

        BLSubsidiaryAccount.__init__(self, id, title, description, type, 'Payroll',currency, id)
        BLEmployee.manage_edit_public(self, title, description, email, address, phone, tax_num, bank_acc, dob,
                                      super_number, super_details)
        BLEmployee.manage_edit_private(self, start_day, department, salary, rate, basis, tax_code,
                                       accrued_leave, sick_days)

    def all_meta_types(self):
        # deductions ...
        return [ ProductsDictionary('BLEntryTemplate') ]

    def manage_edit_public(self, title='', description='', email='', address='', phone='', tax_number='',
                           bank_account='', date_of_birth=EPOCH, super_number='',
                           super_details='', REQUEST=None):
        """ """
        self.title = title
        self.description = description
        self.email = email
        self.address = address
        self.phone = phone
        self.tax_number = tax_number
        self.bank_account = bank_account
        if not isinstance(date_of_birth, DateTime):
            date_of_birth = DateTime(date_of_birth)
        self.date_of_birth = date_of_birth
        self.super_number = super_number
        self.super_details = super_details

        if REQUEST is not None:
            REQUEST.set('management_view', 'Details')
            return self.manage_details(self, REQUEST)
        return 0

    def manage_edit_private(self, start_day=DateTime(), department='', salary=0, rate=0, basis='Hour',
                            tax_code='', accrued_leave=0.0, sick_days=0.0, REQUEST=None):
        """ """
        if not isinstance(start_day, DateTime):
            start_day = DateTime(start_day)
        self.start_day = start_day
        self.department = department
        try:
            assert_currency(salary)
        except:
            salary = ZCurrency(salary, self.base_currency)
        self.salary = salary
        try:
            assert_currency(rate)
        except:
            rate = ZCurrency(rate, self.base_currency)
        self.hourly_rate = rate
        self.basis = basis
        self.tax_code = tax_code
        self.accrued_leave = accrued_leave
        self.sick_days = sick_days

        if REQUEST is not None:
            REQUEST.set('management_view', 'Details')
            return self.manage_details(self, REQUEST)
        return 0

    def entryTemplateValues(self):
        """
        """
        return self.objectValues('BLEntryTemplate')


    def super_fund(self):
        """
        return the super fund name (ie first line of super_details)
        """
        if self.super_details:
            return self.super_details.split('\n')[0]

    def ___repr__(self):
        return str(self.__dict__)

    def blTransaction(self, entry_id):
        return self._getOb(entry_id)


    def getTimesheetStatus(self, date):
        if self.aq_parent.isTimesheetsRequired():
            return self.Timesheets.getTimesheet(date).status()
        #
        # otherwise return OK Timesheet status ...
        #
        return 'approved'

    def grossBreakDown(self, datemin, datemax):

        slots = self.aq_parent.objectValues('BLTimesheetSlot')

        results = {}
        for slot in slots:
            results[slot.getId()] = ZCurrency(self.base_currency, 0)
        
        for timesheet in self.Timesheets.getTimesheets(datemin, datemax):
            for slot in slots:
                #
                # There's something f**ked with the ZCurrency class mathematics ...
                # 
                results[slot.getId()] += ZCurrency(self.base_currency,
                                                  self.hourly_rate().amount() * slot.ratio() * timesheet.sum(slot.getId()))

        return results

    def gross(self, datemin, datemax):
        """
        the total employee income for specified date range
        """
        total = ZCurrency(self.base_currency, 0)
        for amt in self.grossBreakDown(datemin, datemax).values():
            LOG.debug( "BLEmployee::gross() adding  %s" % amt)
            total += amt
        LOG.debug( "BLEmployee::gross() - %s" % total)
        #return reduce( operator.add, self.grossBreakDown(datemin, datemax).values() )
        return total
    
    def setTimesheetsProcessed(self, datemin, datemax):
        for timesheet in self.Timesheets.getTimesheets(datemin, datemax):
            timesheet._status('processed')

    def manage_deletePayslips(self, ids=[], REQUEST=None):
        """
        """
        for id in ids:
            try:
                ob = self._getOb(id)
                if ob.meta_type == 'BLPaySlip':
                    self._delObject(id)
            except (KeyError, AttributeError):
                pass
        if REQUEST:
            return self.manage_main(self, REQUEST)

    def _repair(self):
        #BLSubsidiaryAccount._repair(self)
        if not getattr(aq_base(self), 'basis', None):
            self.basis = 'Hour'
        for payslip in self.objectValues('BLPaySlip'):
            payslip._repair()
        # doh - screwed up BLSubsidiaryAccount ctor parameters ...
        self.tags = []

        if getattr(aq_base(self), 'Timesheets', None):
            for ts in self.Timesheets.objectValues():
                self._setObject(ts.getId(), ts)
            self._delOb('Timesheets')
            
        if getattr(aq_base(self), 'Entries', None):
            self._delOb('Entries')

AccessControl.class_init.InitializeClass(BLEmployee)

manage_addBLEmployeeEntryTemplateForm = PageTemplateFile('zpt/add_emplentrytmpl', globals()) 
def manage_addBLEmployeeEntryTemplate(self, id, currency, account, REQUEST=None):
    """
    Add an entry to a transaction ...
    """
    ac = self.Ledger._getOb(account)
    assert 'empl_dedtn' in ac.tags, 'Invalid Account: %s' % account
    
    self._setObject(id, BLEmployeeEntryTemplate(id, ac.title, currency, account))
    
    if REQUEST is not None:
        REQUEST.RESPONSE.redirect("%s/%s/manage_workspace" % (REQUEST['URL3'], id))

    return id

class BLEmployeeEntryTemplate (BLEntryTemplate):
    """
    A restricted employee deduction template
    """
    meta_type = portal_type = 'BLEmployeeEntryTemplate'
    __setstate__ = BLEntryTemplate.__setstate__
    _params='employee'
    def __init__(self, id, title, currency, account):
        BLEntryTemplate.__init__(self, id, title, currency, account)
        self.write("""#
# return an amount (possibly calculated ...)
#
from Products.BastionBanking.ZCurrency import ZCurrency
gross = context.Gross.amount
tax = context.Tax.amount

return ZCurrency(script.currency, 0.00)
""")

    def __call__(self, employee):
        #
        # we expect to receive a currency from which to build up a 'safe' entry - ie one
        # which we can be reasonably confident that our employee isn't going to stiff us
        # with something inappropriate ...
        #
        # we are return both the debit and credit side - the credit side will automatically
        # aggregate with the employee's net
        #
        currency = BLEntryTemplate.__call__(self, employee)
        assert_currency(currency)
        ac = self.Ledger._getOb(self.account)
        currency = abs(currency)
        if ac.type in ['Liability', 'Proprietorship', 'Income']:
            currency = -currency
        return [ BLEntry(self.account,
                         self.title,
                         'Ledger/%s' % self.account,
                         currency,
                         self.aq_parent.aq_parent.getId()) ]

AccessControl.class_init.InitializeClass(BLEmployeeEntryTemplate)

manage_addBLTimesheetSlotForm = PageTemplateFile('zpt/add_timesheetslot', globals()) 
def manage_addBLTimesheetSlot(self, id, ratio=1.0, max_hrs=8, min_hrs=0,
                              defaults=[0,0,0,0,0,0,0], title='', REQUEST=None):
    """
    define and verify timesheet slots, their acceptable values, and actual payment amounts
    """
    try:
        self._setObject(id, BLTimesheetSlot(id, title, ratio, max_hrs, min_hrs, defaults))
    except:
        # TODO: a messagedialogue ..
        raise
    
    if REQUEST is not None:
        #REQUEST.RESPONSE.redirect("%s/%s/manage_workspace" % (REQUEST['URL3'], id))
        return self.manage_main(self, REQUEST)
    return id

class BLTimesheetSlot( BSimpleItem ):
    """
    This class provides a mechanism to support user-defined semantics between
    accounts - principally by maintaining a list for this 'id' tag.

    It is reasonably context-independent, but it does expect to find a GL with
    the list of available accounts using it's accountContainer method
    """

    meta_type = portal_type = 'BLTimesheetSlot'

    __ac_permissions__ = BSimpleItem.__ac_permissions__ + (
        (ManageBastionLedgers, ('manage_edit',)),
        )

    _properties = (
        {'id':'ratio',      'type':'float', 'mode':'w'},
        {'id':'min_hrs',    'type':'float', 'mode':'w'},
        {'id':'max_hrs',    'type':'float', 'mode':'w'},
        )

    manage_options = (
        {'label': 'Details', 'action': 'manage_main', },
        ) + BSimpleItem.manage_options
 
    manage_main = PageTemplateFile('zpt/edit_timesheetslot', globals())

    def __init__(self, id, title, ratio, max_hrs, min_hrs, defaults):
        self.id = id
        self.manage_edit(title, ratio, max_hrs, min_hrs, defaults)

    def manage_edit(self, title, ratio, max_hrs, min_hrs, defaults, REQUEST=None):
        """ """
        self.title = title
        self.ratio = ratio
        self.min_hrs = min_hrs
        self.max_hrs = max_hrs
        self.defaults = defaults
        if REQUEST is not None:
            return self.manage_main(self, REQUEST)

        
AccessControl.class_init.InitializeClass(BLTimesheetSlot)



manage_addBLTimesheetForm = PageTemplateFile('zpt/add_emptimesheet', globals())
def manage_addBLTimesheet(self, date, entries, id=None, REQUEST=None):
    """
    Add a timesheet
    """
    self = self.this()

    if not id:
        id = date.strftime('timesheet-%Y-%m-%d')
    # check unique date ...
    ts = getattr(aq_base(self),id,None) 
    if ts:
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect('%s/manage_main?manage_tabs_message=Already+Submitted (%s)!!' % ( REQUEST['URL3'], id))
            return
        else:
            raise KeyError, "already submitted (%s)!!" % id

    self._setObject(id, BLTimesheet(id, date.strftime('%Y-%m-%d'), date, entries))

    if REQUEST:
        REQUEST.RESPONSE.redirect('%s/manage_main' % REQUEST['URL3'])
    return id


class BLTimesheet ( BSimpleItem ):

    """
    the record attribute is a list (corresponding to slots) of hashes containing keys of day and slot-id
    the slot-id's value is a list of hours corresponding to each week day
    """
    meta_type = portal_type = 'BLTimesheet'

    __ac_permissions__ = (
        (access_contents_information, ('sum', 'normalisedTime', 'start_day',
                                       'end_day', 'slots', 'getTimesheetSlots')),   
        (OperateBastionLedgers, ('manage_edit', 'manage_approve', 'manage_reject')),  # this is wrong ...
        ) + BSimpleItem.__ac_permissions__

    _properties = BSimpleItem._properties + (
        {'id':'day',         'type':'date',    'mode':'w'},
        )

    manage_options = (
        {'label':'Timesheet', 'action':'manage_main'},
        {'label':'Properties', 'action':'manage_propertiesForm'},
        ) + BSimpleItem.manage_options
    
    manage_main = PageTemplateFile('zpt/view_emptimesheet', globals())
    
    def __init__(self, id, title, date, entries=[], slots=None):
        self.id = id
        self.title = title
        self.day = date
        self.records = entries
        if self.records == []:
            assert slots != None, "Slots must be applied if no entries!"
            for i in range(0, 7):
                rec = {'day':self.day + (i - 6) }
                for slot in slots:
                    rec[slot.getId()] = slot.defaults[ rec['day'].dow() ]
                self.records.append( rec )
 
    def manage_edit(self, entries, REQUEST=None):
        """
        """
        # TODO: need some validation code here ...
        self.records = entries
	self._status('pending')
        if REQUEST:
            REQUEST.set('manage_tabs_message', 'Updated')
            return self.manage_main(self, REQUEST)

    def manage_approve(self, REQUEST=None):
        """ """
        assert self.status() == 'approval', "Wrong state: %s " % self.status()
        self.setStatus('approved')
        if REQUEST:
            return self.manage_main(self,  REQUEST)
        
    def manage_reject(self, REQUEST=None):
        """ """
        assert self.status() == 'Approval', "Wrong state: %s " % self.status()
        self.setStatus('rejected')
        if REQUEST:
            return self.manage_main(self,  REQUEST)
        
    def setStatus(self, status):
	# maybe we need to do some auto state changing later ...
        self._status(status)

    def sum(self, slot_id):
        return reduce( operator.add, map( lambda x, y=slot_id: x[y], self.records ) )

    def normalisedTime(self):
        hours = 0.0
        for slot in self.getTimesheetSlots():
            hours += self.sum(slot.getId()) * slot.ratio
        return hours

    def start_day(self):
        return self.day - 6

    def end_day(self):
        return self.day

    def slots(self):
        """
        return the slot's that this timesheet has snapshotted for
        """
        return filter(lambda x: x != 'day', self.records[0].keys())

    def getTimesheetSlots(self):
        """
        get slots associated with timesheet
        """
        return self.aq_parent.getTimesheetSlots()

    
    def __str__(self):
        """ lazy textual display ... """
        str = ''
        for day in self.records:
            str += day['day'].strftime('%Y/%m/%d')
            for slot in filter( lambda x: x != 'day', day.keys() ):
                str += '   %s (%.1d)' % (slot, day[slot])
            str += '\n'
        return str

AccessControl.class_init.InitializeClass(BLTimesheet)


def addTimesheetSlots(ob, event):
    """
    add default timesheet slots
    """
    factory = ob.manage_addProduct['BastionLedger'].manage_addBLTimesheetSlot
    factory('normal',   title='Normal',   defaults=[  0, 8.0, 8.0, 8.0, 8.0, 8.0,   0]) 
    factory('leave',    title='Leave',    defaults=[  0, 8.0, 8.0, 8.0, 8.0, 8.0,   0]) 
    factory('sick',     title='Sickness', defaults=[  0, 8.0, 8.0, 8.0, 8.0, 8.0,   0])
    factory('overtime', title='Overtime', defaults=[8.0, 4.0, 4.0, 4.0, 4.0, 4.0, 8.0])


def addPaySlip(ob, event):
    """
    go do our summated totals
    """
    if not ob.valid_txn_id():
        raise UnexpectedTransaction, (ob.txn_id, str(ob.blTransaction()))
    ob.calculate_running_totals()


#
# these are to be removed once conversions completed ...
#
class BLEmployeeEntriesFolder(BObjectManager): pass
class BLEmployeeTimesheetFolder(BObjectManager): pass


