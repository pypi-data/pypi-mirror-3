from Acquisition import aq_inner
from zope.app.component.hooks import getSite
from zope.security import checkPermission
from zope.interface import Interface
from zope.component import getUtility

from plone.memoize.view import memoize
from plone.registry.interfaces import IRegistry
from Products.Five.browser import BrowserView
from Products.ExternalEditor.ExternalEditor import EditLink

from collective.edm.listing.interfaces import IEDMListingSettings


class EditPopup(BrowserView):

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        request.RESPONSE.setHeader('Cache-Control', 'no-cache')
        request.RESPONSE.setHeader('Pragma', 'no-cache')

    def canreview(self):
        return len(self.gettransitions())>1

    def canedit(self):
        return checkPermission('cmf.ModifyPortalContent', self.context)

    def canexternaledit(self):
        return self.context.restrictedTraverse('@@externalEditorEnabled').available(bypasslock = True)

    def zopeeditlink(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IEDMListingSettings)
        return settings.downloadZopeedit

    @memoize
    def gettransitions(self):
        wtool = getSite().portal_workflow
        workflows = wtool.getWorkflowsFor(self.context)
        if len(workflows) == 0:
            return []

        workflow = workflows[0]
        transitions = wtool.listActionInfos(object=aq_inner(self.context))

        review_state = wtool.getInfoFor(self.context, 'review_state')
        current_state = workflow.states[review_state]
        choices = [{'title': current_state.title,
                    'id': review_state,
                    'state-id': review_state,
                    'current': True}]

        titles = []
        doubles = []
        for transition in [t for t in transitions if t['category'] == 'workflow']:
            state = workflow.states[transition['transition'].new_state_id]
            title = state.title
            choice = {'title': title,
                      'transition': transition['transition'].actbox_name,
                      'id': transition['id'],
                      'state-id': state.id,
                      'current': False}
            if title in titles:
                doubles.append(title)

            titles.append(title)
            choices.append(choice)

        for choice in choices:
            if choice['title'] in doubles:
                choice['title'] = choice['transition']

        return choices
