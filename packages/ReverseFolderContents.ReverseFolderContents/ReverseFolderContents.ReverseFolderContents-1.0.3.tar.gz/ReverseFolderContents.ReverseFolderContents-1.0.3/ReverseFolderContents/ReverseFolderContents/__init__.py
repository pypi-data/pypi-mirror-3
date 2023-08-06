from plone.app.content.browser.foldercontents import FolderContentsTable

old = FolderContentsTable.contentsMethod

def get(self, context):
    method = old.im_func(self)
    class callme:
        def __init__(self, method, context):
            self.method = method
            self._context = context
        def __call__(self, *args, **kw):
            result = self.method(*args, **kw)
            result = list(result)
            if self._context.REQUEST.get('reversedFolderContents', False):
                result.reverse()
            return result
    return callme(method, context)

def contentsMethod(self):
    if getattr(self.context.aq_base, 'getEnableReverseFolderContents', lambda: False)():
        return get(self, self.context)
    else:
        return old(self)

FolderContentsTable.contentsMethod = contentsMethod

from Products.Archetypes.atapi import BooleanField, BooleanWidget
from Products.CMFCore.permissions import ModifyPortalContent

from messages import RFCMF as _

enableReverseFolderContents = BooleanField('enableReverseFolderContents',
                                           default=False, languageIndependent=True, title=_(u'Reverse contents'),
                                           description=_(u'Setting this will reverse the folder contents listing'),
                                           widget=BooleanWidget(visible={'view':'invisible', 'edit':'visible'},
                                                                description=_(u'Reverse folder contents listing'),
                                                                label=_(u'Reverse contents')),
                                           schemata='settings', isMetaData=True
                                           )

from plone.app.folder import folder

folder.ATFolder.schema.addField(enableReverseFolderContents.copy())

from Products.Archetypes.ClassGen import generateMethods

generateMethods(folder.ATFolder, folder.ATFolder.schema.fields())

from Products.ATContentTypes.content.schemata import finalizeATCTSchema

finalizeATCTSchema(folder.ATFolder.schema, folderish=True, moveDiscussion=False)

from plone.app.portlets.portlets import navigation

OldQueryBuilder = navigation.QueryBuilder

class CustomQueryBuilder(OldQueryBuilder):
    """Custom query builder to reverse contents in folders."""

    def __call__(self):
        query = OldQueryBuilder.__call__.im_func(self)
        reverse = getattr(self.context, 'getEnableReverseFolderContents', lambda: None)()
        if reverse:
            sort_order = query.get('sort_order', '')
            if not sort_order or sort_order.startswith('asc'):
                query['sort_order'] = 'descending'
            if sort_order.startswith('rev') or sort_order.startswith('des'):
                query['sort_order'] = 'ascending'
        return query

navigation.QueryBuilder = CustomQueryBuilder
            
