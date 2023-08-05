from Products.CMFCore.utils import UniqueObject 
from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
import transaction
from Acquisition import aq_base

class PloneTemplatesTool(UniqueObject, SimpleItem,PropertyManager): 
    """ This tool provides some functions for Template objects """ 
    id = 'PloneTemplates_tool' 
    meta_type= 'PloneTemplates tool' 
    plone_tool = 1
        
    manage_options=PropertyManager.manage_options
    
    security = ClassSecurityInfo()
    
    def __init__(self):
        pass
    

    def instantiateTemplate(self,templateObject, targetObject, ownerId=None, postFunc=None, postArgs=()):

        itemsToCopy= templateObject.objectIds()
        if not itemsToCopy:
            raise 'Template is empty.'
        
        clipboard = templateObject.manage_copyObjects(itemsToCopy)
        
        # paste the items
        result = targetObject.manage_pasteObjects(clipboard)
        
        rootObjects=()
        
        #todo
        for r in result:
            #only do this with items that sits in the root
            if r['new_id'] in targetObject.objectIds():
                newObject = targetObject.restrictedTraverse(r['new_id'])
                rootObjects=rootObjects + (newObject,)
                # set ownership for this object and all subobjects
                try:
                    if ownerId:
                        self.plone_utils.changeOwnershipOf(newObject, ownerId, 1)
                        newObject.setCreators( (ownerId,))
                except:
                    pass
                
        if postFunc:
            postFunc(targetObject, rootObjects , postArgs)
            
        return targetObject, rootObjects
            
    def getTemplates(self, object):
        templates = self.fetchTemplates(object)
        
        allowed = object.allowedContentTypes()
            
        allowed_types = [t.id for t in allowed]
        res = [t for t in templates if self.checkTemplateValidity(t, allowed_types)]
        return res

        
    def initializePastedObject(self, context):
        """ When there is only one object instantiated by the template
        Reset it's creation flag so that when the item is edited, 
        Plone can recreate the id when needed
        """
        context.markCreationFlag()
        context.setId(context.aq_parent.generateUniqueId(context.portal_type))
        return context

                
    def checkTemplateValidity(self, template, allowed_types):
        # checks if the template can be instantiated in object
        # regarding the allowed content types.
        objs=template.objectIds()
        for o in objs:
            if not template[o].portal_type in allowed_types:
                return False
        return True
        
    
    def fetchTemplates(self, object):
        """ Get the templates that are available in an object """ 
        res=[]
        cont=1
        portal=self.portal_url.getPortalObject()
        
        cur_object = object
        while cont and not cur_object is portal:
            if hasattr(cur_object.aq_self, 'inheritTemplates'):
                templates = cur_object.getTemplates()
                if templates==None: templates=[]
                res=res+templates
                if cur_object.inheritTemplates=='0':
                    cont=0
                else:
                    cont=1
            cur_object = cur_object.aq_parent
            
        # check if the user has access permission to these
        # templates. reference retrieval doesn't do
        # permission checking.
        
        results = []
        mtool = self.portal_url.getPortalObject().portal_membership
        for r in res:
            if mtool.checkPermission('View', r) and r not in results:
                results.append(r)

        return results
        
        
InitializeClass(PloneTemplatesTool)
