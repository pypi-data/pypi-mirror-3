import unittest
from DateTime import DateTime

from Products.CMFCore.utils import getToolByName

from plone.app.layout.viewlets.tests.test_content import \
    TestDocumentBylineViewletView

from collective.improvedbyline.viewlet import DocumentBylineViewlet


class TestDocumentBylineViewlet(TestDocumentBylineViewletView):
   
    def test_document_not_published(self):
        # prepare content
        self.folder.invokeFactory('Document', 'page1')
        page = getattr(self.folder, 'page1')
        
        # render viewlet
        viewlet = DocumentBylineViewlet(page, self.app.REQUEST, None, None)
        viewlet = viewlet.__of__(viewlet.context)
        viewlet.update()
        content = viewlet.render()
        
        self.failIf('published' in content)
        self.failUnless('modified' in content)
        self.failUnless(viewlet.pub_date() is None)
        self.failIf(viewlet.mod_date() is None)

    def test_document_published(self):
        # login to create and publish content
        self.loginAsPortalOwner()
        
        # prepare content
        self.folder.invokeFactory('Document', 'page1')
        page = getattr(self.folder, 'page1')
        wf_tool = getToolByName(self.portal, 'portal_workflow')
        wf_tool.doActionFor(page, 'publish')
        
        # render viewlet
        viewlet = DocumentBylineViewlet(page, self.app.REQUEST, None, None)
        viewlet = viewlet.__of__(viewlet.context)
        viewlet.update()
        content = viewlet.render()
        
        self.failUnless('published' in content)
        self.failIf('modified' in content)
        self.failIf(viewlet.pub_date() is None)
        self.failUnless(viewlet.mod_date() is None)

    def test_document_published_and_modified(self):
        # login to create and publish content
        self.loginAsPortalOwner()
        
        # prepare content
        self.folder.invokeFactory('Document', 'page1')
        wf_tool = getToolByName(self.portal, 'portal_workflow')
        page = getattr(self.folder, 'page1')
        wf_tool.doActionFor(page, 'publish')
        
        # set document modification date 1 second after publication date
        mDate = DateTime(int(DateTime()) + 1)
        page.setModificationDate(mDate)
        
        # render viewlet
        viewlet = DocumentBylineViewlet(page, self.app.REQUEST, None, None)
        viewlet = viewlet.__of__(viewlet.context)
        viewlet.update()
        content = viewlet.render()
        
        self.failUnless('published' in content)
        self.failUnless('modified' in content)
        self.failIf(viewlet.pub_date() is None)
        self.failIf(viewlet.mod_date() is None)
    
    def test_anonymous(self):
        # login to create and publish content
        self.loginAsPortalOwner()
        
        # prepare content
        self.folder.invokeFactory('Document', 'page1')
        wf_tool = getToolByName(self.portal, 'portal_workflow')
        page = getattr(self.folder, 'page1')
        wf_tool.doActionFor(page, 'publish')
        
        # set document modification date 1 second after publication date
        mDate = DateTime(int(DateTime()) + 1)
        page.setModificationDate(mDate)
        self.logout()
        
        # switch anonymous bylines on
        ptool = getToolByName(self.portal, 'portal_properties')
        ptool.site_properties.allowAnonymousViewAbout = True
        
        # render viewlet
        viewlet = DocumentBylineViewlet(page, self.app.REQUEST, None, None)
        viewlet = viewlet.__of__(viewlet.context)
        viewlet.update()
        content = viewlet.render()
        
        self.failUnless('published' in content)
        self.failUnless('modified' in content)
        self.failIf(viewlet.pub_date() is None)
        self.failIf(viewlet.mod_date() is None)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestDocumentBylineViewlet))
    return suite
