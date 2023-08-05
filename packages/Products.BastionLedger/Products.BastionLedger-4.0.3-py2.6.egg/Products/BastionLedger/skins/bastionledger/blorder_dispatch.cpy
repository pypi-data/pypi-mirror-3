## Controller Python Script "blorder_dispatch"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=send order to delivery department to forward to customer
##
REQUEST=context.REQUEST

# the default is very dumb - it just places the order in the inventory's queue
# so that a warehouse person can fill and freight it

context.aq_parent.blInventory().dispatch(context)

return state.set()

