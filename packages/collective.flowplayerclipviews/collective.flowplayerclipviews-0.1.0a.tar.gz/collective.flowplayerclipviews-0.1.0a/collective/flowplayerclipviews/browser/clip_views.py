# -*- coding: utf-8 -*-

from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from collective.flowplayerclipviews.interfaces import IViewsStats

class ClipViewsViewlet(ViewletBase):
    index = ViewPageTemplateFile('clip_views.pt')

    def update(self):
        context = aq_inner(self.context)
        self.views = IViewsStats(context).views
