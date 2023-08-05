## Python Script "blshoppingcart_setId"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=id='',cookie='_CartId'
##title=embed shopping cart id into customer dialogue
if id:
    # set infinitely unexpiring cookie (payment processing can expire it ...)
    context.REQUEST.RESPONSE.setCookie(cookie, id, path='/')
else:
    context.REQUEST.RESPONSE.expireCookie(cookie)
