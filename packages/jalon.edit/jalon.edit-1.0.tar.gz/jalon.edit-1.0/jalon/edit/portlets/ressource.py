# -*- coding: utf-8 -*-

from Acquisition import aq_inner

from zope import schema
from zope.formlib import form
from zope.interface import implements
from zope.component import getMultiAdapter

from plone.memoize.instance import memoize
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider

from jalon.edit import contentMessageFactory as _

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class IRessourcePortlet(IPortletDataProvider):
    ''' Ressource portlet
    '''
    glossaire = schema.Bool( title = _(u"Glossaire"),
                             required=True, 
                             default=True)
    webographie = schema.Bool( title = _(u"Webographie"),
                               required=True, 
                               default=True)
    bibliographie = schema.Bool( title = _(u"Bibliographie"),
                                 required=True, 
                                 default=True)

class Assignment(base.Assignment):
    implements(IRessourcePortlet)

    def __init__(self, glossaire=True, webographie=True, bibliographie=True):
        self.glossaire = glossaire
        self.webographie = webographie
        self.bibliographie = bibliographie

    @property
    def title(self):
        return _(u"Ressources".encode("utf-8"))

class AddForm(base.AddForm):
    form_fields = form.Fields(IRessourcePortlet)
    label = _(u"Add Ressource Portlet")
    description = _(u"Ce portlet affiche le menu ressource")

    def create(self, data):
        return Assignment(glossaire=data.get('glossaire', True), webographie=data.get('webographie', True), bibliographie=data.get('bibliographie', True))

class EditForm(base.EditForm):
    form_fields = form.Fields(IRessourcePortlet)
    label = _(u"Edit Ressource Portlet")
    description = _(u"Ce portlet affiche le menu ressource.")

class Renderer(base.Renderer):
    _template = ViewPageTemplateFile('templates/ressource.pt')

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)
        context = aq_inner(self.context)
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        self.portal_url = portal_state.portal_url()  # the URL of the portal object

    def render(self):
        return self._template()

    @property
    def available(self):
        """Show the portlet only if there are one or more elements."""
        return len(self._data()) > 0

    def ressource_items(self):
        if not hasattr(self.data, "webographie"): self.data.__init__()
        return self._data()

    def getClass(self, oddrow):
        if str(oddrow) == "False": return "portletItem odd"
        else: return "portletItem even"

    def getTitle(self):
        return self.data.title

    def isAnonymous(self):
        context = aq_inner(self.context)
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        return portal_state.anonymous()

    @memoize
    def _data(self):
        liste = []
        if self.data.glossaire:
           #"ajout" : "%s/glossaire/createObject?type_name=Glossaire" % self.portal_url
           liste.append({"titre" : _(u"Glossaire")
                        ,"url"   : "%s/cours/glossaire" % self.portal_url
                        ,"id"    : "glossaire"
                        ,"ajout" : None})
        if self.data.webographie: 
           liste.append({"titre" : _(u"Webographie")
                        ,"url"   : "%s/cours/webographie" % self.portal_url
                        ,"id"    : "webographie"
                        ,"ajout" : None})
        if self.data.bibliographie: 
           liste.append({"titre" : _(u"Bibliographie")
                        ,"url"   : "%s/cours/bibliographie" % self.portal_url
                        ,"id"    : "bibliographie"
                        ,"ajout" : None})
        return liste
