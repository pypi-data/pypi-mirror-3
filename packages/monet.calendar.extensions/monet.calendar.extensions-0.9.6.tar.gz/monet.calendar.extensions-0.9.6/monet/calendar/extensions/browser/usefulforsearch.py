# -*- coding: utf-8 -*-

from monet.calendar.extensions.interfaces import IMonetCalendarSection, IMonetCalendarSearchRoot
from Acquisition import aq_chain, aq_inner
from Products.CMFCore.utils import getToolByName
from plone.app.layout.navigation.interfaces import INavigationRoot
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot

class UsefulForSearchEvents(object):
    """Utility class for grouping usefull features"""
        
    def _getSubSiteParentFolder(self):
        """Return the first parent folder found that implements the interface IMonetCalendarSearchRoot"""
        for parent in aq_chain(aq_inner(self.context)):
            if IMonetCalendarSearchRoot.providedBy(parent):
                return parent
            # If linguaplone is there we need to stop before reaching the site, but onto the en/es/it folders...
            if INavigationRoot.providedBy(parent) and not IPloneSiteRoot.providedBy(parent):
                return parent
        return None
        
    def getCalendarSection(self,subsite):
        """Return the first folder found that implements the interface IMonetCalendarSection"""
        pcatalog = getToolByName(self.context, 'portal_catalog')
        query = {}
        query['object_provides'] = IMonetCalendarSection.__identifier__
        query['path'] = '/'.join(subsite.getPhysicalPath())
        brains = pcatalog.searchResults(**query)
        if brains:
            return brains[0]
        return None
        
    def _getCalendarSectionParentNoSubSite(self):
        """
        Return the first folder found in the site root (no sub-site)
        that implements the interface IMonetCalendarSection
        """
        portal=getToolByName(self.context, 'portal_url').getPortalObject()
        pcatalog = getToolByName(self, 'portal_catalog')
        query = {}
        query['object_provides'] = IMonetCalendarSection.__identifier__
        query['path'] = {'query':'/'.join(portal.getPhysicalPath()),'depth':1}
        brains = pcatalog.searchResults(**query)
        if brains:
            return brains[0]
        return None
    
    def getCalendarSectionPath(self):
        subsite = self._getSubSiteParentFolder()
        if subsite:
            calendarsection = self.getCalendarSection(subsite)
        else:
            calendarsection = self._getCalendarSectionParentNoSubSite()
        if calendarsection:
            return calendarsection.getURL()
        else:
            portal=getToolByName(self.context, 'portal_url').getPortalObject()
            return portal.absolute_url()
        
    def getSubSitePath(self):
        subsite = self._getSubSiteParentFolder()
        if subsite:
            return '/'.join(subsite.getPhysicalPath())
        return ''

    def formatDateString(self,day):
        """Return a date in YYYY-MM-DD format"""
        return '%s-%s-%s' % (day.year, day.month, day.day)

