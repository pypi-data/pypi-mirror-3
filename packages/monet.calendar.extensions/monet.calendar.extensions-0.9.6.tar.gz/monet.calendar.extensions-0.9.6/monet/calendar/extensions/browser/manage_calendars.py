# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from zope.interface import alsoProvides, noLongerProvides
from monet.calendar.extensions.interfaces import IMonetCalendarSearchRoot, IMonetCalendarSection

from monet.calendar.extensions import eventMessageFactory as _ 

class ManageCalendarsView(BrowserView):
    """Method for managing the calendar status of folders"""
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.putils = getToolByName(context, 'plone_utils')
    
    def make_search_root(self):
        context = self.context
        alsoProvides(context, IMonetCalendarSearchRoot)
        context.reindexObject(idxs=['object_provides'])
        self.putils.addPortalMessage(_(u'Status changed'))
        self.request.response.redirect(context.absolute_url())        
    
    def remove_search_root(self):
        context = self.context
        noLongerProvides(context, IMonetCalendarSearchRoot)
        context.reindexObject(idxs=['object_provides'])
        self.putils.addPortalMessage(_(u'Status changed'))
        self.request.response.redirect(context.absolute_url())

    def make_calendarsection(self):
        context = self.context
        alsoProvides(context, IMonetCalendarSection)
        context.reindexObject(idxs=['object_provides'])
        self.putils.addPortalMessage(_(u'Status changed'))
        self.putils.addPortalMessage(_(u'warn_layout_change',
                                       default=u'You may want to change the current layout to "Calendar view"'))
        self.request.response.redirect(context.absolute_url())
    
    def remove_calendarsection(self):
        context = self.context
        noLongerProvides(context, IMonetCalendarSection)
        context.reindexObject(idxs=['object_provides'])
        self.putils.addPortalMessage(_(u'Status changed'))
        if context.getProperty('layout')=='monetsearchevents':
            self.putils.addPortalMessage(_(u'The view of the folder has been changed'))
            context.manage_changeProperties({'layout': 'folder_listing'})
        self.request.response.redirect(context.absolute_url())
