## Controller Python Script "part_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=unit,weight,onhand,sellprice,listprice,lastcost,inventory_accno,income_accno,expense_accno,id=''
##title=edit part quantity and price details
##
REQUEST=context.REQUEST
 
if not id:
    id = context.getId()

new_context = context.portal_factory.doCreate(context, id)

new_context.edit_prices(unit, weight, onhand, sellprice, listprice, lastcost, 
    	                inventory_accno, income_accno, expense_accno)

context.plone_utils.addPortalMessage('Properties Updated')
return state.set(context=new_context)

