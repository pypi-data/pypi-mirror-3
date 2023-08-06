# -*- coding: utf-8 -*-

from zope.interface import implements
from zope.component import getMultiAdapter
from zope.app.publisher.browser.menu import BrowserMenu
from zope.app.publisher.browser.menu import BrowserSubMenuItem

from plone.browserlayer import utils as browserlayerutils
from Products.ATContentTypes.interface.folder import IATFolder

from monet.calendar.extensions.interfaces import ICalendarMenu, ICalendarSubMenuItem
from monet.calendar.extensions.interfaces import IMonetCalendarExtensionsLayer
from monet.calendar.extensions.interfaces import IMonetCalendarSearchRoot, IMonetCalendarSection
from monet.calendar.extensions import eventMessageFactory as _

class CalendarMenu(BrowserMenu):
    implements(ICalendarMenu)

    def getMenuItems(self, context, request):
        """Return menu item entries in a TAL-friendly form."""

        menu=[]
        url = context.absolute_url()

        if not IMonetCalendarSection.providedBy(context):
            menu.append({
                "title"       : _(u"label_make_caledarsection",
                                    default=u"Mark as calendar section"),
                "description" : _(u"help_make_caledarsection",
                                    default=u"Mark this section as a calendar."),
                "action"      : url+"/make_calendar_section",
                "selected"    : False,
                "icon"        : None,
                "extra"       : { "id"        : "_calendaring_calendar_section",
                                  "separator" : None,
                                  "class"     : ""
                                 },
                "submenu"     : None,
                })
        else:
            menu.append({
                "title"       : _(u"label_remove_caledarsection",
                                    default=u"Unmark as calendar section"),
                "description" : _(u"help_remove_caledarsection",
                                    default=u"Unmark this section from being a calendar section."),
                "action"      : url+"/remove_calendar_section",
                "selected"    : False,
                "icon"        : None,
                "extra"       : { "id"        : "_calendaring_remove_calendar_section",
                                  "separator" : None,
                                  "class"     : ""
                                 },
                "submenu"     : None,
                })


        if not IMonetCalendarSearchRoot.providedBy(context):
            menu.append({
                "title"       : _(u"label_make_caledarsearchroot",
                                    default=u"Mark as calendar root"),
                "description" : _(u"help_make_caledarsearchroot",
                                    default=u"Mark this section as a root for searching events. "
                                            u"Calendar inside this section will not find event defined above."),
                "action"      : url+"/make_calendar_search_root",
                "selected"    : False,
                "icon"        : None,
                "extra"       : { "id"        : "_calendaring_search_root",
                                  "separator" : None,
                                  "class"     : ""
                                 },
                "submenu"     : None,
                })
        else:
            menu.append({
                "title"       : _(u"label_remove_caledarsearchroot",
                                    default=u"Unmark as calendar root"),
                "description" : _(u"help_remove_caledarsearchroot",
                                    default=u"Remove the status of root for searching events."),
                "action"      : url+"/remove_calendar_search_root",
                "selected"    : False,
                "icon"        : None,
                "extra"       : { "id"        : "_calendaring_remove_search_root",
                                  "separator" : None,
                                  "class"     : ""
                                 },
                "submenu"     : None,
                })

        return menu


class CalendarSubMenuItem(BrowserSubMenuItem):
    implements(ICalendarSubMenuItem)

    title = _(u"label_calendar_menu", default=u"Calendar")
    description = _(u"title_calendar_menu", default=u"Manage calendar options for this content.")
    submenuId = "plone_contentmenu_calendaring"

    order = 4
    extra = { "id" : "plone-contentmenu-calendaring" }

    @property
    def action(self):
        return self.context.absolute_url() + "/manage_calendaring_form"

    def available(self):
        context = self.context
        member = getMultiAdapter((context, self.request), name="plone_portal_state").member()
        if IATFolder.providedBy(context) and member.has_permission('monet.calendar.extensions.ManageCalendars',
                                                                   context):
            return IMonetCalendarExtensionsLayer in browserlayerutils.registered_layers()
        return False

    def disabled(self):
        return False

    def selected(self):
        return False
