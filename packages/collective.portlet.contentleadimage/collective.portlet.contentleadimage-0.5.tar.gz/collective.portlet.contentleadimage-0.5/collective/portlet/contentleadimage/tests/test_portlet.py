import os
from zope.component import getUtility, getMultiAdapter
from DateTime import DateTime

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer

from plone.app.portlets.storage import PortletAssignmentMapping

from collective.portlet.contentleadimage import contentleadimagecollectionportlet

from collective.portlet.contentleadimage.tests.base import TestCase

from collective.contentleadimage.leadimageprefs import ILeadImagePrefsForm
from collective.contentleadimage.config import IMAGE_FIELD_NAME
from Products.CMFCore.utils import getToolByName


class TestPortlet(TestCase):

    def afterSetUp(self):
        self.setRoles(('Manager', ))

    def test_portlet_type_registered(self):
        portlet = getUtility(
            IPortletType,
            name='collective.portlet.contentleadimage.ContentLeadImageCollectionPortlet')
        self.assertEquals(portlet.addview,
                          'collective.portlet.contentleadimage.ContentLeadImageCollectionPortlet')

    def test_interfaces(self):
        portlet = contentleadimagecollectionportlet.Assignment(header=u"title")
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

    def test_invoke_add_view(self):
        portlet = getUtility(
            IPortletType,
            name='collective.portlet.contentleadimage.ContentLeadImageCollectionPortlet')
        mapping = self.portal.restrictedTraverse(
            '++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        addview.createAndAdd(data={'header' : u"test title"})

        self.assertEquals(len(mapping), 1)
        self.failUnless(isinstance(mapping.values()[0],
                                   contentleadimagecollectionportlet.Assignment))

    def test_invoke_edit_view(self):
        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST

        mapping['foo'] = contentleadimagecollectionportlet.Assignment(header=u"title")
        editview = getMultiAdapter((mapping['foo'], request), name='edit')
        self.failUnless(isinstance(editview, contentleadimagecollectionportlet.EditForm))

    def test_obtain_renderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.rightcolumn',
                             context=self.portal)
        assignment = contentleadimagecollectionportlet.Assignment(header=u"title")

        renderer = getMultiAdapter(
            (context, request, view, manager, assignment), IPortletRenderer)
        self.failUnless(isinstance(renderer, contentleadimagecollectionportlet.Renderer))


class TestRenderer(TestCase):

    def afterSetUp(self):
        self.setRoles(('Manager', ))
        #make a collection
        self.collection = self._createType(self.folder, 'Topic', 'collection')
        crit = self.collection.addCriterion('portal_type', 'ATSimpleStringCriterion')
        crit.setValue('Folder')

        #Ensure folders can have contentleadimages
        self.loginAsPortalOwner()
        prefs = ILeadImagePrefsForm(self.portal)
        types = list(prefs.allowed_types)
        if not 'Folder' in types:
            types.append('Folder')
            prefs.allowed_types = types
        self.logout()
        self.login()

        # add a folder
        folder1 = self._createType(self.folder, 'Folder', 'folder_1')
        #Add contentleadimage to folder
        test_image = os.path.join(os.path.dirname(__file__), 'test_41x41.jpg')
        raw_image = open(test_image, 'rb').read()
        field = folder1.getField(IMAGE_FIELD_NAME)
        field.set(folder1, raw_image)
        folder1.reindexObject()

    def _createType(self, context, portal_type, id, **kwargs):
        """Helper method to create a new type
        """
        ttool = getToolByName(context, 'portal_types')
        cat = self.portal.portal_catalog

        fti = ttool.getTypeInfo(portal_type)
        fti.constructInstance(context, id, **kwargs)
        obj = getattr(context.aq_inner.aq_explicit, id)
        cat.indexObject(obj)
        return obj

    def renderer(self, context=None, request=None, view=None, manager=None,
                 assignment=None):
        context = context or self.folder
        request = request or self.folder.REQUEST
        view = view or self.folder.restrictedTraverse('@@plone')
        manager = manager or getUtility(
            IPortletManager, name='plone.rightcolumn', context=self.portal)

        assignment = assignment or contentleadimagecollectionportlet.Assignment(header=u"title")
        return getMultiAdapter((context, request, view, manager, assignment),
                               IPortletRenderer)

    def test_render(self):
        r = self.renderer(context=self.portal,
                          assignment=contentleadimagecollectionportlet.Assignment(header=u"title",
                                                                                  target_collection='/Members/test_user_1_/collection'))
        r = r.__of__(self.folder)
        r.update()
        output = r.render()
        self.failUnless('<img' in output)

    def test_start_dates(self):
        event1 = self._createType(self.folder, 'Event', 'event_1')
        start_date = DateTime(2400, 0)
        event1.startDate = start_date
        event1.reindexObject()

        catalog = getToolByName(self.folder, 'portal_catalog')

        event_brain = catalog(id='event_1')[0]
        folder_brain = catalog(id='folder_1')[0]

        r = self.renderer(context=self.portal,
                          assignment=contentleadimagecollectionportlet.Assignment(header=u"title",
                                                                                  start_dates=True,
                                                                                  target_collection='/Members/test_user_1_/collection'))
        r = r.__of__(self.folder)
        r.update()
        shown_date = r.object_date(event_brain)
        self.assertEqual(start_date, shown_date)
        shown_date = r.object_date(folder_brain)
        self.assertEqual(folder_brain.Date, shown_date)

        r = self.renderer(context=self.portal,
                          assignment=contentleadimagecollectionportlet.Assignment(header=u"title",
                                                                                  start_dates=False,
                                                                                  target_collection='/Members/test_user_1_/collection'))
        r = r.__of__(self.folder)
        r.update()
        shown_date = r.object_date(event_brain)
        self.assertEqual(event_brain.Date, shown_date)
        shown_date = r.object_date(folder_brain)
        self.assertEqual(folder_brain.Date, shown_date)

    def test_images_on_news(self):
        #Create a News Item with a image
        new1 = self._createType(self.folder, 'News Item', 'new_1')
        test_image = os.path.join(os.path.dirname(__file__), 'test_41x41.jpg')
        raw_image = open(test_image, 'rb').read()
        field = new1.getField('image')
        field.set(new1, raw_image)
        new1.reindexObject()

        #Change the collection to search only new items
        crit = self.collection.listCriteria()[0]
        crit.setValue('News Item')
        r = self.renderer(context=self.portal,
                          assignment=contentleadimagecollectionportlet.Assignment(header=u"title",
                                                                                  target_collection='/Members/test_user_1_/collection'))
        r = r.__of__(self.folder)
        r.update()
        output = r.render()
        self.failUnless('<img' in output)

    def test_news_without_image(self):
        #Create a News Item without a image
        new1 = self._createType(self.folder, 'News Item', 'new_1')

        #Change the collection to search only new items
        crit = self.collection.listCriteria()[0]
        crit.setValue('News Item')
        r = self.renderer(context=self.portal,
                          assignment=contentleadimagecollectionportlet.Assignment(header=u"title",
                                                                                  target_collection='/Members/test_user_1_/collection'))
        r = r.__of__(self.folder)
        r.update()
        output = r.render()
        self.failIf('<img' in output)

    def test_image_scales(self):
        #default scale size is thumb
        r = self.renderer(context=self.portal,
                          assignment=contentleadimagecollectionportlet.Assignment(header=u"title",
                                                                                  target_collection='/Members/test_user_1_/collection'))
        r = r.__of__(self.folder)
        r.update()
        output = r.render()
        self.failUnless('_thumb' in output)

        r = self.renderer(context=self.portal,
                          assignment=contentleadimagecollectionportlet.Assignment(header=u"title",
                                                                                  scale='tile',
                                                                                  target_collection='/Members/test_user_1_/collection'))
        r = r.__of__(self.folder)
        r.update()
        output = r.render()
        self.failUnless('_tile' in output)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPortlet))
    suite.addTest(makeSuite(TestRenderer))
    return suite
