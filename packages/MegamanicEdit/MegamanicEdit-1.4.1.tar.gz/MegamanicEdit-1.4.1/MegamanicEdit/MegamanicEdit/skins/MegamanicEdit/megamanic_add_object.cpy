## Script (Python) "validate_base"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=adding=False
##

from Products.Archetypes import PloneMessageFactory as _
from Products.Archetypes.utils import addStatusMessage

from MegamanicEdit.MegamanicEdit.FakeRequest import FakeRequest

errors = {}
request = context.REQUEST
edited_objects = request.get('edited_objects', [])

import random

if not context.anonymousAllowedToViewEditWidget():
   # If not anonymous is allowed to add
   # check that a user can add things
   raise 'x'

if edited_objects:
    created_object = None
    if 'added' not in context.objectIds():
        context.invokeFactory(id='added', type_name='Large Plone Folder')
        context['added'].title = 'Added objects'
	context.layout = 'megamanic_listing'
    added_folder = context['added']
    for index in range(len(edited_objects)):
        object_name = edited_objects[index]
        fake_request = FakeRequest()
        for key in request.keys():
            if key.startswith(object_name):
                field_name = key[len(object_name)+1:]
                fake_request.set(field_name, request[key])
        if index == 0 and object_name == context.getId():
            content_type = context.getCreateContentType()
            id = content_type.replace(' ', '-') + '-' + str(random.random())
            added_folder.invokeFactory(id=id, type_name=content_type)
            try:
                created_object = object = added_folder[id]
            except KeyError:
                raise str((id, context.objectIds()))
            # Set subject for added object
            created_object.setSubject(context.Subject())
        else:
            portal_type = context[object_name].portal_type
            id = context[object_name].getId()
            created_object.invokeFactory(id=id, type_name=portal_type)
            object = created_object[id]
        object.processForm(REQUEST=fake_request, data=1, metadata=0)

if errors:
    message = _(u'Please correct the indicated errors.')
    addStatusMessage(request, message, type='error')
    return state.set(status='failure', errors=errors)
else:
    if not adding:
        message = _(u'Object registered.')
        addStatusMessage(request, message)
    return state
