## Script (Python) "instantiateTemplate"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=templateUID
##title=Instantiate template
##

try:
    templateObject = context.reference_catalog.lookupObject(templateUID)
except:
    state.setStatus('failure')
    return state.set(portal_status_message='Template not found')

ownerId=context.portal_membership.getAuthenticatedMember().id

targetObject, rootObjects = context.PloneTemplates_tool.instantiateTemplate(templateObject, context, ownerId)

# redirect to first root object

if len(rootObjects)==1:
    # go straight to edit but make it so that the auto-id-rename machinery becomes active when necessary
    object = rootObjects[0]
    object = context.PloneTemplates_tool.initializePastedObject(object)
    state.setContext(object)
    state.setNextAction('redirect_to_action:string:edit')
else:
    # go to the fview of the first item. let the user decide what to do with all instantiated objects.
    state.setContext(rootObjects[0])
    state.setNextAction('redirect_to_action:string:view')
    
return state.set(portal_status_message="Template '" + templateObject.title_or_id() + "' instantiated.")

