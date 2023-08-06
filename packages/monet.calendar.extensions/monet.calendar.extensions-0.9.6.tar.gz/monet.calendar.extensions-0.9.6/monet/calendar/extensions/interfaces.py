# -*- coding: utf-8 -*-

from zope.interface import Interface
from monet.calendar.event.interfaces import IMonetCalendar

from zope.app.publisher.interfaces.browser import IBrowserMenu
from zope.app.publisher.interfaces.browser import IBrowserSubMenuItem

class IMonetCalendarSection(IMonetCalendar):
    """Identifies folders on which you can use the view search events"""
    
class IMonetCalendarSearchRoot(Interface):
    """Identifies sub-folders, called sub-sites"""

class ICalendarMenu(IBrowserMenu):
    """The calendar menu.
    """

class ICalendarSubMenuItem(IBrowserSubMenuItem):
    """The menu item linking to the calendar menu.
    """

class IMonetCalendarExtensionsLayer(Interface):
    """Marker interface for the monet.calendar.extensions layer"""