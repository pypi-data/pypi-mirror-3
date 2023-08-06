# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import time
from types import StringType
from cStringIO import StringIO

from DateTime import DateTime

from Products.Archetypes import atapi
try:
    # turn off
    from Products.LinguaPlone.public import *
except ImportError:
    # No multilingual support
    from Products.Archetypes.atapi import *

from Products.Archetypes.utils import DisplayList
from rt.calendarinandout.widget import CalendarInAndOutWidget

from Products.ATContentTypes.content import schemata
from Products.ATContentTypes.content.event import ATEventSchema, ATEvent

from Products.ATContentTypes.permission import ChangeEvents
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.permissions import View
from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.lib.calendarsupport import rfc2445dt, vformat, foldLine
from Products.ATContentTypes.lib.calendarsupport import ICS_EVENT_START, ICS_EVENT_END, VCS_EVENT_END

from monet.calendar.event import eventMessageFactory as _


RECURRING_EVENT_SCHEMA = atapi.Schema((
         
        LinesField(
            'cadence',
            required= False,
            vocabulary='_get_days_vocab',
            widget = MultiSelectionWidget(
                format = 'checkbox',
                label=_("label_cadence", default=u"Cadence"),
                description=_("description_cadence",
                              default=u"You can set the actual days of the event in the date range specified above.\n"
                                      u"If you don't set this field the event takes place every day of the week."),
                ),
            enforceVocabulary=True,
            languageIndependent=True
        ),
                                     
        LinesField(
            'except',
            required= False,
            widget = CalendarInAndOutWidget(
                label=_("label_except", default=u"Except"),
                description=_("description_field_except",
                              default=u"In this field you can set the list of days on which the event is not held.\n"
                                      u"Enter dates in the form yyyy-mm-dd."),
                auto_add=True,
                ),
            languageIndependent=True
        ),

        LinesField(
            'including',
            required= False,
            widget = CalendarInAndOutWidget(
                label=_("label_including", default=u"Including"),
                description=_("description_field_including",
                              default=u"In this field you can set the list of days on which the event is additionally held, even if excluded by other filters.\n"
                                      u"Enter dates in the form yyyy-mm-dd."),
                auto_add=True,
                ),
            languageIndependent=True
        ),

))


EventSchema = ATEventSchema.copy() + RECURRING_EVENT_SCHEMA.copy()

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

EventSchema['title'].storage = atapi.AnnotationStorage()
EventSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(EventSchema, moveDiscussion=False)
EventSchema.moveField('cadence', after='endDate')
EventSchema.moveField('except', after='cadence')
# finalizeATCTSchema moves 'location' into 'categories', we move it back:
EventSchema.changeSchemataForField('location', 'default')
EventSchema.moveField('location', before='startDate')

EventSchema['subject'].widget.visible = {'edit': 'visible'}
EventSchema['subject'].mode = 'wr'


class RecurringEvent(ATEvent):
    """Description of the Example Type"""

    schema = EventSchema

    #title = atapi.ATFieldProperty('title')
    #description = atapi.ATFieldProperty('description')
    
    # -*- Your ATSchema to Python Property Bridges Here ... -*-
    security = ClassSecurityInfo()
    
    def _get_days_vocab(self):
        return DisplayList([('0',_('Monday')),
                           ('1',_('Tuesday')),
                           ('2',_('Wednesday')),
                           ('3',_('Thursday')),
                           ('4',_('Friday')),
                           ('5',_('Saturday')),
                           ('6',_('Sunday'))])
    
    security.declareProtected(View, 'getDates')
    def getDates(self, day=None):
        """Main method that return all day in which the event occurs"""
        event_days = []
        blacklist = []
        
        try:
            exceptions = set(self.getExcept())
        except TypeError, e:
            self.plone_log(str(e))
            exceptions = self.getExcept()
            
        for black in sorted(exceptions):
            black = black.split('-')
            datee = datetime(int(black[0]),int(black[1]),int(black[2]))
            blacklist.append(datee.date())

        if day:
            if ((not self.getCadence() or str(day.weekday()) in self.getCadence()) 
                 and not day in blacklist):
                event_days.append(day)
            return event_days
         
        duration = (self._end_date().date() - self._start_date().date()).days

        while(duration > 0):
            day = self._end_date() - timedelta(days=duration)
            if (not self.getCadence() or str(day.weekday()) in self.getCadence()) and not day.date() in blacklist:
                event_days.append(day.date())
            duration = duration - 1
        if (not self.getCadence() or str(self._end_date().weekday()) in self.getCadence()) and not self._end_date().date() in blacklist:
            event_days.append(self._end_date().date())

        # now includings additional days
        # includings = set([datetime.strptime(a,'%Y-%m-%d') for a in self.getIncluding()]) # only for Python 2.5+
        includings = set([datetime(*(time.strptime(a, '%Y-%m-%d')[0:6])) for a in self.getIncluding()])
        includings.update(set(event_days))
        return tuple(includings)

    def getISODates(self):
        event_days = self.getDates()
        return [d.strftime('%Y-%m-%d') for d in event_days]
    
    security.declareProtected(View, 'getVCal')
    def getVCal(self):
        """get vCal data
        """
        event_start = self._start_date().date()
        event_end = self._end_date().date()
        event_days = self.getDates()
        
        duration = (event_end - event_start).days
        intervals = []
        interval = []
        
        while(duration > 0):
            day = event_end - timedelta(days=duration)
            if day in event_days:
                if day == event_start:
                    interval.append(self._start_date())
                else:
                    interval.append(day)
            else:
                if interval:
                    intervals.append(interval)
                    interval = []
            duration = duration - 1

        if event_end in event_days:
            interval.append(self._end_date())
        if interval:
            intervals.append(interval)

        out = StringIO()
        for interval in intervals:
            startTime = interval[0]
            endTime = interval[-1]
            if not endTime == self._end_date():
                endTime = datetime(endTime.year,endTime.month,endTime.day,23,59,00)
            if not startTime == self._start_date():
                startTime = datetime(startTime.year,startTime.month,startTime.day,00,00,00)
#            if len(intervals) == 1:
#                startTime = self._start_date()
            map = {
                'dtstamp'   : rfc2445dt(DateTime()),
                'created'   : rfc2445dt(DateTime(self.CreationDate())),
                'uid'       : self.UID() + dstartformat(interval[0]),
                'modified'  : rfc2445dt(DateTime(self.ModificationDate())),
                'summary'   : vformat(self.Title()),
                'startdate' : rfc2445dt(toDateTime(startTime)),
                'enddate'   : rfc2445dt(toDateTime(endTime)),
                }
            out.write(VCS_EVENT_START % map)
            
            description = self.Description()
            if description:
                out.write(foldLine('DESCRIPTION:%s\n' % vformat(description)))
    
            location = self.getLocation()
            if location:
                out.write('LOCATION:%s\n' % vformat(location))
                
            out.write(VCS_EVENT_END)
        
        return out.getvalue()
    
    
    security.declareProtected(View, 'getICal')
    def getICal(self):
        """get iCal data
        """
        event_start = self._start_date().date()
        event_end = self._end_date().date()
        event_days = self.getDates()
        
        duration = (event_end - event_start).days
        intervals = []
        interval = []
        
        while(duration > 0):
            day = event_end - timedelta(days=duration)
            if day in event_days:
                if day == event_start:
                    interval.append(self._start_date())
                else:
                    interval.append(day)
            else:
                if interval:
                    intervals.append(interval)
                    interval = []
            duration = duration - 1
 
        if event_end in event_days:
            interval.append(self._end_date())
        if interval:
            intervals.append(interval)
            
        out = StringIO()
        for interval in intervals:
            startTime = interval[0]
            endTime = interval[-1]
            if not endTime == self._end_date():
                endTime = datetime(endTime.year,endTime.month,endTime.day,23,59,00)
            if not startTime == self._start_date():
                startTime = datetime(startTime.year,startTime.month,startTime.day,00,00,00)
#            if len(intervals) == 1:
#                startTime = self._start_date()
            map = {
                'dtstamp'   : rfc2445dt(DateTime()),
                'created'   : rfc2445dt(DateTime(self.CreationDate())),
                'uid'       : self.UID() + dstartformat(interval[0]),
                'modified'  : rfc2445dt(DateTime(self.ModificationDate())),
                'summary'   : vformat(self.Title()),
                'startdate' : rfc2445dt(toDateTime(startTime)),
                'enddate'   : rfc2445dt(toDateTime(endTime)),
                }
            out.write(ICS_EVENT_START % map)
            
            description = self.Description()
            if description:
                out.write(foldLine('DESCRIPTION:%s\n' % vformat(description)))
    
            location = self.getLocation()
            if location:
                out.write('LOCATION:%s\n' % vformat(location))
    
            eventType = self.getEventType()
            if eventType:
                out.write('CATEGORIES:%s\n' % ','.join(eventType))
    
            # TODO  -- NO! see the RFC; ORGANIZER field is not to be used for non-group-scheduled entities
            #ORGANIZER;CN=%(name):MAILTO=%(email)
            #ATTENDEE;CN=%(name);ROLE=REQ-PARTICIPANT:mailto:%(email)
    
            cn = []
            contact = self.contact_name()
            if contact:
                cn.append(contact)
            phones = self.contact_phone()
            for phone in phones:
                cn.append(phone)
            emails = self.contact_email()
            for email in emails:
                cn.append(email)
            if cn:
                out.write('CONTACT:%s\n' % ', '.join(cn))
                
            url = self.event_url()
            if url:
                out.write('URL:%s\n' % ', '.join(url))
    
            out.write(ICS_EVENT_END)
        
        return out.getvalue()
    
    
    security.declareProtected(ChangeEvents, 'setEventType')
    def setEventType(self, value, alreadySet=False, **kw):
        """CMF compatibility method

        Changing the event type.
        """
        if type(value) is StringType:
            value = (value,)
        elif not value:
            # mostly harmless?
            value = ()
        f = self.getField('eventType')
        f.set(self, value, **kw) # set is ok

    security.declareProtected(ModifyPortalContent, 'setSubject')
    def setSubject(self, value, **kw):
        """CMF compatibility method

        Changing the subject.
        """
        f = self.getField('subject')
        f.set(self, value, **kw) # set is ok

    security.declareProtected(ModifyPortalContent, 'setExcept')
    def setExcept(self, value, **kw):
        """
        Setting exception the clean way:
         - remove dups
         - sort elements
        """
        if value is None:
            return
        if not isinstance(value,list):
            value = [value,]
        f = self.getField('except')
        f.set(self, sorted(set(value)), **kw) # set is ok
        
    def post_validate(self, REQUEST, errors):
        """Check to make sure that the user give date in the right format/range"""
        
        blacklist = REQUEST.get('except', [])
        blacklist = set(blacklist)
        cadence = [int(x) for x in REQUEST.get('cadence', []) if x]

        startdate = REQUEST.get('startDate',None)
        if startdate:
            try:
                startdate = startdate.split(' ')[0].split('-')
                startdate = datetime(int(startdate[0]),int(startdate[1]),int(startdate[2])).date()
            except:
                errors['except'] = _("description_except",
                                     default=u'Enter the dates in the form yyyy-mm-dd')

        enddate = REQUEST.get('endDate',None)
        if enddate:
            try:
                enddate = enddate.split(' ')[0].split('-')
                enddate = datetime(int(enddate[0]),int(enddate[1]),int(enddate[2])).date()
            except:
                errors['except'] = _("description_except",
                                     default=u'Enter the dates in the form yyyy-mm-dd')

        # 1) Basic field validation
        for black in blacklist:
            try:
                black = black.split('-')
                datee = datetime(int(black[0]), int(black[1]), int(black[2])).date()
            except:
                errors['except'] = _("description_except",
                                     default=u'Enter the dates in the form yyyy-mm-dd')
                return errors

            if startdate:
                if datee < startdate:
                    errors['except'] = _("interval_except",
                                         default=u'One or more dates are not in the previous range [Start event - End event]')
                    return errors
            if enddate:
                if datee > enddate:
                    errors['except'] = _("interval_except",
                                         default=u'One or more dates are not in the previous range [Start event - End event]')
                    return errors

        # 2) Check if cadence fill event start and end
        if cadence and (startdate or enddate):
            startOk = False
            endOk = False
            for c in cadence:
                if startdate and startdate.weekday()==c:
                    startOk = True
                if enddate and enddate.weekday()==c:
                    endOk = True
            if not startOk and startdate:
                errors['startDate'] = _("cadence_bound_except_start",
                                     default=u'The start date is not a valid date because is not in the cadence set.')
                return errors
            if not endOk and enddate:
                errors['endDate'] = _("cadence_bound_except_end",
                                     default=u'The end date is not a valid date because is not in the cadence set.')
                return errors

        # 3) Check if except will not skip event start or end
        if blacklist and (startdate or enddate):
            for black in blacklist:
                black = black.split('-')
                datee = datetime(int(black[0]), int(black[1]), int(black[2])).date()
                if startdate and datee==startdate:
                    errors['startDate'] = _("except_bound_except_start",
                                         default=u'The start date is not a valid date because an except entry invalidate it.')
                    return errors
                if enddate and datee==enddate:
                    errors['endDate'] = _("except_bound_except_end",
                                         default=u'The end date is not a valid date because an except entry invalidate it.')
                    return errors


def toDateTime(time):
    try:
        returntime = DateTime(time.year,time.month,time.day,time.hour,time.minute,time.second)
    except AttributeError:
        returntime = DateTime(time.year,time.month,time.day)
    return returntime

def dstartformat(time):
    return toDateTime(time).strftime("%Y%m%d")

VCS_EVENT_START = """\
BEGIN:VEVENT
DTSTART:%(startdate)s
DTEND:%(enddate)s
UID:ATEvent-%(uid)s
SEQUENCE:0
LAST-MODIFIED:%(modified)s
SUMMARY:%(summary)s
"""
