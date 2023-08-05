## Script (Python) "pretty_title_or_id"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=default=None
##title=
##
from Products.CMFCore.utils import getToolByName

putils = getToolByName(context, 'plone_utils')

if default is not None:
    return putils.pretty_title_or_id(context, default)

return putils.pretty_title_or_id(context)
