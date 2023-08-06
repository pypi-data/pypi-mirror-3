"""Definition of the Contact content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

# -*- Message Factory Imported Here -*-

#from GrailTact.GrailTact.interfaces import IContact
from GrailTact.GrailTact.config import PROJECTNAME

from MegamanicEdit.MegamanicEdit import MegamanicEditable, tools

ContactSchema = folder.ATFolderSchema.copy() + MegamanicEditable.templateObjectSchema.copy()
# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

ContactSchema['title'].storage = atapi.AnnotationStorage()
ContactSchema['title'].widget._properties['label'] = 'Fullname'
ContactSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(
    ContactSchema,
    folderish=True,
    moveDiscussion=False
)

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

class Contactlandingpage(MegamanicEditable.MegamanicEditableTemplateObject, folder.ATFolder, ):
    """Description of the Example Type"""

    meta_type = "Contactlandingpage"
    schema = ContactSchema

    security = ClassSecurityInfo()

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-

    security.declarePublic('getMegamanicEditableFields')
    def getMegamanicEditableFields(self):
        """Returns names of the fields we can edit."""
        return ('title', 'description')

    security.declarePublic('getMegamanicEditableFields')
    def getMegamanicEditableFields(self):
        """Returns names of the fields we can edit."""
        return ('title', 'description', 'createContentType')

    security.declarePublic('anonymousAllowedToViewEditWidget')
    def anonymousAllowedToViewEditWidget(self):
        """Returns true if anonymous can add."""
        return self.getAllowAnonymousAdd()

InitializeClass(Contactlandingpage)
atapi.registerType(Contactlandingpage, PROJECTNAME)
tools.setup(Contactlandingpage)
