# -*- coding: utf-8 -*-

from plone.app.portlets.portlets.calendar import Renderer
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from monet.calendar.extensions.browser.usefulforsearch import UsefulForSearchEvents
from plone.memoize.compress import xhtml_compress

class Renderer(Renderer, UsefulForSearchEvents):
    """A new calendar portlet, with no day highlight"""
    _template = ViewPageTemplateFile('monetcalendar.pt')
    
    def getDateString(self,daynumber):
        return '%s-%s-%s' % (self.year, self.month, daynumber)

    def render(self):
        return xhtml_compress(self._template())
