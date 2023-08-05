from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import StringField
from Products.Archetypes.atapi import TextAreaWidget
from Products.Archetypes.atapi import TextField
from Products.Archetypes.atapi import RichWidget
from Products.Archetypes.atapi import BooleanField
from Products.Archetypes.atapi import BooleanWidget
from Products.Archetypes.atapi import registerType
from Products.CMFCore.permissions import View

from Products.ATContentTypes.content.base import ATCTOrderedFolder
from Products.ATContentTypes.content.document import finalizeATCTSchema

from Products.ATContentTypes.lib.constraintypes import ConstrainTypesMixinSchema

schema = ATCTOrderedFolder.schema.copy() + ConstrainTypesMixinSchema + Schema((
    StringField('description',
                isMetadata=1,
                accessor='Description',
                searchable=1,                
                widget=TextAreaWidget(label='Description', description='Give a short description for this template.'),),
    BooleanField('showUsage',
                 default = False,
                 widget=BooleanWidget(label='Show template description and instructions', 
                                      description='When checked, a page with instructions for this template will be displayed before the actual template items are created.')),                
    TextField('usage',
                searchable=1,
                required=0,
                primary=1,
                default_output_type = 'text/x-html-safe',
                allowable_content_types=('text/html',),
                widget=RichWidget(allow_file_upload=0, label='Instructions for the user', 
                                  allow_format_edit=0,
                                  description="")),
        ))

finalizeATCTSchema(schema)

class Template(ATCTOrderedFolder):
    """A Template is a container that can hold any kind of content. After
the Template is registered in a folder (or any other template-aware
folderish item), a user can instantiate whatever is inside the
Template container by using the templates drop-down menu next to the
add item menu.
    """
    meta_type = 'Template'
    schema = schema
    _at_rename_after_creation = True    
    security = ClassSecurityInfo()

    security.declareProtected(View, "getAutoIcon")
    def getAutoIcon(self):
        """ Return the icon of the first contained object in this template """
        items = self.getFolderContents(contentFilter={'sort_on':'getObjPositionInParent'})
        if len(items)>0:
            return items[0].getIcon
        else:
            return self.content_icon

    security.declareProtected(View, "getAutoIconType")
    def getAutoIconType(self):
        items = self.getFolderContents(contentFilter={'sort_on':'getObjPositionInParent'})
        if len(items)>0:
            return items[0].portal_type
        else:
            return self.portal_type

registerType(Template, 'Products.PloneTemplates')
