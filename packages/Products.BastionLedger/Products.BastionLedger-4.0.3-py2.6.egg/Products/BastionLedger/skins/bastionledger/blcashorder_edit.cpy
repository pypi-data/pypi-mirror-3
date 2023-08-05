## Controller Python Script "blcashorder_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=orderdate,reqdate,buysell,taxincluded=0,discount=0.0,notes='',parts=[],title='', contact='', email='',id=''
##title=edit an order
##
request = context.REQUEST

if request.has_key('form.button.CreateAccount'):
    orderbook_id = request['orderbook_id']
    account = context.upgradeToAccount(orderbook_id)
    context.plone_utils.addPortalMessage('Created Account %s in %s Orderbook' % (account.prettyTitle(), orderbook_id))
    return state

if not id:
    id = context.getId()
new_context = context.portal_factory.doCreate(context, id)


new_context.manage_edit(title, orderdate, reqdate, notes, discount, taxincluded, 
                        contact, email, context.shiptoaddress)

if new_context.buysell != buysell:
    new_context.manage_changeProperties(buysell=buysell)

    # we need to toggle sell/buy price on the order lines
    part_ids = map(lambda x: x.part_id, new_context.objectValues('BLOrderItem'))
    new_context.blorder_deleteitems(ids=new_context.objectIds('BLOrderItem'))
    new_context.blorder_additems(part_ids=part_ids)
else:
    for part in parts:
        orderitem = getattr(new_context, part['id'])
        orderitem.manage_edit(orderitem.title, part['quantity'], discount, part['unit'], None, part['note'])

# auto upgrade/downgrade status
new_context.setStatus()


context.plone_utils.addPortalMessage('Edited cash order')
return state.set(context=new_context)
