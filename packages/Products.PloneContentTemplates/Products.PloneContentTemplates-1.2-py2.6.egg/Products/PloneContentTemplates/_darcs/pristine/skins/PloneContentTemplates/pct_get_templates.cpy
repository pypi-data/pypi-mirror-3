## Script (Python) "pct_get_templates.py"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##

# Alternative method of retrieving templates, will
# return all objects in the templates folder as
# possible templates.
#
# return context.templates.contentValues()
return map(lambda x: x.getObject(), context.portal_catalog(Subject='content-template'))
