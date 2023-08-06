# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from zope.i18n import translate

from DateTime import DateTime
from Products.CMFPlone.i18nl10n import _interp_regex, datetime_formatvariables, name_formatvariables
from Products.CMFPlone.i18nl10n import weekdayname_msgid, monthname_msgid, weekdayname_msgid_abbr, monthname_msgid_abbr

from zope.component import getMultiAdapter
from zope.i18nmessageid import MessageFactory

from Acquisition import aq_inner
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from Products.Archetypes.atapi import DisplayList

from monet.calendar.event.interfaces import IMonetEvent
from monet.calendar.extensions import eventMessageFactory as _
from monet.calendar.extensions.browser.usefulforsearch import UsefulForSearchEvents

try:
    import Products.LinguaPlone
    LINGUAPLONE = True
except ImportError:
    LINGUAPLONE = False
    
try:
    # python2.6
    import json
except ImportError:
    # python2.4
    import simplejson as json


PLMF = MessageFactory('plonelocales')

SlotsVocab = {'morning':_(u'Morning'),
              'afternoon':_(u'Afternoon'),
              'night':_(u'Evening'),
              'allday':_(u'All day long')}

ParameterDatesList = ['fromYear',
                      'fromMonth',
                      'fromDay',
                      'toYear',
                      'toMonth',
                      'toDay']

def daterange(start_date, end_date):
    for n in range((end_date - start_date).days):
        yield start_date + timedelta(n)

class MonetFormSearchValidation(BrowserView):
    """Simple view for perform AJAX form validation"""

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self._translation_service = getToolByName(self.context, 'translation_service')

    def _validate(self, date_from, date_to, directLocalization=False):
        """Perform a date validation
        return the error message or an empty string is validation pass
        """
        key = default = None
        message_error = ''
        if not date_from or not date_to:
            key, default = (u'label_failed_arguments',
                            u'Dates are not valid, please retry.')
        elif self.checkInvalidDateGreaterThan(date_from,date_to):
            key, default = (u'label_failed_gtinterval',
                            u'The second date (TO) must be greater than or equal to the first date (FROM). Please re-enter dates.')
        elif self.checkInvalidDateInterval(date_from,date_to):
            key, default = (u'label_failed_interval',
                            u'The search of events must be inside a range or 60 days. Please re-enter dates.')
        if key:
            if not directLocalization:
                message_error = _(key, default=default)
            else:
                message_error = self._translation_service.utranslate(domain='monet.calendar.extensions',
                                                                     msgid=key,
                                                                     default=default,
                                                                     context=self.context)
        return message_error

    def checkInvalidDateGreaterThan(self,date_from,date_to):
        """Check the dates DAL AL"""
        if date_to >= date_from:
            return False
        else:
            return True
        
    def checkInvalidDateInterval(self,date_from,date_to):
        """Check the dates DAL AL"""
        if not (date_to - date_from).days > 60:
            return False
        else:
            return True

    def writeDate(self, day, month, year):
        """Write down the value of the date.
        Date is normalized, removing days fraction data like hour timing
        """
        try:
            return datetime(int(year), int(month), int(day)).date()
        except StandardError:
            self.context.plone_log("Error in date conversion: %s-%s-%s" % (year, month, day))
            return ''

    def toCalendarLocalizedTime(self, time):
        """Convert a date in the calendar date format"""
        time = DateTime(time.strftime("%Y-%m-%d"))

        mapping = {}
        formatstring = translate('date_format_long', 'monet.calendar.extensions', mapping,
                                 self.request, default="${A} ${B} ${d} ${Y}")
        
        # get the format elements used in the formatstring
        formatelements = _interp_regex.findall(formatstring)
        # reformat the ${foo} to foo
        formatelements = [el[2:-1] for el in formatelements]
    
        # add used elements to mapping
        elements = [e for e in formatelements if e in datetime_formatvariables]
    
        # add weekday name, abbr. weekday name, month name, abbr month name
        week_included = True
        month_included = True
    
        name_elements = [e for e in formatelements if e in name_formatvariables]
        if not ('a' in name_elements or 'A' in name_elements):
            week_included = False
        if not ('b' in name_elements or 'B' in name_elements):
            month_included = False
    
        for key in elements:
            mapping[key]=time.strftime('%'+key)
    
        if week_included:
            weekday = int(time.strftime('%w')) # weekday, sunday = 0
            if 'a' in name_elements:
                mapping['a']=weekdayname_msgid_abbr(weekday)
            if 'A' in name_elements:
                mapping['A']=weekdayname_msgid(weekday)
        if month_included:
            monthday = int(time.strftime('%m')) # month, january = 1
            if 'b' in name_elements:
                mapping['b']=monthname_msgid_abbr(monthday)
            if 'B' in name_elements:
                mapping['B']=monthname_msgid(monthday)
    
        # translate translateable elements
        for key in name_elements:
            mapping[key] = translate(mapping[key], 'plonelocales', context=self.request, default=mapping[key])
    
        # translate the time string
        return translate('date_format_long', 'monet.calendar.extensions', mapping,
                         self.request, default="${A} ${B} ${d} ${Y}")

    def __call__(self, *args, **kw):
        response = self.request.response
        response.setHeader('content-type','application/json');
        response.addHeader("Cache-Control", "no-cache")
        response.addHeader("Pragma", "no-cache")

        form = self.request.form
        date_from = self.writeDate(form.get('fromDay'),form.get('fromMonth'),form.get('fromYear'))
        date_to = self.writeDate(form.get('toDay'),form.get('toMonth'),form.get('toYear'))
        message_error = self._validate(date_from, date_to, directLocalization=True)
        
        return json.dumps({'title': self._translation_service.utranslate(domain='plone',
                                                                         msgid='Error',
                                                                         default=u'Error',
                                                                         context=self.context),
                           'error': message_error})


class MonetSearchEvents(MonetFormSearchValidation, UsefulForSearchEvents):
    """View for the events search page"""

    template = ViewPageTemplateFile("monetsearchevent.pt")
    __call__ = template

    def __getitem__(self, key):
        return self.template.macros[key]

    def notEmptyArgumentsDate(self,day,month,year):
        """Check the date viewlets's parameters"""
        if day or month or year:
            return True
        else:
            return False

    def getFromTo(self):
        """Create dates from the parameters"""
        
        date = date_from = date_to = ''
        dates = {'date':'','date_from':'','date_to':''}
        form = self.request.form
        
        if form.get('date'):
            date = form.get('date').split('-')
            date = datetime(int(date[0]),int(date[1]),int(date[2])).date()
            
        if self.notEmptyArgumentsDate(form.get('fromDay'), form.get('fromMonth'), form.get('fromYear')) or \
                        self.notEmptyArgumentsDate(form.get('toDay'), form.get('toMonth'), form.get('toYear')):
            date_from = self.writeDate(form.get('fromDay'), form.get('fromMonth'), form.get('fromYear'))
            date_to = self.writeDate(form.get('toDay'), form.get('toMonth'), form.get('toYear'))
            message_error = self._validate(date_from, date_to)
            if message_error:
                IStatusMessage(self.request).addStatusMessage(message_error,type="error")            
                # BBB: silly redirect... must perform validation BEFORE page rendering!
                url = getMultiAdapter((self.context, self.request), name='absolute_url')()
                self.request.response.redirect(url + '/@@monetsearchevents')
        
        # One day search only
        if date_from and date_to and date_to==date_from:
            dates = {'date':date or date_from}
        # Multiple days
        else:
            dates = {'date':date or date_from,'date_from':date_from,'date_to':date_to}
        
        if dates['date']:
            return dates
        return {'date': datetime.now().date()}

    def getEventsInParent(self):
        """Return all events found in the parent folder
        """
        context = aq_inner(self.context)
        pcatalog = getToolByName(self, 'portal_catalog')
        query = {}
        query['object_provides'] = IMonetEvent.__identifier__
        if self.request.form.get('path') is None:
            query['path'] = self.getSubSitePath()
            
        # Now copy al other request parameter in the catalog query
        for key in self.request.form.keys():
            if not key in ParameterDatesList:
                if self.request.form.get(key):
                    query[key] = self.request.form.get(key)
               
        try:     
            request_obj = context.unrestrictedTraverse(query['path'])
        except:
            request_obj = context
        if LINGUAPLONE:
            if not context.getLanguage() == request_obj.getLanguage():
                if request_obj.hasTranslation(context.getLanguage()):
                    query['path'] = '/'.join(request_obj.getTranslation(context.getLanguage()).getPhysicalPath())
        else:
            if not context.Language() == request_obj.Language():
                if request_obj.hasTranslation(context.Language()):
                    query['path'] = '/'.join(request_obj.getTranslation(context.Language()).getPhysicalPath())
        if query.has_key('set_language'):
            del query['set_language']
        
        brains = pcatalog.searchResults(**query)
        return brains    
    
    def getSummarySearchDates(self,dates):
        """Return a part of the summary of the search from request
        """
        if dates.get('date_from') and dates.get('date_to'):
            date_from = self.context.toLocalizedTime(dates.get('date_from').strftime('%m/%d/%Y'),long_format=0)
            date_to = self.context.toLocalizedTime(dates.get('date_to').strftime('%m/%d/%Y'),long_format=0)
            return _(u'summary_search_from_to',
                    default='from ${date_from} to ${date_to}',
                    mapping={'date_from':date_from,
                             'date_to':date_to},
                    )
        else:
            date = self.context.toLocalizedTime(dates.get('date').strftime('%m/%d/%Y'),long_format=0)
            return _(u'summary_search_in',
                    default='in ${date}',
                    mapping={'date':date},
                    )
    
    def filterEventsByDate(self, events, date):
        """Filter passed events by date"""
        filtered_events = []
        for event in events:
            if date in event.getDates:
                filtered_events.append(event)
        return filtered_events

    def filterEventsByRange(self, events, dates, datee):
        """Filter passed events a range of dates
        @return: a structure like this: [ (date_1, [event1, event2, ...]), (date_2, [event3, ...]), ... ]
        """
        filtered_events = []
        for d in daterange(dates, datee+timedelta(1)):
            filtered_events.append( (d, self.filterEventsByDate(events, d)) )
        return filtered_events
    
    def eventFound(self,list_event):
        for day in list_event:
            if day[1]:
                return True
        return False
    
    def sortedEventsBySlots(self,events):
        """Sorted events by slot"""
        
        mp = getToolByName(self,'portal_properties')
        special_event_types_pro = mp.monet_calendar_event_properties.special_event_types
        special_event_types = DisplayList()
        for etype in special_event_types_pro:
            special_event_types.add(etype,_(etype))
    
        sorted_events = {'morning':[],
                         'afternoon':[],
                         'night':[],
                         'allday':[],
                         'sequence_slots':['morning','afternoon','night','allday']}
        sorted_events_keys = sorted_events.keys()
        
        for event in events:
            inter = list(set(event.getEventType).intersection(set(special_event_types)))
            if inter:
                if not inter[0] in sorted_events['sequence_slots']:
                    sorted_events['sequence_slots'].append(inter[0])
                    sorted_events[inter[0]] = []
                sorted_events[inter[0]].append(event)
                continue
            for key in sorted_events_keys:
                if event.getSlots == key:
                    sorted_events[key].append(event)
        return sorted_events
    
    def getDateInterval(self,date_from,date_to):
        interval = []
        duration = (date_to - date_from).days
        while(duration > 0):
            day = date_to - timedelta(days=duration)
            interval.append(day)
            duration -= 1
        interval.append(date_to)
        return interval
    
    def getPreviousDate(self,date,date_from):
        if date == date_from:
            return None
        else:
            return date - timedelta(1)
    
    def getNextDate(self,date,date_to):
        if date == date_to:
            return None
        else:
            return date + timedelta(1)
        
    def getWeekdayName(self,date):
        msgid = date.isoweekday() == 7 and self._translation_service.day_msgid(0) or self._translation_service.day_msgid(date.isoweekday())
        english = date.isoweekday() == 7 and self._translation_service.weekday_english(0) or self._translation_service.weekday_english(date.isoweekday())
        return _(msgid, default=english)
        
    def getMonthName(self,date):
        msgid   = self._translation_service.month_msgid(date.month)
        english = self._translation_service.month_english(date.month)
        return PLMF(msgid, default=english)
    
    def getSlotsName(self,key):
        mp = getToolByName(self,'portal_properties')
        
        special_event_types_pro = mp.monet_calendar_event_properties.special_event_types
        special_event_types = DisplayList()
        for etype in special_event_types_pro:
            special_event_types.add(etype,_(etype))
        
        return (key in special_event_types) and special_event_types.getValue(key) or SlotsVocab[key]
