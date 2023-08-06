"""Definition of the Structured Document content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import document
from Products.ATContentTypes.content import schemata

from rer.structured_content import structured_contentMessageFactory as _
from rer.structured_content.interfaces import IStructuredDocument
from rer.structured_content.config import PROJECTNAME

StructuredDocumentSchema = folder.ATFolderSchema.copy() + document.ATDocumentSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

StructuredDocumentSchema['title'].storage = atapi.AnnotationStorage()
StructuredDocumentSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(
    StructuredDocumentSchema,
    folderish=True,
    moveDiscussion=False
)

StructuredDocumentSchema['relatedItems'].widget.visible = {'view': 'visible', 'edit': 'visible'}

class StructuredDocument(folder.ATFolder):
    """Description of the Example Type"""
    implements(IStructuredDocument)

    meta_type = "Structured Document"
    schema = StructuredDocumentSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    
    # -*- Your ATSchema to Python Property Bridges Here ... -*-

atapi.registerType(StructuredDocument, PROJECTNAME)
