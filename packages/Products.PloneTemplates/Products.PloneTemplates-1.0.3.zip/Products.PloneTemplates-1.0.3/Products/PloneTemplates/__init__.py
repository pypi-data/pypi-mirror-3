import sys
from Products.Archetypes.public import process_types, listTypes
from Products.CMFCore.utils import ContentInit
from Products.CMFCore.utils import ToolInit
from Products.PloneTemplates.Permissions import wireAddPermissions

from Products.PloneTemplates.config import PROJECTNAME


# Module aliases - we don't always get it right on the first try, but and we
# can't move modules around because things are stored in the ZODB with the
# full module path. However, we can create aliases for backwards compatability.
from Products.PloneTemplates import content
sys.modules['Products.PloneTemplates.Template'] = content.template

from zope.i18nmessageid import MessageFactory as _mf
MessageFactory = _mf("PloneTemplates")


def initialize(context):
    ##Import Types here to register them
    from Products.PloneTemplates.content import Template

    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)

    from Products.PloneTemplates.Permissions import permissions
    
    allTypes = zip(content_types, constructors)
    wireAddPermissions()
    for atype, constructor in allTypes:
        kind = "%s: %s" % (PROJECTNAME, atype.archetype_name)
        ContentInit(
            kind,
            content_types      = (atype,),
            permission         = permissions[atype.portal_type],
            extra_constructors = (constructor,),
            fti                = ftis,
            ).initialize(context)

    from Products.PloneTemplates.TemplateTool import PloneTemplatesTool
    ToolInit(
        'PloneTemplates tool', 
        tools=(PloneTemplatesTool,),  
        icon='tool.gif', ).initialize(context)

    # patch types
    import Products.PloneTemplates.PatchSchemas

