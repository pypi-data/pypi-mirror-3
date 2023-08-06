"""Definition of the Contact content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

# -*- Message Factory Imported Here -*-

from MegamanicEdit.MegamanicEdit import MegamanicEditable, tools

from GrailTact.GrailTact.interfaces import IContact
from GrailTact.GrailTact.config import PROJECTNAME

ContactSchema = folder.ATFolderSchema.copy() + atapi.Schema((

)) 

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

ContactSchema['title'].storage = atapi.AnnotationStorage()
ContactSchema['title'].label = 'Fullname'
ContactSchema['title'].widget.label = 'Fullname'
ContactSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(
    ContactSchema,
    folderish=True,
    moveDiscussion=False
)

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

class Contact(folder.ATFolder, MegamanicEditable.MegamanicEditable):
    """Description of the Example Type"""
    implements(IContact)

    meta_type = "Contact"
    schema = ContactSchema

    security = ClassSecurityInfo()

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-

    def manage_afterAdd(self, a, b):
        """Hook to add some default things."""
        pass
        # self.portal_types.constructContent('Contact email address', self, 'email_address')

    security.declarePublic('getMegamanicEditableFields')
    def getMegamanicEditableFields(self):
        """Returns names of the fields we can edit."""
        return ('title', 'description')

    def getEmailAddresses(self):
        """Returns the email adresses contained."""
        return filter(None, map(lambda x: x.getEmail(), self.objectValues('Contactemailaddress')))

InitializeClass(Contact)
atapi.registerType(Contact, PROJECTNAME)
tools.setup(Contact)
