# -*- coding: utf-8 -*-

import json
from datetime import datetime, timedelta
from uuid import uuid4
from zope.interface import alsoProvides
from Products.Five.browser import BrowserView

from collective.flowplayer.interfaces import IMediaInfo
from collective.flowplayerclipviews.interfaces import IViewsStats, IMediaWithViewsStats
from collective.flowplayerclipviews import logger

class ViewStartedView(BrowserView):
    """View to be called when the video show starts"""
    
    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)

    def __call__(self):
        context = self.context
        request = self.request
        token = str(uuid4())
        if not request.SESSION.get('collective.flowplayerclipviews'):
            request.SESSION['collective.flowplayerclipviews'] = {}
        if not request.SESSION['collective.flowplayerclipviews'].get('/'.join(context.getPhysicalPath())):
            request.SESSION['collective.flowplayerclipviews']['/'.join(context.getPhysicalPath())] = {'token': token,
                                                                                                      'time': datetime.now()}
        return json.dumps({'token': str(token)})

class ViewCompletedView(BrowserView):
    """View for mark the Video as view by the user"""
    
    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)

    def _getClipDuration(self):
        """Return the video duration, or None if not able to extract it"""
        # info = IMediaInfo(self.context)
        # ...
        # XXX not until flowplayer will support video "duration" extraction
        return None

    def __call__(self):
        context = self.context
        request = self.request
        token = request.form.get('token')
        session_data = request.SESSION.get('collective.flowplayerclipviews', {}).get('/'.join(context.getPhysicalPath()))
        if token and token == session_data['token']:
            logger.debug("token %s: test ok" % token)
            clipDuration = self._getClipDuration()
            if clipDuration is not None:
                now = datetime.now()
                if clipDuration > (now-session_data['time']):
                    return
                logger.debug("client response time: ok")
            stats = IViewsStats(context)
            if not IMediaWithViewsStats.providedBy(context):
                alsoProvides(context, IMediaWithViewsStats)
                stats.views = 1
                logger.debug("views count inited")
            else:
                stats.views += 1
                logger.debug("views count: %s" % stats.views)
            return json.dumps({'views': stats.views})
        return json.dumps({})
