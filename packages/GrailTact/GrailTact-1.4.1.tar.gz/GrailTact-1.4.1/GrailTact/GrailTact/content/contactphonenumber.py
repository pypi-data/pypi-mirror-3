"""Definition of the Contact phone number content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

# -*- Message Factory Imported Here -*-

from GrailTact.GrailTact.interfaces import IContactphonenumber
from GrailTact.GrailTact.config import PROJECTNAME

ContactphonenumberSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    atapi.StringField(
        name='phone',
        required=1,
        searchable=1,
        default='',
        validators=('isInternationalPhoneNumber',),
        size=40,
    )

))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

ContactphonenumberSchema['title'].storage = atapi.AnnotationStorage()
ContactphonenumberSchema['title'].widget.visible = {'edit' : 'invisible', 'view':'visible'}
ContactphonenumberSchema['description'].storage = atapi.AnnotationStorage()


schemata.finalizeATCTSchema(
    ContactphonenumberSchema,
    folderish=True,
    moveDiscussion=False
)

from MegamanicEdit.MegamanicEdit import MegamanicEditable, tools

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

class Contactphonenumber(folder.ATFolder, MegamanicEditable.MegamanicEditable):
    """Description of the Example Type"""
    implements(IContactphonenumber)

    meta_type = "Contactphonenumber"
    schema = ContactphonenumberSchema

    security = ClassSecurityInfo()

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-

    security.declarePublic('getMegamanicEditableFields')
    def getMegamanicEditableFields(self):
        """Returns names of the fields we can edit."""
        return ('phone', 'description')

    security.declarePublic('validateMainField')
    def validateMainField(self, phone=''):
        """Validates that the value given is acceptable."""
        return not self.schema['phone'].validate(phone, self)

    def Title(self):
        """Returns a proper title."""
        return 'Phone number'

InitializeClass(Contactphonenumber)
atapi.registerType(Contactphonenumber, PROJECTNAME)
tools.setup(Contactphonenumber)
