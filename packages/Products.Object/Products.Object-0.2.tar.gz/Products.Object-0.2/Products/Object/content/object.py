"""Definition of the Object content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

# -*- Message Factory Imported Here -*-

from Products.Object.interfaces import IObject
from Products.Object.config import PROJECTNAME

ObjectSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

ObjectSchema['title'].storage = atapi.AnnotationStorage()
ObjectSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(
    ObjectSchema,
    folderish=True,
    moveDiscussion=False
)


class Object(folder.ATFolder):
    """A physical object"""
    implements(IObject)

    meta_type = "Object"
    schema = ObjectSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-

atapi.registerType(Object, PROJECTNAME)
