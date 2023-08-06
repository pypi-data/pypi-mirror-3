"""Definition of the Contact net address content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

# -*- Message Factory Imported Here -*-

from GrailTact.GrailTact.interfaces import IContactnetaddress
from GrailTact.GrailTact.config import PROJECTNAME

from VariousDisplayWidgets.VariousDisplayWidgets.widgets.URI import URIWidget

ContactnetaddressSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

    atapi.StringField(
        name='address',
        required=1,
        searchable=1,
        default='',
        validators=('isURL',),
        size=40,
        widget=URIWidget(),
    )

))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

ContactnetaddressSchema['title'].storage = atapi.AnnotationStorage()
ContactnetaddressSchema['title'].widget.visible = {'edit' : 'invisible', 'view':'visible'}
ContactnetaddressSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(
    ContactnetaddressSchema,
    folderish=True,
    moveDiscussion=False
)

from MegamanicEdit.MegamanicEdit import MegamanicEditable, tools

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

class Contactnetaddress(folder.ATFolder, MegamanicEditable.MegamanicEditable):
    """Description of the Example Type"""
    implements(IContactnetaddress)

    meta_type = "Contactnetaddress"
    schema = ContactnetaddressSchema

    security = ClassSecurityInfo()

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-

    security.declarePublic('getMegamanicEditableFields')
    def getMegamanicEditableFields(self):
        """Returns names of the fields we can edit."""
        return ('address', 'description')

    security.declarePublic('validateMainField')
    def validateMainField(self, address=''):
        """Validates that the value given is acceptable."""
        return not self.schema['address'].validate(address, self)

    def Title(self):
        """Returns a proper title."""
        return 'Net (web) address'

# Redundant to hvae InitializeClass?
InitializeClass(Contactnetaddress)
atapi.registerType(Contactnetaddress, PROJECTNAME)
tools.setup(Contactnetaddress)
