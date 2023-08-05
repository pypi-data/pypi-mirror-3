from Products.Archetypes.public import DisplayList

PROJECTNAME = "Products.PloneTemplates"
SKINS_DIR = 'skins'

GLOBALS = globals()

TEMPLATE_INHERIT_MODE=DisplayList((
    ('1', 'Add to available templates from parent folders'), ('0', 'Redefine new set of templates for this folder'),))

# Add the types that will be patched to support templates
from Products.ATContentTypes.content.folder import ATFolder, ATFolderSchema

typesToPatch = [ (ATFolder, ATFolderSchema) ]

