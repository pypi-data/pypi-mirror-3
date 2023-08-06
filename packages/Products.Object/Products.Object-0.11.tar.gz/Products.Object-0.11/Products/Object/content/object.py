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
            description = 'Primary reference',
            label = _(u'Imported Primary reference', default=u'Primary reference')
        )),
    
    StringField('object_number',
        searchable=True,
        write_permission = ModifyPortalContent,
        isMetadata = True,
        schemata = _(u"private", default=u"private"),
        widget = StringWidget(
            description = u'Nummer van de Object',
            label = _(u'Imported Object number reference', default=u'Objectnummer')
        )),

    StringField('object_name',
        searchable=True,
        write_permission = ModifyPortalContent,
        isMetadata = True,
        schemata = _(u"private", default=u"private"),
        widget = StringWidget(
            description = u'Naam van de Object',
            label = _(u'Imported Object name reference', default=u'Objectnaam')
        )),
        
    StringField('production_place',
        searchable=True,
        write_permission = ModifyPortalContent,
        widget = StringWidget(
            description = 'Vervaardigingsplaats',
            label = _(u'City of production', default=u'Vervaardigingsplaats')
        )),
    
    StringField('production_date_start',
        searchable=True,
        write_permission = ModifyPortalContent,
        widget = StringWidget(
            description = 'Jaar van de begin van productie',
            label = _(u'start of production', default=u'Productiedatum begin')
        )),
    
    StringField('production_date_end',
        searchable=True,
        write_permission = ModifyPortalContent,
        widget = StringWidget(
            description = 'Jaar van de eind van productie',
            label = _(u'end of production', default=u'Productiedatum eind')
        )),
    
    StringField('period',
        searchable=True,
        write_permission = ModifyPortalContent,
        widget = StringWidget(
            description = 'Periode van de stuk',
            label = _(u'period', default=u'Periode')
        )),
    
    StringField('materials',
        searchable=True,
        write_permission = ModifyPortalContent,
        widget = StringWidget(
            description = 'Materiaal van de Object',
            label = _(u'Materials', default=u'Materiaal')
        )),
    
    StringField('dimentions',
        searchable=True,
        write_permission = ModifyPortalContent,
        widget = StringWidget(
            description = 'Afmeting van de Object',
            label = _(u'Dimentions', default=u'Afmeting')
        )),
    
    StringField('creator',
        searchable=True,
        write_permission = ModifyPortalContent,
        widget = StringWidget(
            description = 'Schepper/Vervaardiger van de Object',
            label = _(u'Creator of the object', default=u'Schepper/Vervaardiger')
        )),
    
    TextField('licence',
        searchable=True,
        write_permission = ModifyPortalContent,
        default = u'<a href="http://creativecommons.org/licenses/by-nc-sa/3.0/nl/"> CC by-nc-sa </a>',
        widget = RichWidget(
            description = 'Licentie',
            label = _(u'Label text', default=u'Licentie')
        )),

    TextField('label_text',
        searchable=True,
        schemata = _(u"private", default=u"private"),
        write_permission = ModifyPortalContent,
        widget = TextAreaWidget(
            description = 'Prive-notities over de Object',
            label = _(u'Label text', default=u'Prive-notities')
        )),
    
    BooleanField('for_sale',
        searchable = False,
        write_permission = ModifyPortalContent,
        default = False,
        widget = BooleanWidget(
            description = 'Is dit Object te koop?',
            label = _(u'For Sale', default=u'Te koop')
        )),
    
    FixedPointField('price',
        searchable=True,
        write_permission = ModifyPortalContent,
        widget = DecimalWidget(
            description = 'Prijs van de Object in EUR. (ie: 12,99)',
            label = _(u'Price', default=u'Prijs')
        )),
    
    BooleanField('in_exhibition',
        searchable = False,
        write_permission = ModifyPortalContent,
        default = False,
        widget = BooleanWidget(
            description = 'Is dit porselein in de tentoonstelling',
            label = _(u'For Sale', default=u'Tentoonstelling')
        )),
))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

ObjectSchema['title'].storage = atapi.AnnotationStorage()
ObjectSchema['description'].storage = atapi.AnnotationStorage()
ObjectSchema['text'].storage = atapi.AnnotationStorage()
ObjectSchema['priref'].storage = atapi.AnnotationStorage()
ObjectSchema['object_number'].storage = atapi.AnnotationStorage()
ObjectSchema['object_name'].storage = atapi.AnnotationStorage()
ObjectSchema['production_place'].storage = atapi.AnnotationStorage()
ObjectSchema['production_date_start'].storage = atapi.AnnotationStorage()
ObjectSchema['production_date_end'].storage = atapi.AnnotationStorage()
ObjectSchema['period'].storage = atapi.AnnotationStorage()
ObjectSchema['materials'].storage = atapi.AnnotationStorage()
ObjectSchema['dimentions'].storage = atapi.AnnotationStorage()
ObjectSchema['creator'].storage = atapi.AnnotationStorage()
ObjectSchema['licence'].storage = atapi.AnnotationStorage()
ObjectSchema['label_text'].storage = atapi.AnnotationStorage()
ObjectSchema['for_sale'].storage = atapi.AnnotationStorage()
ObjectSchema['price'].storage = atapi.AnnotationStorage()
ObjectSchema['in_exhibition'].storage = atapi.AnnotationStorage()


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
    period = atapi.ATFieldProperty('period')
    materials = atapi.ATFieldProperty('materials')
    dimentions = atapi.ATFieldProperty('dimentions')
    creator = atapi.ATFieldProperty('creator')
    licence = atapi.ATFieldProperty('licence')
    label_text = atapi.ATFieldProperty('label_text')
    for_sale = atapi.ATFieldProperty('for_sale')
    price = atapi.ATFieldProperty('price')
    in_exhibition = atapi.ATFieldProperty('in_exhibition')
    

atapi.registerType(Object, PROJECTNAME)
