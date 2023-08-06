from Acquisition import aq_inner, aq_parent

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.CMFPlone.utils import base_hasattr
from Products.CMFPlacefulWorkflow.PlacefulWorkflowTool import WorkflowPolicyConfig_id
from Products.CMFPlacefulWorkflow.interfaces.portal_placeful_workflow import IPlacefulMarker


def get_workflow_policy(context):
    wtool = getToolByName(context, 'portal_workflow')
    if IPlacefulMarker.providedBy(wtool):
        chain = None
        current_ob = aq_inner(context)
        while current_ob is not None and not IPloneSiteRoot.providedBy(current_ob):
            if base_hasattr(current_ob, WorkflowPolicyConfig_id):
                return getattr(current_ob, WorkflowPolicyConfig_id)

            current_ob = aq_inner(aq_parent(current_ob))

    return None
