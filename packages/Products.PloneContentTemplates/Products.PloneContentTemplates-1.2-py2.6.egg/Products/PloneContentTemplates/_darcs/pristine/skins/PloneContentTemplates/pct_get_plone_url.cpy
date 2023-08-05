## Script (Python) "pct_get_plone_url.py"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=object
##title=
##

referenced = object
steps = []

while 1:
    if referenced.meta_type == 'Plone Site':
        break
    else:
        steps.append(referenced.id)
    referenced = referenced.getParentNode()

steps.reverse()
# Assuming that all Plone objects have IDs that are valid in URLs
return '/'.join(steps)
