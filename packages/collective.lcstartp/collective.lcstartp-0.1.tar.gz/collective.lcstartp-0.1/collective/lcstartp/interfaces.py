# -*- coding: utf-8 -*-
from zope import interface, schema
from plone.theme.interfaces import IDefaultPloneLayer
from collective.lcstartp import lcStartPageMessageFactory as _

class ILinkCheckerStartPageLayer(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer.
    """

class ILcStartPageSettingsSchema(interface.Interface):

        content_types = schema.List(
        title = _(u'Content types'),
        required = False,
        default = [u'Link', u'Event', u'Document', u'News Item'],
        description = _(u"A list of types to be checked",),
        value_type = schema.Choice(title=_(u"Content types"),
            source="plone.app.vocabularies.ReallyUserFriendlyTypes")
        )
