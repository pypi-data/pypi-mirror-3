from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from simplelayout.types.common.config import *
from simplelayout_schemas import imageSchema, finalize_simplelayout_schema
from Products.ATContentTypes.lib.constraintypes import ConstrainTypesMixinSchema
from Products.ATContentTypes.content.folder import ATFolder
from Products.CMFCore.permissions import View
from zope.interface import implements
from simplelayout.types.common.interfaces import IPage
from simplelayout.base.interfaces import ISimpleLayoutCapable
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import ModifyPortalContent


from archetypes.referencebrowserwidget.widget import ReferenceBrowserWidget

schema = Schema((
        
        ReferenceField('relatedItems',
           relationship = 'relatesTo',
           schemata='settings',
           multiValued = True,
           isMetadata = True,
           languageIndependent = False,
           index = 'KeywordIndex',
           write_permission = ModifyPortalContent,
           widget = ReferenceBrowserWidget(
                 allow_search = True,
                 allow_browse = True,
                 show_indexes = False,
                 force_close_on_insert = True,
                 i18n_domain="plone",
                 label="Related Items",
                 label_msgid="label_related_items",
                 description="",
                 description_msgid="",
                 visible = {'edit' : 'visible', 'view' : 'invisible' }
                 )
           )
),
)

page_schema = ATFolder.schema.copy() + ConstrainTypesMixinSchema.copy() \
    + schema.copy()

finalize_simplelayout_schema(page_schema, folderish=True)




class Page(ATFolder):
    """
    """
    implements(IPage, ISimpleLayoutCapable)
    security = ClassSecurityInfo()    

    schema = page_schema
    
    def getPageTypes(self):
        catalog = getToolByName(self, "portal_catalog")
        return catalog.uniqueValuesFor("page_types")

registerType(Page, PROJECTNAME)

