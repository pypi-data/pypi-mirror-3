from Products.CMFCore.permissions import setDefaultRoles
from Products.Archetypes.public import listTypes
from Products.PloneTemplates.config import PROJECTNAME


TYPE_ROLES = ('Manager', 'Owner')

permissions = {}
def wireAddPermissions():
    """Creates a list of add permissions for all types in this project
    
    Must be called **after** all types are registered!
    """
    global permissions
    issue_types = listTypes(PROJECTNAME)
    for itype in issue_types:
        permission = "%s: Add %s" % (PROJECTNAME, itype['portal_type'])
        setDefaultRoles(permission, TYPE_ROLES)
        
        permissions[itype['portal_type']] = permission
    return permissions
