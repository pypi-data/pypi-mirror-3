from Products.ATContentTypes.interface import IATTopic
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget
from plone.app.portlets.portlets import base
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.portlets.interfaces import IPortletDataProvider
from zope import schema
from zope.component import getMultiAdapter
from zope.formlib import form
from zope.interface import implements


class IContentSearchPortlet(IPortletDataProvider):
    """ A portlet for content search."""

    target_collection = schema.Choice(
        title=_(u"Target collection"),
        description=_(u"Add collection with which the search result will be filtered."),
        required=True,
        source=SearchableTextSourceBinder(
            {'object_provides': IATTopic.__identifier__},
            default_query='path:'))


class Assignment(base.Assignment):
    implements(IContentSearchPortlet)

    target_collection = None

    def __init__(self, target_collection=None):
        self.target_collection = target_collection

    @property
    def title(self):
        return _(u"Search")


class Renderer(base.Renderer):

    render = ViewPageTemplateFile('contentsearchportlet.pt')

    def update(self):
        self.results = []
        if self.request.form.get('form.contentsearch') is not None:
            words = self.request.get('SearchableContentText')
            if words:
                self.results = self._collection.queryCatalog(SearchableText=words)
        super(self.__class__, self).update()

    @property
    def _collection(self):
        """ get the collection the portlet is pointing to"""
        path = self.data.target_collection
        if path:
            portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
            portal = portal_state.portal()
            path = '{}{}'.format('/'.join(portal.getPhysicalPath()), path)
            query = {'path': {
                'query': path,
                'depth': 0,
            }}
            catalog = getToolByName(self.context, 'portal_catalog')
            return catalog(query)[0].getObject()

    @property
    def available(self):
        return self._collection


class AddForm(base.AddForm):
    form_fields = form.Fields(IContentSearchPortlet)
    form_fields['target_collection'].custom_widget = UberSelectionWidget
    label = _(u"Add Content Search Portlet")
    description = _(u"This portlet shows a content search form.")

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    form_fields = form.Fields(IContentSearchPortlet)
    form_fields['target_collection'].custom_widget = UberSelectionWidget
    label = _(u"Edit Content Search Portlet")
    description = _(u"This portlet shows a content search form.")
