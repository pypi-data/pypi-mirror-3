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

class IPresentationPortlet(IPortletDataProvider):
    ''' Presentation portlet
    '''
    caracteristiques = schema.Bool( title = _(u"Description"),
                                    required=True, 
                                    default=True)
    finalites = schema.Bool( title = _(u"Pré-requis"),
                             required=True, 
                             default=True)
    contenu = schema.Bool( title = _(u"Objectifs"),
                           required=True, 
                           default=True)

class Assignment(base.Assignment):
    implements(IPresentationPortlet)

    def __init__(self, caracteristiques=True, finalites=True, contenu=True):
        self.caracteristiques = caracteristiques
        self.finalites = finalites
        self.contenu = contenu

    @property
    def title(self):
        return _(u"Présentation")

class AddForm(base.AddForm):
    form_fields = form.Fields(IPresentationPortlet)
    label = _(u"Add Presentation Portlet")
    description = _(u"Ce portlet affiche le menu Presentation")

    def create(self, data):
        return Assignment(caracteristiques=data.get('caracteristiques', True), finalites=data.get('finalites', True), contenu=data.get('contenu', True))

class EditForm(base.EditForm):
    form_fields = form.Fields(IPresentationPortlet)
    label = _(u"Edit Presentation Portlet")
    description = _(u"Ce portlet affiche le menu Presentation.")

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
        if not hasattr(self.data, "finalites"): self.data.__init__()
        return self._data()

    def getClass(self, oddrow):
        if str(oddrow) == "False": return "portletItem odd"
        else: return "portletItem even"

    def getTitle(self):
        return self.data.title

    def isAnonymous(self):
        return True

    @memoize
    def _data(self):
        liste = []
        if self.data.caracteristiques: 
           liste.append({"titre" : _(u"Description")
                        ,"url"   : "%s/cours/presentation#a" % self.portal_url
                        ,"id"    : "caracteristiques"
                        ,"ajout" : None})
        if self.data.finalites: 
           liste.append({"titre" : _(u"Pré-requis")
                        ,"url"   : "%s/cours/presentation#b" % self.portal_url
                        ,"id"    : "finalites"
                        ,"ajout" : None})
        if self.data.contenu: 
           liste.append({"titre" : _(u"Objectifs")
                        ,"url"   : "%s/cours/presentation#c" % self.portal_url
                        ,"id"    : "contenu"
                        ,"ajout" : None})
        return liste
