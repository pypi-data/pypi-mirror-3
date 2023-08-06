import logging

from zope import schema
from zope import component
from zope.interface import implements
from zope.component import getUtility, getMultiAdapter
from zope.formlib import form
from AccessControl import getSecurityManager
from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.form.widgets.wysiwygwidget import WYSIWYGWidget
from plone.app.portlets.portlets import base
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.portlets.interfaces import IPortletDataProvider
from plone.memoize.instance import memoize
from plone.portlet.static import PloneMessageFactory as _

from Products.CMFCore.utils import getToolByName

logger = logging.getLogger('nge.spa.portlet.slider')


class ISliderPortlet(IPortletDataProvider):
    """A portlet which renders predefined static HTML.

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    target_folder = schema.Choice(
        title=_(u"Target folder"),
        description=_(u"Find the folder which provides the photos"),
        required=True,
        source=SearchableTextSourceBinder(
            {"portal_type": "Folder"},
            default_query='path:'))


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(ISliderPortlet)
    title = _(u"NivoSlider portlet")
    target_folder = None

    def __init__(self, target_folder=None):
        self.target_folder = target_folder


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('portlet.pt')

    @memoize
    def folder(self):
        folder_path = self.data.target_folder
        if not folder_path:
            return None

        if folder_path.startswith('/'):
            folder_path = folder_path[1:]

        if not folder_path:
            return None

        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        portal = portal_state.portal()
        if isinstance(folder_path, unicode):
            # restrictedTraverse accepts only strings
            folder_path = str(folder_path)

        result = portal.unrestrictedTraverse(folder_path, default=None)
        if result is not None:
            sm = getSecurityManager()
            if not sm.checkPermission('View', result):
                result = None
        return result

    def images(self):
        folder = self.folder()
        query = {"portal_types": "Image",
                 "sort_on": "getPositionInParent"}
        images = folder.listFolderContents(contentFilter=query)
        return images

    def site_url(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        return portal_state.portal_url()


class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(ISliderPortlet)
    form_fields['target_folder'].custom_widget = UberSelectionWidget
    label = _(u"title_add_slider_portlet",
              default=u"Add NivoSlider portlet")
    description = _(u"description_slider_portlet",
                    default=u"A portlet which display a slider")

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(ISliderPortlet)
    form_fields['target_folder'].custom_widget = UberSelectionWidget
    label = _(u"title_edit_slider_portlet",
              default=u"Edit NivoSlider portlet")
    description = _(u"description_slider_portlet",
                    default=u"A portlet which display a slider")
