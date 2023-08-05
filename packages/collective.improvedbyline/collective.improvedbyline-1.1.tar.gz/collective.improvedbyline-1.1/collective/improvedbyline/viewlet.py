from Acquisition import aq_inner
from DateTime import DateTime

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.Archetypes.utils import shasattr

from plone.app.layout.viewlets.content import DocumentBylineViewlet as base
from plone.memoize.instance import memoize


class DocumentBylineViewlet(base):

    index = ViewPageTemplateFile("document_byline.pt")

    @memoize
    def pub_date(self):
        """Return object published date if it's currently in published
        workflow state.
        """
        review_history = self._review_history()
        if review_history:
           info = review_history[-1]
           if info['review_state'] == 'published':
               return info['time']

        return None
    
    def mod_date(self):
        """Return modification date if object was modified after it was
        published, or if object is not published yet.
        """
        modified = DateTime(self.context.ModificationDate())
        published = self.pub_date()
        if modified is not None and published is not None and \
           modified <= published:
            return None
        
        return modified

    def _review_history(self):
        """Get review history using low level API to skip security check
        agains Review Portal Content permission.
        
        Otherwise published date won't be available for anonymous and plain
        member users.
        """
        wtool = getToolByName(self.context, 'portal_workflow')
        found = None
        for wf in wtool.getWorkflowsFor(self.context):
            if wf.isInfoSupported(self.context, 'review_history'):
                found = wf
        
        if found:
            if shasattr(self.context, 'workflow_history'):
                history = self.context.workflow_history
                if found.id in history:
                    return history[found.id]
        
        return None
