## Script (Python) "pct_add_object.py"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=template=None,new_object_context=None,count=0
##title=
##

from random import random

from Products.PloneContentTemplates import PCTMessageFactory as _

if hasattr(template, 'startswith'):
   # We have a path
   template = context.restrictedTraverse(template)
   redirect = True
else:
   # template=template
   redirect = False

if new_object_context is None:
    new_object_context = context

if template.absolute_url() == new_object_context.absolute_url():
   context.plone_utils.addPortalMessage(_('Sorry, cannot add template in template'), type='error')
   context.REQUEST.RESPONSE.redirect(context.absolute_url() + '/pct_add')
   return

id = str(random())
new_object_context.invokeFactory(template.portal_type, id)
new_object = new_object_context[id]
for field in template.Schema().fields():
    field_name = field.getName()
    if field_name in ('id', 'creators', 'contributors',
	'creation_date', 'modification_date',
	# Something stupid..
	'eventType'): continue
    if field_name == 'subject':
        copy = ()
        for value in field.getAccessor(template)():
            if value != 'content-template':
                copy += (value,)
        if copy:
            new_object.setSubject(copy)
    else:
        field.getMutator(new_object)(field.getAccessor(template)())

if template.portal_type.lower().find('folder') > -1:
    for object in template.contentValues():
        new_object.pct_add_object(template=object,new_object_context=new_object,count=count)

if redirect:
   new_object_context.REQUEST.RESPONSE.redirect(new_object.absolute_url() + '/base_edit')
