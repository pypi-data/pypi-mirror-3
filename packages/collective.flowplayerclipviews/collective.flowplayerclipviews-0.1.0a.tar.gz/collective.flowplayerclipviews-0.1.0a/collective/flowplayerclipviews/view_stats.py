# -*- coding: utf-8 -*-

from persistent import Persistent
from zope.interface import implements
from zope.component import adapts
from zope.annotation import factory

from collective.flowplayer.interfaces import IVideo
from collective.flowplayerclipviews.interfaces import IViewsStats

class ViewStats(Persistent):
    """Collect statistic about the a video view"""
    implements(IViewsStats)
    adapts(IVideo)

    def __init__(self, starting_views=0):
        self.views = starting_views

ViewStatsAdapter = factory(ViewStats)
