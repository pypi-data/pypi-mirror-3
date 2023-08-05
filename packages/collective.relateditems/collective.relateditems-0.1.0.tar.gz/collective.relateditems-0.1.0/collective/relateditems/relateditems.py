# -*- coding: utf-8 -*-

from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone.utils import base_hasattr
from Products.CMFCore.utils import getToolByName
from plone.app.layout.viewlets import ViewletBase

class ContentRelatedItems(ViewletBase):

    index = ViewPageTemplateFile("document_relateditems.pt")

    def related_items(self):
        context = aq_inner(self.context)
        res = ()
        if base_hasattr(context, 'getRawRelatedItems'):
            catalog = getToolByName(context, 'portal_catalog')
            related = context.getRawRelatedItems()
            if not related:
                return ()
            brains = catalog(UID=related)
            if brains:
                # build a position dict by iterating over the items once
                positions = dict([(v, i) for (i, v) in enumerate(related)])
                # We need to keep the ordering intact
                res = list(brains)
                def _key(brain):
                    return positions.get(brain.UID, -1)
                res.sort(key=_key)
        return res
