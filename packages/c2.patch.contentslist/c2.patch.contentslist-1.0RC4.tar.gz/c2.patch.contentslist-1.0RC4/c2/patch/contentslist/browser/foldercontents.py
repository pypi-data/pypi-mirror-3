
from Acquisition import aq_parent, aq_inner
from plone.app.content.browser.foldercontents import FolderContentsView \
                                as BaseFolderContentsView
from plone.app.content.browser.foldercontents import FolderContentsTable
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

try:
    import pkg_resources
    plone_version = pkg_resources.get_distribution('Plone').version
    if plone_version.startswith('3'):
        PLONE3 = True
    else:
        PLONE3 = False
except:
    PLONE3 = False


class FolderContentsView(BaseFolderContentsView):
    """
    """
    template = ViewPageTemplateFile('folder_contents.pt')
    plone3_template = ViewPageTemplateFile('plone3_folder_contents.pt')
    # TODO: 

    def __call__(self, *args, **kw):
        # super(FolderContentsView, self).__call__(self, *args, **kw)
        if PLONE3:
            return self.plone3_template()
        else:
            return self.template()

    def is_listing_reverse(self):
        try:
            field = self.context.getField('is_listing_reverse', None)
        except AttributeError:
            return False
        if field is None:
            return False
        return field.get(self.context)

    def contents_table(self):
        contentFilter={}
        if self.is_listing_reverse():
            contentFilter['sort_order'] = 'reverse'
        table = FolderContentsTable(aq_inner(self.context), self.request,
                                contentFilter=contentFilter)
        return table.render()

