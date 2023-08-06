# -*- coding: utf-8 -*-
from zope.interface import implements, Interface
from zope.component import getUtility

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName

from plone.registry.interfaces import IRegistry

from collective.lcstartp import lcStartPageMessageFactory as _
from collective.lcstartp.interfaces import ILcStartPageSettingsSchema


class IStartPageView(Interface):
    """
    Public view interface
    """



class StartPageView(BrowserView):
    """
    Public browser view
    """
    implements(IStartPageView)
    template = ViewPageTemplateFile('startp.pt')
    content_types=['Document']

    def __init__(self, context, request):
        self.context = context
        self.request = request
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ILcStartPageSettingsSchema)
        self.content_types = settings.content_types

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

    def get_links(self):
        brains = self.portal_catalog(portal_type=self.content_types)
        return brains

    def __call__(self):
        self.request.response.setHeader('X-Theme-Disabled', 'True')
        return self.template()
