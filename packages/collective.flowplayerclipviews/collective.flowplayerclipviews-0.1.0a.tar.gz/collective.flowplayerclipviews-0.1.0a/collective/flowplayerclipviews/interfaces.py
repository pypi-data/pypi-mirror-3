# -*- coding: utf-8 -*-

from zope.interface import Interface
from zope.interface import Attribute

class IViewsStats(Interface):
    """Collect statistics about the a video view"""
    
    views = Attribute("Total current views count of the clip")

class IMediaWithViewsStats(Interface):
    """Marker interface for all media that behave view stats information"""

