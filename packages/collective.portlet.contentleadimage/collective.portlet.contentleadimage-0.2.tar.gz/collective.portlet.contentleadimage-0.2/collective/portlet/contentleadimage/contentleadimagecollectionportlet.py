from zope.interface import implements
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Acquisition import aq_inner

from collective.portlet.contentleadimage import ContentLeadImageCollectionPortletMessageFactory as _

from plone.portlet.collection import collection
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget

from collective.contentleadimage.config import IMAGE_FIELD_NAME
from collective.contentleadimage.config import IMAGE_CAPTION_FIELD_NAME
from collective.contentleadimage.leadimageprefs import ILeadImagePrefsForm


class IContentLeadImageCollectionPortlet(collection.ICollectionPortlet):
    """A portlet which renders the results of a collection object, but
    displaying the contentleadimages.
    """

class Assignment(collection.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IContentLeadImageCollectionPortlet)


class Renderer(collection.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    #_template = ViewPageTemplateFile('contentleadimagecollectionportlet.pt')
    render = ViewPageTemplateFile('contentleadimagecollectionportlet.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

    def tag(self, obj, css_class='tileImage'):
        context = aq_inner(obj)
        field = context.getField(IMAGE_FIELD_NAME)
        titlef = context.getField(IMAGE_CAPTION_FIELD_NAME)
        if titlef is not None:
            title = titlef.get(context)
        else:
            title = ''
        if field is not None:
            if field.get_size(context) != 0:
                portal = getUtility(IPloneSiteRoot)
                prefs =  ILeadImagePrefsForm(portal)
                scale = prefs.desc_scale_name
                return field.tag(context, scale=scale, css_class=css_class, title=title)
        return ''


class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IContentLeadImageCollectionPortlet)
    form_fields['target_collection'].custom_widget = UberSelectionWidget

    label = _(u"Add ContentLeadImage Collection Portlet")
    description = _(u"This portlet display a listing of items's contentleadimages from a Collection.")

    def create(self, data):
        return Assignment(**data)

class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IContentLeadImageCollectionPortlet)
    form_fields['target_collection'].custom_widget = UberSelectionWidget

    label = _(u"Edit ContentLeadImage Collection Portlet")
    description = _(u"This portlet display a listing of items's contentleadimages from a Collection.")
