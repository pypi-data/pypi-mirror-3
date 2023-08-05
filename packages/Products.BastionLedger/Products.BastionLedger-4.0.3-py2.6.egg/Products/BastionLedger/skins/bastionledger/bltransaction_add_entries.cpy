## Controller Python Script "bltransaction_add_entries"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=effective, addentries=[],editentries=[], title='', description=''
##title=add entries to a transaction
##
from Products.BastionBanking.ZCurrency import ZCurrency
from Products.BastionLedger.utils import assert_currency
from Products.BastionLedger.BLEntry import manage_addBLEntry
from Products.BastionLedger.BLSubsidiaryEntry import manage_addBLSubsidiaryEntry

REQUEST = context.REQUEST

if REQUEST.has_key('form.button.AddEntries'):
    entries = addentries
else:
    entries = editentries

if context.modifiable():

    if context.status() in ('posted',):
        context.manage_unpost()

    id = context.getId()
    new_context = context.portal_factory.doCreate(context, id)

    new_context.editProperties(title, description, effective)
    
    # don't do entries with blank amounts ...
    for entry in filter(lambda x: getattr(x, 'amount', None), entries):
        try:
	    assert_currency(entry.amount)
        except:
            entry.amount = ZCurrency(entry.amount)

        # be paranoid in determining debit/credit values ...
        if entry.get('credit', False):
            entry.amount = -abs(entry.amount)
        else:
            entry.amount = abs(entry.amount)

	if REQUEST.has_key('form.button.AddEntries'):
            if entry.subsidiary:
                manage_addBLSubsidiaryEntry(new_context, entry.account, entry.amount, entry.title)
            else:
                manage_addBLEntry(new_context, entry.account, entry.amount, entry.title)
	elif REQUEST.has_key('form.button.EditEntries'):
            # yuk - acc path may or may not be ledger/accno
            if entry.account.find('/') != -1:
                ledid, accid = entry.account.split('/')
            else:
                accid = entry.account
                ledid = context.aq_parent.getId()
            e = new_context.entry(accid, ledid)
            if e is None:
                raise KeyError, '%s/%s' % (ledid, accid)
	    e.manage_changeProperties(title=entry.title,
                                      amount=entry.amount)

if REQUEST.has_key('form.button.AddEntries'):
    context.plone_utils.addPortalMessage('Added Entries')
elif REQUEST.has_key('form.button.EditEntries'):
    context.plone_utils.addPortalMessage('Updated Entries')

return state.set(context=new_context)

