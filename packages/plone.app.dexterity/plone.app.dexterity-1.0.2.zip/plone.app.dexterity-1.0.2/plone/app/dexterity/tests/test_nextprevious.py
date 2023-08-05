from plone.app.layout.nextprevious.interfaces import INextPreviousProvider
from plone.app.dexterity.tests.base import DexterityTestCase
from plone.dexterity.fti import DexterityFTI

from Products.CMFCore.utils import getToolByName

class NextPreviousBase:
    # subclass here
    _behaviors = None
    _portal_type = None

    def _setupFTI(self):
        fti = DexterityFTI(self._portal_type)
        self.portal.portal_types._setObject(self._portal_type, fti)
        fti.klass = 'plone.dexterity.content.Container'
        fti.filter_content_types = False
        fti.behaviors = self._behaviors


class NextPreviousEnabledTests(NextPreviousBase, DexterityTestCase):
    """ basic use cases and tests for next/previous navigation, essentially
        borrowed from `plone.app.folder.tests.test_nextprevious.py` """

    _behaviors = ('plone.app.dexterity.behaviors.nextprevious.INextPreviousEnabled',)
    _portal_type = 'FolderEnabled'

    def afterSetUp(self):
        self.wf = getToolByName(self.portal, "portal_workflow")
        self.portal.acl_users._doAddUser('user_std', 'secret', ['Member'], [])
        self.setRoles(['Manager'])
        self._setupFTI()
        self.portal.invokeFactory('Document', 'doc1')
        self.portal.invokeFactory('Document', 'doc2')
        self.portal.invokeFactory('Document', 'doc3')
        self.portal.invokeFactory(self._portal_type, 'folder1')
        self.portal.invokeFactory('Link', 'link1')
        self.portal.link1.setRemoteUrl('http://plone.org')
        self.portal.link1.reindexObject()
        folder1 = getattr(self.portal, 'folder1')
        folder1.invokeFactory('Document', 'doc11')
        folder1.invokeFactory('Document', 'doc12')
        folder1.invokeFactory('Document', 'doc13')
        self.portal.invokeFactory(self._portal_type, 'folder2')
        folder2 = getattr(self.portal, 'folder2')
        folder2.invokeFactory('Document', 'doc21')
        folder2.invokeFactory('Document', 'doc22')
        folder2.invokeFactory('Document', 'doc23')
        folder2.invokeFactory('File', 'file21')
        self.setRoles(['Member'])

    def testIfFolderImplementsPreviousNext(self):
        self.failUnless(INextPreviousProvider(self.portal.folder1, None))

    def testNextPreviousEnablingOnCreation(self):
        self.failUnless(INextPreviousProvider(self.portal.folder1).enabled)

    def testNextPreviousViewEnabled(self):
        doc = self.portal.folder1.doc11
        view = doc.restrictedTraverse('@@plone_nextprevious_view')
        self.failIf(view is None)
        self.failUnless(view.enabled())

    def testNextPreviousItems(self):
        container = self.folder[self.folder.invokeFactory(self._portal_type, 'case3')]
        for id in range(1, 4):
            container.invokeFactory('Document', 'subDoc%d' % id)

        from OFS.Folder import manage_addFolder
        manage_addFolder(container, 'notacontentishtype')

        for id in range(5, 6):
            container.invokeFactory('Document', 'subDoc%d' % id)

        adapter = INextPreviousProvider(container)
        # text data for next/previous items
        next = adapter.getNextItem(container.subDoc2)
        self.assertEqual(next['id'], 'subDoc3')
        self.assertEqual(next['portal_type'], 'Document')
        self.assertEqual(next['url'], container.subDoc3.absolute_url())
        previous = adapter.getPreviousItem(container.subDoc2)
        self.assertEqual(previous['id'], 'subDoc1')
        self.assertEqual(previous['portal_type'], 'Document')
        self.assertEqual(previous['url'], container.subDoc1.absolute_url())

        # #11234 not contentish contents shouldn't be returned
        # as next or previous content
        next = adapter.getNextItem(container.subDoc3)
        self.assertEqual(next['id'], 'subDoc5')
        previous = adapter.getPreviousItem(container.subDoc5)
        self.assertEqual(previous['id'], 'subDoc3')

        # first item should not have a previous item
        previous = adapter.getPreviousItem(container.subDoc1)
        self.assertEqual(previous, None)
        # last item should not have a next item
        next = adapter.getNextItem(container.subDoc5)
        self.assertEqual(next, None)

    def testNextItemOnlyShowViewable(self):
        container = self.folder[self.folder.invokeFactory(self._portal_type, 'case3')]
        # create objects [subDoc1,subDoc2,subDoc3,subDoc4,subDoc5,subDoc6]
        # published objects [subDoc2, subDoc4, subDoc5]
        self.setRoles(("Manager",))
        for id in range(1, 7):
            doc = container[container.invokeFactory('Document', 'subDoc%d' % id)]
            if id in [2,4,5]:
                self.wf.doActionFor(doc, "publish")

        # Member should only see the published items
        self.logout()
        self.login('user_std')
        adapter = INextPreviousProvider(container)
        # text data for next/tems
        next = adapter.getNextItem(container.subDoc2)
        self.assertEqual(next['id'], 'subDoc4')
        next = adapter.getNextItem(container.subDoc4)
        self.assertEqual(next['id'], 'subDoc5')
        next = adapter.getNextItem(container.subDoc5)
        self.assertEqual(next, None)

    def testPreviousItemOnlyShowViewable(self):
        container = self.folder[self.folder.invokeFactory(self._portal_type, 'case3')]
        # create objects [subDoc1,subDoc2,subDoc3,subDoc4,subDoc5,subDoc6]
        # published objects [subDoc2, subDoc4, subDoc5]
        self.setRoles(("Manager",))
        for id in range(1, 7):
            doc = container[container.invokeFactory('Document', 'subDoc%d' % id)]
            if id in [2,4,5]:
                self.wf.doActionFor(doc, "publish")

        # Member should only see the published items
        self.logout()
        self.login('user_std')
        adapter = INextPreviousProvider(container)
        # text data for next/tems
        previous = adapter.getPreviousItem(container.subDoc5)
        self.assertEqual(previous['id'], 'subDoc4')
        previous = adapter.getPreviousItem(container.subDoc4)
        self.assertEqual(previous['id'], 'subDoc2')
        previous = adapter.getPreviousItem(container.subDoc2)
        self.assertEqual(previous, None)


class NextPreviousToggleTests(NextPreviousBase, DexterityTestCase):
    """ basic use cases and tests for next/previous navigation, essentially
        borrowed from `plone.app.folder.tests.test_nextprevious.py` """

    _behaviors = ('plone.app.dexterity.behaviors.nextprevious.INextPreviousToggle',)
    _portal_type = 'FolderWithToggle'

    def afterSetUp(self):
        self.wf = getToolByName(self.portal, "portal_workflow")
        self.portal.acl_users._doAddUser('user_std', 'secret', ['Member'], [])
        self.setRoles(['Manager'])
        self._setupFTI()
        self.portal.invokeFactory(self._portal_type, 'folder1')
        self.portal.folder1.invokeFactory('Document', 'doc11')
        self.setRoles(['Member'])

    def testIfFolderImplementsPreviousNext(self):
        self.failUnless(INextPreviousProvider(self.portal.folder1, None))

    def testNextPreviousEnablingOnCreation(self):
        # This is tested properly in the doctest, the default z3c.form
        # value is not set here.
        self.failIf(INextPreviousProvider(self.portal.folder1).enabled)

    def testNextPreviousViewDisabled(self):
        doc = self.portal.folder1.doc11
        view = doc.restrictedTraverse('@@plone_nextprevious_view')
        self.failIf(view is None)
        self.failIf(view.enabled())

    def testNextPreviousViewEnabled(self):
        self.portal.folder1.nextPreviousEnabled = True
        doc = self.portal.folder1.doc11
        view = doc.restrictedTraverse('@@plone_nextprevious_view')
        self.failIf(view is None)
        self.failUnless(view.enabled())


def test_suite():
    from unittest import defaultTestLoader
    return defaultTestLoader.loadTestsFromName(__name__)
