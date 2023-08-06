import urllib

from Acquisition import aq_inner
from zope.component import getMultiAdapter
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.i18n import translate
from zope.publisher.browser import BrowserView
from zope.interface import implements

from plone.app.content.browser.foldercontents import FolderContentsView as FolderContentsViewOrig
from plone.app.content.browser.foldercontents import FolderContentsTable as FolderContentsTableOrig
from plone.app.content.browser.tableview import TableKSSView
from plone.app.content.browser.tableview import Table as TableOrig
from plone.memoize import instance
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.CMFPlone.utils import pretty_title_or_id, isExpired

from collective.edm.listing.interfaces import IEDMListing, IEDMListingSupplColumn
from collective.edm.listing.utils import get_workflow_policy
from zope.component import getAdapters


class FolderContentsView(FolderContentsViewOrig):
    """
    """
    implements(IEDMListing)

    def __init__(self, context, request):
        # avoids setting IContentsPage on our FolderContentsView
        BrowserView.__init__(self, context, request)

    def contents_table(self):
        table = FolderContentsTable(aq_inner(self.context), self.request)
        return table.render()


class FolderContentsTable(FolderContentsTableOrig):
    """
    The foldercontents table renders the table and its actions.
    """

    def __init__(self, context, request, contentFilter=None):
        self.context = context
        self.request = request
        self.contentFilter = contentFilter is not None and contentFilter or {}
        if self.request.get('sort_order', False):
            self.contentFilter['sort_order'] = self.request['sort_order']
        if self.request.get('sort_on', False):
            # if there is a sortable_xx index matching
            # (ex : sortable_title, sortable_creator), use it
            catalog = getToolByName(self.context, 'portal_catalog')
            sortable_index = 'sortable_%s' % self.request['sort_on'].lower()
            if sortable_index in catalog.indexes():
                self.contentFilter['sort_on'] = sortable_index
            else:
                self.contentFilter['sort_on'] = self.request['sort_on']

        self.items = self.folderitems()

        url = context.absolute_url()
        view_url = url + '/edm_folder_listing'
        self.table = Table(request, url, view_url, self.items,
                           show_sort_column=self.show_sort_column,
                           buttons=self.buttons, context=context)


class Table(TableOrig):
    render = ViewPageTemplateFile("templates/table.pt")
    batching = ViewPageTemplateFile("templates/batching.pt")

    def __init__(self, *args, **kwargs):
        context = kwargs['context']
        del kwargs['context']
        super(Table, self).__init__(*args, **kwargs)
        self.context = context
        self.mtool = getToolByName(context, 'portal_membership')
        self.wtool = getToolByName(context, 'portal_workflow')
        self.portal_url = getToolByName(context, 'portal_url')()
        self.icon_edit = self.portal_url + '/edit.png'
        self.icon_cut = self.portal_url + '/cut_icon.png'
        self.icon_copy = self.portal_url + '/copy_icon.png'
        self.icon_delete = self.portal_url + '/delete_icon.png'
        self.icon_history = self.portal_url + '/history.png'
        self.icon_download = self.portal_url + '/download_icon.png'
        self.listingrights = self.context.unrestrictedTraverse('@@edmlistingrights')
        self.listingrights.update()
        self.brains = []
        self.wf_policy = get_workflow_policy(self.context)
        for item in self.items:
            if not 'brain' in item:
                # bypass items not in page
                continue

            if 'view_url' in item and item['view_url'].endswith('folder_contents'):
                item['view_url'] = item['view_url'].replace('/folder_contents', '')

            if 'url_href_title' in item and item['url_href_title'].endswith(': '):# todo: fix it in plone
                item['url_href_title'] = item['url_href_title'][:-2]

            if self.wf_policy and item['brain'].review_state:
                chain = self._getPlacefulChainForType(item['brain'].portal_type)
                if chain:
                    workflow = self.wtool[chain[0]]
                    state = workflow.states.get(item['brain'].review_state, None)
                    if state:
                        item['state_title'] = state.title

            self.brains.append(item['brain'])

        self.sortable_columns = self.listingrights.sortable_columns()
        self.show_sort_column = not self.sortable_columns and self.listingrights.globally_show_sort()
        suppl_columns = getAdapters((self.context, self.request, self),
                                    IEDMListingSupplColumn)
        self.suppl_columns = [col for name, col in suppl_columns]

    @instance.memoize
    def _getPlacefulChainForType(self, portal_type):
        return self.wf_policy.getPlacefulChainFor(portal_type, start_here=False)

    @instance.memoize
    def getMemberInfo(self, member):
        return self.mtool.getMemberInfo(member)

    def showDownload(self):
        return self.listingrights.globally_show_download(self.brains)

    def downloadItemView(self, item):
        download = self.listingrights.show_download(item['brain'])
        if download and not isinstance(download, basestring):
            download = 'download'

        return download

    def checkEdit(self):
        return self.listingrights.globally_can_edit(self.brains)

    def checkEditItem(self, item):
        return self.listingrights.can_edit(item['brain'])

    def checkRemove(self):
        return self.listingrights.globally_can_cut(self.brains)

    def checkRemoveItem(self, item):
        """ can trash or cut """
        return self.listingrights.can_delete(item['brain'])

    def checkCopy(self):
        return self.listingrights.globally_can_copy(self.brains)

    def checkCopyItem(self, item):
        return self.listingrights.can_copy(item['brain'])

    def checkDelete(self):
        return self.listingrights.globally_can_delete(self.brains)

    def checkDeleteItem(self, item):
        return self.listingrights.can_delete(item['brain'])

    def useEditPopup(self, item):
        return self.listingrights.use_edit_popup(item['brain'])

    def showHistory(self):
        return self.listingrights.globally_show_history()

    def showItemHistory(self, item):
        return self.listingrights.show_history(item['brain'])

    def showState(self):
        return self.listingrights.globally_show_state(self.brains)

    def showSize(self):
        return self.listingrights.globally_show_size(self.brains)

    def showAuthor(self):
        return self.listingrights.globally_show_author()

    def itemSize(self, item):
        if not self.listingrights.show_size(item['brain']):
            return u""
        else:
            return item['size'] or u""

    def showModified(self):
        return self.listingrights.globally_show_modified()

    def listing_buttons(self):
        if not self.listingrights.show_folder_buttons():
            return []
        else:
            return self.buttons

    def arrow(self, sort_index):
        if sort_index != self.request.get('sort_on', None):
            return u""
        if self.request.get('sort_order', 'descending') == 'descending':
            return u"""<img class="sortdirection" src="%s/listing-arrowup.gif" />""" % self.portal_url
        else:
            return u"""<img class="sortdirection" src="%s/listing-arrowdown.gif" />""" % self.portal_url

