from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import ReferenceField
from Products.Archetypes.atapi import StringField
from Products.Archetypes.atapi import SelectionWidget
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget
from Products.CMFCore.permissions import ManagePortal
from Products.PloneTemplates.config import TEMPLATE_INHERIT_MODE

PloneTemplatesMixinSchema = Schema((
            ReferenceField('templates', 
                     multiValued=True,
                     write_permission=ManagePortal,
                     allowed_types=('Template',),
                     schemata='Templates',
                     relationship='EnablesTemplate',
                     widget=ReferenceBrowserWidget(label_msgid="label_templates",
                                      description_msgid="help_templates",
                                      i18n_domain="PloneTemplates",
                                      force_close_on_insert=True,
                                      label="", populate=1,  description="")),
        StringField('inheritTemplates',
                     vocabulary=TEMPLATE_INHERIT_MODE,
                     default='1',
                     write_permission=ManagePortal,
                     enforceVocabulary=True,
                     schemata='Templates',
                     widget=SelectionWidget(label_msgid="label_inheritTemplates",
                                      description_msgid="help_inheritTemplates",
                                      i18n_domain="PloneTemplates",
                                      label="", description=""))
            ))
