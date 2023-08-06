"""Definition of the Object content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.Archetypes.atapi import *
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import document
from Products.ATContentTypes.content import schemata
from Products.CMFCore.permissions import ModifyPortalContent, View
from Products.ATContentTypes import ATCTMessageFactory as _

# -*- Message Factory Imported Here -*-

from Products.Object.interfaces import IObject
from Products.Object.config import PROJECTNAME

ObjectSchema = folder.ATFolderSchema.copy() + document.ATDocumentSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-
    StringField('priref',
        searchable=True,
        isMetadata = True,
        schemata = _(u"private", default=u"private"),
        write_permission = ModifyPortalContent,
        widget = StringWidget(
            description = 'Imported Primary reference',
            label = _(u'Imported Primary reference', default=u'Primary reference')
        )),
    
    StringField('object_number',
        searchable=True,
        write_permission = ModifyPortalContent,
        isMetadata = True,
        schemata = _(u"private", default=u"private"),
        widget = StringWidget(
            description = u'Imported Object number reference',
            label = _(u'Imported Object number reference', default=u'Object number')
        )),

    StringField('object_name',
        searchable=True,
        write_permission = ModifyPortalContent,
        isMetadata = True,
        schemata = _(u"private", default=u"private"),
        widget = StringWidget(
            description = u'Imported Object name reference',
            label = _(u'Imported Object name reference', default=u'Object name')
        )),
        
    StringField('production_place',
        searchable=True,
        write_permission = ModifyPortalContent,
        widget = StringWidget(
            description = 'City of production',
            label = _(u'City of production', default=u'Production place')
        )),
    
    StringField('production_date_start',
        searchable=True,
        write_permission = ModifyPortalContent,
        widget = StringWidget(
            description = 'Start of production, could be a year or a full date with the format dd/mm/yyyy',
            label = _(u'start of production', default=u'Production date')
        )),
    
    StringField('production_date_end',
        searchable=True,
        write_permission = ModifyPortalContent,
        widget = StringWidget(
            description = 'End of production, could be a year or a full date with the format dd/mm/yyyy',
            label = _(u'end of production', default=u'Production date')
        )),
    
    StringField('materials',
        searchable=True,
        write_permission = ModifyPortalContent,
        widget = StringWidget(
            description = 'Materials the object is made of',
            label = _(u'Materials', default=u'Materials')
        )),
    
    StringField('dimentions',
        searchable=True,
        write_permission = ModifyPortalContent,
        widget = StringWidget(
            description = 'Dimentions of the object',
            label = _(u'Dimentions', default=u'Dimentions')
        )),
    
    StringField('creator',
        searchable=True,
        write_permission = ModifyPortalContent,
        widget = StringWidget(
            description = 'A person or company',
            label = _(u'Creator of the object', default=u'Creator')
        )),

    TextField('label_text',
        searchable=True,
        schemata = _(u"private", default=u"private"),
        write_permission = ModifyPortalContent,
        widget = TextAreaWidget(
            description = 'Extra text about the object',
            label = _(u'Label text', default=u'Label text')
        )),
))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

ObjectSchema['title'].storage = atapi.AnnotationStorage()
ObjectSchema['description'].storage = atapi.AnnotationStorage()
ObjectSchema['priref'].storage = atapi.AnnotationStorage()
ObjectSchema['object_number'].storage = atapi.AnnotationStorage()
ObjectSchema['object_name'].storage = atapi.AnnotationStorage()
ObjectSchema['production_place'].storage = atapi.AnnotationStorage()
ObjectSchema['production_date_start'].storage = atapi.AnnotationStorage()
ObjectSchema['production_date_end'].storage = atapi.AnnotationStorage()
ObjectSchema['materials'].storage = atapi.AnnotationStorage()
ObjectSchema['dimentions'].storage = atapi.AnnotationStorage()
ObjectSchema['creator'].storage = atapi.AnnotationStorage()
ObjectSchema['label_text'].storage = atapi.AnnotationStorage()


schemata.finalizeATCTSchema(
    ObjectSchema,
    folderish=True,
    moveDiscussion=False
)


class Object(folder.ATFolder, document.ATDocument):
    """A physical object"""
    implements(IObject)

    meta_type = "Object"
    schema = ObjectSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    text = atapi.ATFieldProperty('text')
    # -*- Your ATSchema to Python Property Bridges Here ... -*-
    priref = atapi.ATFieldProperty('priref')
    object_number = atapi.ATFieldProperty('object_number')
    object_name = atapi.ATFieldProperty('object_name')
    production_place = atapi.ATFieldProperty('production_place')
    production_date_start = atapi.ATFieldProperty('production_date_start')
    production_date_end = atapi.ATFieldProperty('production_date_end')
    materials = atapi.ATFieldProperty('materials')
    dimentions = atapi.ATFieldProperty('dimentions')
    creator = atapi.ATFieldProperty('creator')
    label_text = atapi.ATFieldProperty('label_text')

atapi.registerType(Object, PROJECTNAME)
