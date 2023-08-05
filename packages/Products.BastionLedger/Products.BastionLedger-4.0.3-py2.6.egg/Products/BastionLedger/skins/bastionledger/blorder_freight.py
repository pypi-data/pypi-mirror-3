## Python Script "blorder_freight"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=calculate freight charges on order
##

#
# demo imports and variables ...
#

#from Products.BastionBanking.ZCurrency import ZCurrency

order = context
#address = order.shiptoaddress

#
# go and knock yourself out pricing your freight here ...
#

return order.blAccount().zeroAmount()
