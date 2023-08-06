"""Definition of the Folder Deepening content type
"""

from zope.interface import implements, directlyProvides

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

from rer.structured_content import structured_contentMessageFactory as _
from rer.structured_content.interfaces import IFolderDeepening
from rer.structured_content.config import PROJECTNAME
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_parent
from Acquisition import aq_inner
from Products.ATContentTypes.interface import ISelectableConstrainTypes
from Products.CMFCore.PortalFolder import PortalFolderBase as PortalFolder
#ACQUIRE = -1 # acquire locallyAllowedTypes from parent (default)
#DISABLED = 0 # use default behavior of PortalFolder which uses the FTI information

FolderDeepeningSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

FolderDeepeningSchema['title'].storage = atapi.AnnotationStorage()
FolderDeepeningSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(
    FolderDeepeningSchema,
    folderish=True,
    moveDiscussion=False
)

FolderDeepeningSchema.changeSchemataForField('excludeFromNav', 'default')
FolderDeepeningSchema['relatedItems'].widget.visible = {'view': 'visible', 'edit': 'visible'}

class FolderDeepening(folder.ATFolder):
    """Description of the Example Type"""
    implements(IFolderDeepening)

    meta_type = "Folder Deepening"
    schema = FolderDeepeningSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    
#    def _ct_defaultConstrainTypesMode(self):
#       """Configure constrainTypeMode depending on the parent
#
#       ACQUIRE if parent support ISelectableConstrainTypes
#       DISABLE if not
#       """
#       
#       portal_factory = getToolByName(self, 'portal_factory', None)
#       if portal_factory is not None and portal_factory.isTemporary(self):
#           # created by portal_factory
#           parent = aq_parent(aq_parent(aq_parent(aq_inner(self))))
#       else:
#           parent = aq_parent(aq_inner(self))
#
#       if ISelectableConstrainTypes.providedBy(parent):
#           return ACQUIRE
#       else:
#           return DISABLED
#       
#    def allowedContentTypes(self, context=None):
#        """returns constrained allowed types as list of fti's
#        """
#        
#        if context is None:
#            context=self
#        mode = self.getConstrainTypesMode()
#        
#        if mode == DISABLED:
#            return PortalFolder.allowedContentTypes(self)
#
#        globalTypes = self.getDefaultAddableTypes(context)
#        
#        portal_factory = getToolByName(self, 'portal_factory', None)
#        if portal_factory is not None and portal_factory.isTemporary(self):
#            # created by portal_factory
#            parent = aq_parent(aq_parent(aq_parent(aq_inner(self))))
#        else:
#            parent = aq_parent(aq_inner(self))
#        
#        allowed = list(parent.getLocallyAllowedTypes())
#        ftis = [ fti for fti in globalTypes if fti.getId() in allowed ]
#
#        return ftis

atapi.registerType(FolderDeepening, PROJECTNAME)
