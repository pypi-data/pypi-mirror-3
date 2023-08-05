from Products.Archetypes.ClassGen import generateMethods
from Products.PloneTemplates.TemplateSchema import PloneTemplatesMixinSchema
from Products.PloneTemplates.config import typesToPatch

# patch objects, see config.py
for klass, schema in typesToPatch:
    schema.addField(PloneTemplatesMixinSchema['templates'])
    schema.addField(PloneTemplatesMixinSchema['inheritTemplates'])
    generateMethods(klass, klass.schema.fields())


