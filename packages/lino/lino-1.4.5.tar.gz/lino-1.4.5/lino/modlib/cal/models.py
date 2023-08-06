# -*- coding: UTF-8 -*-
## Copyright 2011-2012 Luc Saffre
## This file is part of the Lino project.
## Lino is free software; you can redistribute it and/or modify 
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 3 of the License, or
## (at your option) any later version.
## Lino is distributed in the hope that it will be useful, 
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
## GNU General Public License for more details.
## You should have received a copy of the GNU General Public License
## along with Lino; if not, see <http://www.gnu.org/licenses/>.

"""
This module turns Lino into a basic calendar client. 
To be combined with :attr:`lino.Lino.use_extensible`.
Supports remote calendars.
Events and Tasks can get attributed to a :attr:`Project <lino.Lino.project_model>`.

"""
import logging
logger = logging.getLogger(__name__)

import cgi
import datetime
import dateutil

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy
#~ from django.utils.translation import string_concat
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_unicode

from lino import mixins
from lino import dd
#~ from lino.core import reports
from lino.core import actions
from lino.utils import babel
from lino.utils import AttrDict
from lino.ui import requests as ext_requests
from lino.core.modeltools import resolve_model, obj2str
#~ from lino.core.perms import UserProfiles

from lino.modlib.contacts import models as contacts

from lino.modlib.outbox import models as outbox 
from lino.modlib.postings import models as postings
#~ postings = dd.resolve_app('postings')


from lino.modlib.cal.utils import \
    Weekday, DurationUnits, setkw, dt2kw, EventState, GuestState, TaskState, AccessClasses
#~ from lino.modlib.cal.utils import EventStatus, \
    #~ TaskStatus, DurationUnit, Priority, AccessClass, \
    #~ GuestStatus, setkw, dt2kw

from lino.utils.babel import dtosl



class CalendarType(object):
    
    def validate_calendar(self,cal):
        pass
        
class LocalCalendar(CalendarType):
    label = "Local Calendar"
  
class GoogleCalendar(CalendarType):
    label = "Google Calendar"
    def validate_calendar(self,cal):
        if not cal.url_template:
            cal.url_template = \
            "https://%(username)s:%(password)s@www.google.com/calendar/dav/%(username)s/"
  
CALENDAR_CHOICES = []
CALENDAR_DICT = {}

def register_calendartype(name,instance):
    CALENDAR_DICT[name] = instance
    CALENDAR_CHOICES.append((name,instance.label))
    
register_calendartype('local',LocalCalendar())
register_calendartype('google',GoogleCalendar())
    
COLOR_CHOICES = [i + 1 for i in range(32)]
  
from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator



#~ class Calendar(mixins.UserAuthored):
class Calendar(mixins.PrintableType,outbox.MailableType,babel.BabelNamed):
    """
    A Calendar is a collection of events and tasks.
    There are local calendars and remote calendars.
    Remote calendars will be synchronized by
    :mod:`lino.modlib.cal.management.commands.watch_calendars`,
    and local modifications will be sent back to the remote calendar.
    """
    
    templates_group = 'cal/Event'
    
    class Meta:
        verbose_name = _("Calendar")
        verbose_name_plural = _("Calendars")
        
    type = models.CharField(_("Type"),max_length=20,
        default='local',
        choices=CALENDAR_CHOICES)
    #~ name = models.CharField(_("Name"),max_length=200)
    description = dd.RichTextField(_("Description"),blank=True,format='html')
    url_template = models.CharField(_("URL template"),
        max_length=200,blank=True) # ,null=True)
    username = models.CharField(_("Username"),
        max_length=200,blank=True) # ,null=True)
    password = dd.PasswordField(_("Password"),
        max_length=200,blank=True) # ,null=True)
    readonly = models.BooleanField(_("read-only"),default=False)
    invite_team_members = models.BooleanField(
        _("Invite team members"),default=False)
    #~ is_default = models.BooleanField(
        #~ _("is default"),default=False)
    #~ is_private = models.BooleanField(
        #~ _("private"),default=False,help_text=_("""\
#~ Whether other users may subscribe to this Calendar."""))
    start_date = models.DateField(
        verbose_name=_("Start date"),
        blank=True,null=True)
    color = models.IntegerField(
        _("color"),default=1,
        validators=[MinValueValidator(1), MaxValueValidator(32)]
        )
        #~ choices=COLOR_CHOICES)
    
    #~ def full_clean(self,*args,**kw):
        #~ if not self.name:
            #~ if self.username:
                #~ self.name = self.username
            #~ elif self.user is None:
                #~ self.name = "Anonymous"
            #~ else:
                #~ self.name = self.user.get_full_name()
        #~ super(Calendar,self).full_clean(*args,**kw)
        
    def save(self,*args,**kw):
        ct = CALENDAR_DICT.get(self.type)
        ct.validate_calendar(self)
        super(Calendar,self).save(*args,**kw)
        #~ if self.is_default: # and self.user is not None:
            #~ for cal in Calendar.objects.filter(user=self.user):
                #~ if cal.pk != self.pk and cal.is_default:
                    #~ cal.is_default = False
                    #~ cal.save()

    def get_url(self):
        if self.url_template:
            return self.url_template % dict(
              username=self.username,
              password=self.password)
        return ''
                    
    def __unicode__(self):
        return self.name
        
    #~ def color(self,request):
        #~ return settings.LINO.get_calendar_color(self,request)
    #~ color.return_type = models.IntegerField(_("Color"))
        
        
    
class Calendars(dd.Table):
    required = dict(user_groups='office',user_level='manager')
    model = 'cal.Calendar'
    column_names = "name type color readonly build_method template *"
    
    detail_template = """
    type name id 
    # description
    url_template username password
    readonly invite_team_members color start_date
    build_method template email_template attach_to_email
    EventsByCalendar
    # SubscriptionsByCalendar
    """

#~ def default_calendar(user):
    #~ """
    #~ Returns or creates the default calendar for the given user.
    #~ """
    #~ try:
        #~ return Calendar.objects.get(user=user,is_default=True)
    #~ except Calendar.DoesNotExist,e:
        #~ color = Calendar.objects.all().count() + 1
        #~ while color > 32:
            #~ color -= 32
        #~ cal = Calendar(user=user,is_default=True,color=color)
        #~ cal.full_clean()
        #~ cal.save()
        #~ logger.debug(u"Created default calendar for %s.",user)
        #~ return cal





class Subscription(mixins.UserAuthored):
    """
    A Suscription is when a User subscribes to some Calendar.
    
    :user: points to the author (recipient) of this subscription
    :calendar: points to the Calendar to subscribe
    
    """
    
    class Meta:
        verbose_name = _("Subscription")
        verbose_name_plural = _("Subscriptions")
        
    #~ quick_search_fields = ('user__username','user__first_name','user__last_name')
    

    calendar = models.ForeignKey(Calendar,help_text=_("""\
The calendar you want to subscribe to.
You can subscribe to *non-private* calendars of *other* users."""))
    is_hidden = models.BooleanField(
        _("hidden"),default=False,help_text=_("""\
Whether this subscription should initially be hidden in your calendar panel."""))
    

    
        
class Subscriptions(dd.Table):
    required = dict(user_groups='office',user_level='manager')
    model = Subscription

class SubscriptionsByCalendar(Subscriptions):
    master_key = 'calendar'

class SubscriptionsByUser(Subscriptions):
    required = dict(user_groups='office')
    master_key = 'user'

#~ class MySubscriptions(Subscriptions,mixins.ByUser):
    #~ pass



class Membership(mixins.UserAuthored):
    """
    A Membership is when a User decides that subscribes to somebody else's Calendar.
    
    :user: points to the author (recipient) of this membership
    :watched_user: points to the watched user
    
    """
    
    class Meta:
        verbose_name = _("Membership")
        verbose_name_plural = _("Memberships")
        
    #~ quick_search_fields = ('user__username','user__first_name','user__last_name')
    
    watched_user = models.ForeignKey(settings.LINO.user_model,
        help_text=_("""\
The user whose calendar events you want to see in team view."""))



    @dd.chooser()
    def watched_user_choices(cls,user):
        return settings.LINO.user_model.objects.exclude(
            profile=dd.UserProfiles.blank_item).exclude(id=user.id)
    
        
class Memberships(dd.Table):
    required = dict(user_groups='office',user_level='manager')
    model = Membership


class MembershipsByUser(Memberships):
    required = dict(user_groups='office')
    master_key = 'user'
    label = _("Team Members")












class Place(babel.BabelNamed):
    """
    A location where Events can happen.
    For a given Place you can see the :class:`EventsByPlace` 
    that happened (or will happen) there.
    """
    class Meta:
        verbose_name = _("Place")
        verbose_name_plural = _("Places")
        
    #~ name = models.CharField(_("Name"),max_length=200)
    #~ def __unicode__(self):
        #~ return self.name 
  
class Places(dd.Table):
    required = dict(user_groups='office')
    model = Place
    detail_layout = """
    id name
    cal.EventsByPlace
    """
    
class Priority(babel.BabelNamed):
    "The priority of a Task or Event."
    class Meta:
        verbose_name = _("Priority")
        verbose_name_plural = _('Priorities')
    ref = models.CharField(max_length='1')
class Priorities(dd.Table):
    required = dict(user_groups='office')
    model = Priority
    column_names = 'name *'

#~ class AccessClass(babel.BabelNamed):
    #~ "The access class of a Task or Event."
    #~ required = dict(user_groups='office')
    #~ class Meta:
        #~ verbose_name = _("Access Class")
        #~ verbose_name_plural = _('Access Classes')
    #~ ref = models.CharField(max_length='1')
#~ class AccessClasses(dd.Table):
    #~ model = AccessClass
    #~ column_names = 'name *'



#~ class EventType(mixins.PrintableType,outbox.MailableType,babel.BabelNamed):
    #~ """The type of an Event.
    #~ Determines which build method and template to be used for printing the event.
    #~ """
  
    #~ templates_group = 'cal/Event'
    
    #~ class Meta:
        #~ verbose_name = pgettext_lazy(u"cal",u"Event Type")
        #~ verbose_name_plural = pgettext_lazy(u"cal",u'Event Types')

#~ class EventTypes(dd.Table):
    #~ model = EventType
    #~ required = dict(user_groups='office')
    #~ column_names = 'name build_method template *'
    #~ detail_template = """
    #~ id name
    #~ build_method template email_template attach_to_email
    #~ cal.EventsByType
    #~ """



    
    
#~ class AutoEvent(object):
    #~ def __init__(self,auto_id,user,date,subject,owner,start_time,end_time):
        #~ self.auto_id = auto_id
        #~ self.user = user
        #~ self.date = date
        #~ self.subject = subject
        #~ self.owner = owner
        #~ self.start_time = start_time
        #~ self.end_time = end_time
    
    
class EventGenerator(mixins.UserAuthored):
    """
    Base class for things that generate a suite of events.
    Examples
    :class:`isip.Contract`,     :class:`jobs.Contract`, 
    :class:`schools.Course`
    """
    
    class Meta:
        abstract = True
        
    def save(self,*args,**kw):
        super(EventGenerator,self).save(*args,**kw)
        self.update_reminders()
  
    def update_cal_rset(self):
        return self.exam_policy
        
    def update_cal_from(self):
        return self.applies_from
        
    #~ def update_cal_event_type(self,i):
    def update_cal_calendar(self,i):
        return None
        
    def update_cal_until(self):
        return self.date_ended or self.applies_until
        
    def update_cal_subject(self,i):
        raise NotImplementedError()
        #~ return _("Evaluation %d") % i

    def update_reminders(self):
        """
        Generate automatic calendar events owned by this contract.
        
        [NOTE1] if one event has been manually rescheduled, all following events
        adapt to the new rythm.
        
        """
        return self.update_auto_events()
            
        #~ rset = self.update_cal_rset()
        #~ if rset and rset.every > 0 and rset.every_unit:
            #~ date = self.update_cal_from()
            #~ defaults = dict(start_time=rset.start_time,end_time=rset.end_time)
        #~ else:
            #~ date = None
            #~ defaults = dict()
        #~ until = self.update_cal_until()
        #~ if not until:
            #~ date = None
        #~ for i in range(settings.LINO.max_auto_events):
            #~ if date:
                #~ date = rset.every_unit.add_duration(date,rset.every)
                #~ if until and date > until:
                    #~ date = None
            #~ subject = self.update_cal_subject(i)
            #~ e = update_auto_event(
              #~ i + 1,
              #~ self.user,
              #~ date,subject,self,
              #~ **defaults)
            #~ if e: # [NOTE1]
                #~ date = e.start_date
                
    def update_auto_events(self):
        if settings.LINO.loading_from_dump: 
            #~ print "20111014 loading_from_dump"
            return 
        qs = self.get_existing_auto_events()
        wanted = self.get_wanted_auto_events()
        current = 0
        #~ LEN = len(wanted)
        
        msg = obj2str(self)
        msg += ", qs=" + str([e.auto_type for e in qs])
        msg += ", wanted=" + str([babel.dtos(e.start_date) for e in wanted.values()])
        #~ logger.info('20120707 ' + msg)
        
        for e in qs:
            ae = wanted.pop(e.auto_type,None)
            if ae is None:
                # there is an unwanted event in the database
                if not e.is_user_modified():
                    e.delete()
                #~ else:
                    #~ e.auto_type = None
                    #~ e.save()
            elif e.is_user_modified():
                if e.start_date != ae.start_date:
                    # modify subsequent dates
                    delta = e.start_date - ae.start_date
                    for se in wanted.values():
                        se.start_date += delta
            else:
                self.compare_auto_event(e,ae)
        # create new Events for remaining wanted
        for ae in wanted.values():
            Event(**ae).save()
            
    def compare_auto_event(self,obj,ae):
        original_state = dict(obj.__dict__)
        if obj.user != ae.user:
            obj.user = ae.user
        summary = force_unicode(ae.summary)
        if obj.summary != summary:
            obj.summary = summary
        if obj.start_date != ae.start_date:
            obj.start_date = ae.start_date
        if obj.start_time != ae.start_time:
            obj.start_time = ae.start_time
        if obj.end_time != ae.end_time:
            obj.end_time = ae.end_time
        if obj.calendar != ae.calendar:
            obj.calendar = ae.calendar
        if obj.__dict__ != original_state:
            obj.save()
      
    def get_wanted_auto_events(self):
        wanted = dict()
        rset = self.update_cal_rset()
        if rset and rset.every > 0 and rset.every_unit:
            date = self.update_cal_from()
            if not date:
                return wanted
        else:
            return wanted
        until = self.update_cal_until()
        if not until:
            return wanted
        i = 0
        obsolete = datetime.date.today() + datetime.timedelta(days=-7)
        while i <= settings.LINO.max_auto_events:
            i += 1
            date = rset.every_unit.add_duration(date,rset.every)
            if date > until:
                return wanted
            if date > obsolete:
                wanted[i] = AttrDict(
                    auto_type=i,
                    user=self.user,
                    start_date=date,
                    summary=self.update_cal_subject(i),
                    owner=self,
                    calendar=self.update_cal_calendar(i),
                    start_time=rset.start_time,
                    end_time=rset.end_time)
        return wanted
                    
        
    def get_existing_auto_events(self):
        ot = ContentType.objects.get_for_model(self.__class__)
        return Event.objects.filter(
            owner_type=ot,owner_id=self.pk,
            auto_type__isnull=False).order_by('auto_type')
        
        #~ if date and date >= datetime.date.today() + datetime.timedelta(days=-7):
            #~ defaults.setdefault('user',user)
            #~ obj,created = model.objects.get_or_create(
              #~ defaults=defaults,
              #~ owner_id=owner.pk,
              #~ owner_type=ot,
              #~ auto_type=autotype)
            #~ if not obj.is_user_modified():
                #~ original_state = dict(obj.__dict__)
                #~ if obj.user != user:
                    #~ obj.user = user
                #~ summary = force_unicode(summary)
                #~ if obj.summary != summary:
                    #~ obj.summary = summary
                #~ if obj.start_date != date:
                    #~ obj.start_date = date
                #~ if created or obj.__dict__ != original_state:
                    #~ obj.save()
            #~ return obj
                


#~ class EventStatus(babel.BabelNamed):
    #~ "The status of an Event."
    #~ class Meta:
        #~ verbose_name = _("Event Status")
        #~ verbose_name_plural = _('Event Statuses')
    #~ ref = models.CharField(max_length='1')
    #~ reminder = models.BooleanField(_("Reminder"),default=True)
    
#~ class EventStatuses(dd.Table):
    #~ model = EventStatus
    #~ column_names = 'name *'

#~ class TaskStatus(babel.BabelNamed):
    #~ "The status of a Task."
    #~ class Meta:
        #~ verbose_name = _("Task Status")
        #~ verbose_name_plural = _('Task Statuses')
    #~ ref = models.CharField(max_length='1')
#~ class TaskStatuses(dd.Table):
    #~ model = TaskStatus
    #~ column_names = 'name *'

#~ class GuestStatus(babel.BabelNamed):
    #~ "The status of a Guest."
    #~ class Meta:
        #~ verbose_name = _("Guest Status")
        #~ verbose_name_plural = _('Guest Statuses')
    #~ ref = models.CharField(max_length='1')
#~ class GuestStatuses(dd.Table):
    #~ model = GuestStatus
    #~ column_names = 'name *'

#~ class CalendarRelated(mixins.UserAuthored):
    #~ "Deserves more documentation."
    #~ class Meta:
        #~ abstract = True
        
    #~ calendar = models.ForeignKey(Calendar,verbose_name=_("Calendar"),blank=True)
    
    #~ def full_clean(self,*args,**kw):
        #~ self.before_clean()
        #~ super(CalendarRelated,self).full_clean(*args,**kw)
        
    #~ def save(self,*args,**kw):
        #~ self.before_clean()
        #~ super(CalendarRelated,self).save(*args,**kw)
        
    #~ def before_clean(self):
        #~ """
        #~ Called also from `save()` because `get_or_create()` 
        #~ doesn't call full_clean().
        #~ We cannot do this only in `save()` because otherwise 
        #~ `full_clean()` (when called) will complain 
        #~ about the empty fields.
        
        #~ If an administrator changes the user of an Event, 
        #~ the calendar should change accordingly
        
        #~ """
        #~ if not self.calendar_id:
            #~ self.calendar = default_calendar(self.user)
        #~ if self.calendar.user != self.user:
            #~ self.calendar = default_calendar(self.user)
            
    #~ @dd.chooser()
    #~ def calendar_choices(cls,user):
        #~ return Calendar.objects.filter(user=user)
        
    #~ def user_changed(self,ar):
        #~ """
        #~ """
        #~ self.before_clean()
            

class Started(dd.Model):
    class Meta:
        abstract = True
        
    start_date = models.DateField(
        blank=True,null=True,
        verbose_name=_("Start date")) # iCal:DTSTART
    start_time = models.TimeField(
        blank=True,null=True,
        verbose_name=_("Start time"))# iCal:DTSTART
    #~ start = dd.FieldSet(_("Start"),'start_date start_time')

    def save(self,*args,**kw):
        """
        Fills default value "today" to start_date
        """
        if not self.start_date:
            self.start_date = datetime.date.today()
        super(Started,self).save(*args,**kw)
        
    def set_datetime(self,name,value):
        """
        Given a datetime `value`, update the two corresponding 
        fields `FOO_date` and `FOO_time` 
        (where FOO is specified in `name` which must be 
        either "start" or "end").
        """
        #~ logger.info("20120119 set_datetime(%r)",value)
        setattr(self,name+'_date',value.date())
        t = value.time()
        if not t:
            t = None
        setattr(self,name+'_time',t)
        
    def get_datetime(self,name,altname=None):
        """
        Return a `datetime` value from the two corresponding 
        date and time fields.
        `name` can be 'start' or 'end'.
        """
        d = getattr(self,name+'_date')
        t = getattr(self,name+'_time')
        if not d and altname is not None: 
            d = getattr(self,altname+'_date')
            if not t and altname is not None: 
                t = getattr(self,altname+'_time')
        if not d: return None
        if t:
            return datetime.datetime.combine(d,t)
        else:
            return datetime.datetime(d.year,d.month,d.day)
        
class Ended(dd.Model):
    class Meta:
        abstract = True
    end_date = models.DateField(
        blank=True,null=True,
        verbose_name=_("End Date"))
    end_time = models.TimeField(
        blank=True,null=True,
        verbose_name=_("End Time"))
    #~ end = dd.FieldSet(_("End"),'end_date end_time')
    
  
    
class ComponentBase(mixins.ProjectRelated,Started):
    """
    Abstract model used as base class for 
    both :class:`Event` and :class:`Task`.
    """
    class Meta:
        abstract = True
        
    uid = models.CharField(_("UID"),
        max_length=200,
        blank=True) # ,null=True)

    summary = models.CharField(_("Summary"),max_length=200,blank=True) # iCal:SUMMARY
    description = dd.RichTextField(_("Description"),blank=True,format='html')
    
    def __unicode__(self):
        return self._meta.verbose_name + " #" + str(self.pk)

    def summary_row(self,ar,**kw):
        html = mixins.ProjectRelated.summary_row(self,ar,**kw)
        if self.summary:
            html += '&nbsp;: %s' % cgi.escape(force_unicode(self.summary))
            #~ html += ui.href_to(self,force_unicode(self.summary))
        html += _(" on ") + babel.dtos(self.start_date)
        return html
        

class RecurrenceSet(ComponentBase,Ended):
    """
    Abstract base for models that group together all instances 
    of a set of recurring calendar components.
    
    Thanks to http://www.kanzaki.com/docs/ical/rdate.html
    
    """
    class Meta:
        abstract = True
        verbose_name = _("Recurrence Set")
        verbose_name_plural = _("Recurrence Sets")
    
    every = models.IntegerField(_("Evaluation every X months"),
        default=0)
    every_unit = DurationUnits.field(_("Duration unit"),
        default=DurationUnits.months,
        blank=True) # iCal:DURATION
        
    calendar = models.ForeignKey(Calendar,null=True,blank=True)
    #~ event_type = models.ForeignKey(EventType,null=True,blank=True)
    
    #~ rdates = models.TextField(_("Recurrence dates"),blank=True)
    #~ exdates = models.TextField(_("Excluded dates"),blank=True)
    #~ rrules = models.TextField(_("Recurrence Rules"),blank=True)
    #~ exrules = models.TextField(_("Exclusion Rules"),blank=True)
    
class RecurrenceSets(dd.Table):
    """
    The list of all :class:`Recurrence Sets <RecurrenceSet>`.
    """
    model = RecurrenceSet
    required = dict(user_groups='office')
    
    detail_template = """
    id calendar uid summary start_date start_time
    description
    """
    #~ """
    #~ ## rdates exdates rrules exrules
    #~ ## EventsBySet    
    #~ """
    
    
class Component(ComponentBase,
                #~ CalendarRelated,
                mixins.UserAuthored,
                mixins.Controllable,
                mixins.CreatedModified):
    """
    Abstract base class for :class:`Event` and :class:`Task`.
    
    """
    workflow_state_field = 'state'
    
    class Meta:
        abstract = True
        
    calendar = models.ForeignKey(Calendar,verbose_name=_("Calendar"),blank=True,null=True)
        
    access_class = AccessClasses.field(help_text=_("""\
Whether this is private, public or between.""")) # iCal:CLASS
    #~ access_class = models.ForeignKey(AccessClass,
        #~ blank=True,null=True,
        #~ help_text=_("""\
#~ Indicates whether this is private or public (or somewhere between)."""))
    sequence = models.IntegerField(_("Revision"),default=0)
    #~ alarm_value = models.IntegerField(_("Value"),null=True,blank=True,default=1)
    #~ alarm_unit = DurationUnit.field(_("Unit"),blank=True,
        #~ default=DurationUnit.days.value) # ,null=True) # note: it's a char field!
    #~ alarm = dd.FieldSet(_("Alarm"),'alarm_value alarm_unit')
    #~ dt_alarm = models.DateTimeField(_("Alarm time"),
        #~ blank=True,null=True,editable=False)
        
    auto_type = models.IntegerField(null=True,blank=True,editable=False) 
    
    #~ user_modified = models.BooleanField(_("modified by user"),
        #~ default=False,editable=False) 
    
    #~ rset = models.ForeignKey(RecurrenceSet,
        #~ verbose_name=_("Recurrence Set"),
        #~ blank=True,null=True)
    #~ rparent = models.ForeignKey('self',verbose_name=_("Recurrence parent"),blank=True,null=True)
    #~ rdate = models.TextField(_("Recurrence date"),blank=True)
    #~ exdate = models.TextField(_("Excluded date(s)"),blank=True)
    #~ rrules = models.TextField(_("Recurrence Rules"),blank=True)
    #~ exrules = models.TextField(_("Exclusion Rules"),blank=True)
    
    #~ def get_mailable_contacts(self):
        #~ yield ('to',self.project)
    
        
        
    def save(self,*args,**kw):
        if not self.calendar:
            self.calendar = self.user.calendar
        if not self.access_class:
            self.access_class = self.user.access_class
            #~ self.access_class = AccessClasses.public
        super(Component,self).save(*args,**kw)
        
    def on_duplicate(self,ar,master):
        self.auto_type = None
        
    def disabled_fields(self,ar):
        if self.auto_type:
            #~ return settings.LINO.TASK_AUTO_FIELDS
            return self.DISABLED_AUTO_FIELDS
        return []
        
    def get_uid(self):
        """
        This is going to be used when sending 
        locally created components to a remote calendar.
        """
        if self.uid:
            return self.uid
        if not settings.LINO.uid:
            raise Exception('Cannot create local calendar components because settings.LINO.uid is empty.')
        return "%s@%s" % (self.pk,settings.LINO.uid)
            

    def is_user_modified(self):
        return self.state
        
    def on_user_change(self,request):
        raise NotImplementedError
        #~ self.user_modified = True
        
    #~ def summary_row(self,ui,rr,**kw):
        #~ html = contacts.PartnerDocument.summary_row(self,ui,rr,**kw)
        #~ if self.summary:
            #~ html += '&nbsp;: %s' % cgi.escape(force_unicode(self.summary))
        #~ html += _(" on ") + babel.dtos(self.start_date)
        #~ return html
        
    def summary_row(self,ar,**kw):
        #~ logger.info("20120217 Component.summary_row() %s", self)
        #~ if self.owner and not self.auto_type:
        #~ html = ui.ext_renderer.href_to(self)
        html = ar.renderer.href_to(self)
        if self.start_time:
            #~ html += _(" at ") + unicode(self.start_time)
            html += _(" at ") + self.start_time.strftime(settings.LINO.time_format_strftime)
        if self.state:
            html += ' [%s]' % cgi.escape(force_unicode(self.state))
        if self.summary:
            html += '&nbsp;: %s' % cgi.escape(force_unicode(self.summary))
            #~ html += ui.href_to(self,force_unicode(self.summary))
        #~ html += _(" on ") + babel.dtos(self.start_date)
        #~ if self.owner and not self.owner.__class__.__name__ in ('Person','Company'):
            #~ html += " (%s)" % reports.summary_row(self.owner,ui,rr)
        if self.project:
            html += " (%s)" % dd.summary_row(self.project,ar)
            #~ print 20120217, self.project.__class__, self
            #~ html += " (%s)" % self.project.summary_row(ui)
        return html
        #~ return super(Event,self).summary_row(ui,rr,**kw)
        
#~ Component.owner.verbose_name = _("Automatically created by")

class ExtAllDayField(dd.VirtualField):
    """
    An editable virtual field needed for 
    communication with the Ext.ensible CalendarPanel
    because we consider the "all day" checkbox 
    equivalent to "empty start and end time fields".
    """
    
    editable = True
    
    def __init__(self,*args,**kw):
        dd.VirtualField.__init__(self,models.BooleanField(*args,**kw),None)
        
    def set_value_in_object(self,request,obj,value):
        if value:
            obj.end_time = None
            obj.start_time = None
        else:
            if not obj.start_time:
                obj.start_time = datetime.time(9,0,0)
            if not obj.end_time:
                obj.end_time = datetime.time(10,0,0)
        #~ obj.save()
        
    def value_from_object(self,obj,ar):
        #~ logger.info("20120118 value_from_object() %s",obj2str(obj))
        return (obj.start_time is None)
        
#~ from lino.modlib.workflows import models as workflows # Workflowable

#~ class Components(dd.Table):
#~ # class Components(dd.Table,workflows.Workflowable):
  
    #~ workflow_owner_field = 'user'    
    #~ workflow_state_field = 'state'
    
    #~ def disable_editing(self,request):
    #~ def get_row_permission(cls,row,user,action):
        #~ if row.rset: return False
        
    #~ @classmethod
    #~ def get_row_permission(cls,action,user,row):
        #~ if not action.readonly:
            #~ if row.user != user and user.level < UserLevel.manager: 
                #~ return False
        #~ if not super(Components,cls).get_row_permission(action,user,row):
            #~ return False
        #~ return True




#~ bases = (Component,Ended,mixins.TypedPrintable,outbox.Mailable, postings.Postable)
#~ class Event(*bases):
class Event(Component,Ended,
    mixins.TypedPrintable,
    outbox.Mailable, 
    postings.Postable):
    """
    A Calendar Event (french "Rendez-vous", german "Termin") 
    is a scheduled lapse of time where something happens.
    """
    
    class Meta:
        #~ abstract = True
        verbose_name = pgettext_lazy(u"cal",u"Event")
        verbose_name_plural = pgettext_lazy(u"cal",u"Events")
        
    transparent = models.BooleanField(_("Transparent"),default=False,help_text=_("""\
Indicates that this Event shouldn't prevent other Events at the same time."""))
    #~ type = models.ForeignKey(EventType,null=True,blank=True)
    place = models.ForeignKey(Place,null=True,blank=True) # iCal:LOCATION
    priority = models.ForeignKey(Priority,null=True,blank=True)
    #~ priority = Priority.field(_("Priority"),blank=True) # iCal:PRIORITY
    state = EventState.field(blank=True) # iCal:STATUS
    #~ status = models.ForeignKey(EventStatus,verbose_name=_("Status"),blank=True,null=True) # iCal:STATUS
    #~ duration = dd.FieldSet(_("Duration"),'duration_value duration_unit')
    #~ duration_value = models.IntegerField(_("Duration value"),null=True,blank=True) # iCal:DURATION
    #~ duration_unit = DurationUnit.field(_("Duration unit"),blank=True) # iCal:DURATION
    #~ repeat_value = models.IntegerField(_("Repeat every"),null=True,blank=True) # iCal:DURATION
    #~ repeat_unit = DurationUnit.field(verbose_name=_("Repeat every"),null=True,blank=True) # iCal:DURATION
    all_day = ExtAllDayField(_("all day"))
    #~ all_day = models.BooleanField(_("all day"),default=False)
    
    
    #~ def compute_times(self):
        #~ if self.duration_value is None or not self.duration_unit:
            #~ return
        #~ if self.start_time:
            #~ dt = self.get_datetime('start')
            #~ end_time = self.duration_unit.add_duration(dt,self.duration_value)
            #~ # end_time = add_duration(dt,self.duration_value,self.duration_unit)
            #~ setkw(self,**dt2kw(end_time,'end'))
        #~ elif self.end_time:
            #~ dt = self.get_datetime('end')
            #~ end_time = self.duration_unit.add_duration(dt,-self.duration_value)
            #~ setkw(self,**dt2kw(end_time,'start'))
        
    #~ def duration_value_changed(self,oldvalue): self.compute_times()
    #~ def duration_unit_changed(self,oldvalue): self.compute_times()
    #~ def start_date_changed(self,oldvalue): self.compute_times()
    #~ def start_time_changed(self,oldvalue): self.compute_times()
    #~ def end_date_changed(self,oldvalue): self.compute_times()
    #~ def end_time_changed(self,oldvalue): self.compute_times()
        
    def save(self,*args,**kw):
        #~ if not self.state and self.start_date and self.start_date < datetime.date.today():
            #~ self.state = EventState.obsolete
        super(Event,self).save(*args,**kw)
        if self.calendar.invite_team_members:
            if True or self.access_class == AccessClasses.public:
                if not self.state in (EventState.blank_item, EventState.draft):
                    if self.guest_set.all().count() == 0:
                        #~ print 20120711
                        for obj in Membership.objects.filter(user=self.user):
                            if obj.watched_user.partner:
                                Guest(event=self,partner=obj.watched_user.partner).save()
        
    def after_state_change(self,ar,kw,old,new):
        """
        Tell the user that they should now inform the guests.
        """
        super(Event,self).after_state_change(ar,kw,old,new)
        if new.name in ('suggested','cancelled','scheduled','rescheduled'):
            if self.guest_set.all().count() > 0:
                kw.update(alert=True,message=_("You should now inform the guests about this state change."))
                
    def after_send_mail(self,mail,ar,kw):
        if self.state.name == 'suggested':
            self.state = EventState.notified
            kw['message'] += '\n('  +_("Event %s has been marked *notified*.") % self + ')'
            self.save()
        #~ else:
            #~ kw['message'] += '\n(' + _("Event remains *%s*.") % self.state + ')'
                
            
    def on_user_change(self,request):
        if not self.state:
            self.state = EventState.draft
        #~ self.user_modified = True
        
    def on_create(self,ar):
        self.start_date = datetime.date.today()
        self.start_time = datetime.datetime.now().time()
        super(Event,self).on_create(ar)
        
        
    def get_postable_recipients(self):
        """return or yield a list of Partners"""
        if issubclass(settings.LINO.project_model,contacts.Partner):
            if self.project:
                yield self.project
        for g in self.guest_set.all():
            yield g.partner
        #~ if self.user.partner:
            #~ yield self.user.partner
        
    def get_mailable_type(self):  
        return self.calendar
        
    def get_mailable_recipients(self):
        if issubclass(settings.LINO.project_model,contacts.Partner):
            if self.project:
                yield ('to',self.project)
        for g in self.guest_set.all():
            yield ('to',g.partner)
        if self.user.partner:
            yield ('cc',self.user.partner)
            
    #~ def get_mailable_body(self,ar):
        #~ return self.description
        
            
    def allow_state_suggest(self,user):
        if not self.start_time: return False
        return True
      
    #~ def allow_state_scheduled(self,user):
        #~ if not self.start_time: return False
        #~ return True
      
    #~ @classmethod
    #~ def setup_report(cls,rpt):
        #~ mixins.TypedPrintable.setup_report(rpt)
        #~ outbox.Mailable.setup_report(rpt)
        
    @dd.displayfield(_("Link URL"))
    def url(self,request): return 'foo'
    #~ url.return_type = dd.DisplayField(_("Link URL"))
    
    #~ @dd.virtualfield(models.BooleanField(_("all day")))
    #~ def all_day(self,request): 
        #~ return not self.start_time
    
    @dd.virtualfield(dd.DisplayField(_("Reminder")))
    def reminder(self,request): return False
    #~ reminder.return_type = dd.DisplayField(_("Reminder"))

    def get_print_language(self,bm):
        if settings.LINO.project_model is not None and self.project:
            return self.project.get_print_language(bm)
        return self.user.language
        
    #~ @dd.action(EventState.scheduled.text,sort_index=10,required=dict(states=['','draft']))
    #~ def mark_scheduled(self,ar):
        #~ if not self.start_time:
            #~ return ar.error_response(
                #~ _("Cannot mark scheduled with empty start time."),
                #~ alert=True)
        #~ self.state = EventState.scheduled
        #~ self.save()
        #~ return ar.ui.success_response(refresh=True)
    
    #~ @dd.action(EventState.notified.text,sort_index=11,required=dict(states=['scheduled']))
    #~ def mark_notified(self,ar):
        #~ """
        #~ Running this action means 
        #~ "This event has somehow (no matter how) been notified to the guests."
        #~ """
        #~ self.state = EventState.notified
        #~ self.save()
        #~ return ar.ui.success_response(refresh=True)
    
    #~ @dd.action(EventState.confirmed.text,sort_index=12,
        #~ required=dict(states=['scheduled','notified']))
    #~ def mark_confirmed(self,ar):
        #~ self.state = EventState.confirmed
        #~ self.save()
        #~ return ar.ui.success_response(refresh=True)
        
    #~ @dd.action(EventState.took_place.text,sort_index=13,
        #~ required=dict(states=['scheduled','notified','confirmed']))
    #~ def mark_took_place(self,ar):
        #~ self.state = EventState.took_place
        #~ self.save()
        #~ return ar.ui.success_response(refresh=True)
        
    #~ @dd.action(EventState.cancelled.text,sort_index=13,
        #~ required=dict(states=['scheduled','notified','confirmed']))
    #~ def mark_cancelled(self,ar):
        #~ self.state = EventState.cancelled
        #~ self.save()
        #~ return ar.ui.success_response(refresh=True)
        
    #~ @dd.action(_("Absent"),sort_index=13,
        #~ required=dict(states=['scheduled','notified','confirmed']))
    #~ def mark_present(self,ar):
        #~ self.state = EventState.absent
        #~ self.save()
        #~ return ar.ui.success_response(refresh=True)
        
    #~ def get_row_permission(self,user,state,action):
        #~ """
        #~ """
        #~ if isinstance(action,postings.CreatePostings):
            #~ if self.state < EventState.scheduled:
                #~ return False
        #~ return super(Event,self).get_row_permission(user,state,action)
        
    @classmethod
    def site_setup(cls,lino):
        cls.DISABLED_AUTO_FIELDS = dd.fields_list(cls,
            '''summary''')
            
    #~ @classmethod
    #~ def setup_table(cls,t):
        #~ """
        #~ See also :meth:`lino.core.table.Table.setup_table`
        #~ """
        #~ t.create_postings.set_required(states=['scheduled'])
        #~ t.create_mail.set_required(states=['scheduled'])
  


    
class EventDetailLayout(dd.FormLayout):
    start = "start_date start_time"
    end = "end_date end_time"
    main = """
    calendar summary user 
    start end #all_day #duration state
    place priority access_class transparent #rset 
    owner created:20 modified:20  
    description
    GuestsByEvent outbox.MailsByController
    """

class EventInsertLayout(EventDetailLayout):
    main = """
    type summary 
    start end 
    place priority access_class transparent 
    """
    
class Events(dd.Table):
    model = 'cal.Event'
    required = dict(user_groups='office',user_level='manager')
    column_names = 'start_date start_time user summary calendar state *'
    #~ active_fields = ['all_day']
    order_by = ["start_date","start_time"]
    
    detail_layout = EventDetailLayout()
    insert_layout = EventInsertLayout()
    

        
    
    
class EventsByCalendar(Events):
    master_key = 'calendar'
    
#~ class EventsByType(Events):
    #~ master_key = 'type'
    
class EventsByPartner(Events):
    required = dict(user_groups='office')
    master_key = 'user'
    
class EventsByPlace(Events):
    """
    Displays the :class:`Events <Event>` at a given :class:`Place`.
    """
    master_key = 'place'

class EventsByController(Events):
    required = dict(user_groups='office')
    master_key = 'owner'
    column_names = 'start_date start_time summary state *'

if settings.LINO.project_model:    
  
    class EventsByProject(Events):
        required = dict(user_groups='office')
        master_key = 'project'
    
if settings.LINO.user_model:    
  
    class MyEvents(Events,mixins.ByUser):
        required = dict(user_groups='office')
        help_text = _("Table of all my calendar events.")
        column_names = 'start_date start_time calendar project summary state workflow_buttons *'
        #~ model = 'cal.Event'
        #~ label = _("My Events")
        #~ column_names = 'start_date start_time summary state *'
        
    class EventsSuggested(Events):
        """
        """
        help_text = _("Table of all suggested events.")
        label = _("Suggested Events")
        required = dict(user_groups='office',user_level='manager')
        column_names = 'start_date start_time user project summary workflow_buttons *'
        known_values = dict(state=EventState.suggested)
        
    class MyEventsSuggested(EventsSuggested,MyEvents):
        help_text = _("Table of my suggested events (to become notified).")
        required = dict(user_groups='office')
        column_names = 'start_date start_time project summary workflow_buttons *'
        label = _("My suggested Events")
        
    class EventsNotified(Events):
        """
        """
        help_text = _("Table of all notified events (waiting to become scheduled).")
        label = _("Notified Events")
        required = dict(user_groups='office',user_level='manager')
        column_names = 'start_date start_time user project summary workflow_buttons *'
        known_values = dict(state=EventState.notified)
        
    class MyEventsNotified(EventsNotified,MyEvents):
        help_text = _("Table of my notified events (waiting to become scheduled).")
        required = dict(user_groups='office')
        column_names = 'start_date start_time project summary workflow_buttons *'
        label = _("My notified Events")
        
    #~ class EventsToNotify(Events):
        #~ """
        #~ A list of events that need to be notified (i.e. communicated to the guests). 
        #~ Clicking on :attr:`Event.mark_notified` 
        #~ will remove this Event from this 
        #~ table and make it appear 
        #~ in :class:`MyEventsToConfirm`.
        #~ or :class:`MyEventsConfirmed`.
        #~ """
        #~ help_text = _("Table of all events that need to be communicated to guests.")
        #~ required = dict(user_level='manager',user_groups='office')
        #~ column_names = 'start_date start_time user project summary workflow_buttons *'
        #~ label = _("Events to notify")
        #~ order_by = ["start_date","start_time"]
        #~ filter = models.Q(state=EventState.scheduled)
        
    #~ class MyEventsToNotify(EventsToNotify,MyEvents):
        #~ help_text = _("Table of all my events that need to be communicated to guests.")
        #~ required = dict(user_groups='office')
        #~ column_names = 'start_date start_time project summary workflow_buttons *'
        #~ label = _("My events to notify")
        
    #~ class EventsToSchedule(Events):
        #~ """
        #~ A list of events that aren't yet scheduled. 
        #~ The user is supposed to fill at least a start_date and start_time.
        #~ Clicking on "mark scheduled" 
        #~ means "I made up my mind on when this event should happen"
        #~ and will remove this Event from this 
        #~ table and make it appear in 
        #~ :class:`EventsToNotify` and 
        #~ :class:`MyEventsToNotify`.
        #~ """
        #~ help_text = _("Table of all events that need to be scheduled.")
        #~ label = _("Events to schedule")
        #~ required = dict(user_groups='office',user_level='manager')
        #~ column_names = 'start_date start_time user project summary workflow_buttons *'
        #~ filter = models.Q(state__in=(EventState.blank_item,EventState.draft))
        
    #~ class MyEventsToSchedule(EventsToSchedule,MyEvents):
        #~ help_text = _("Table of all my events that need to be scheduled.")
        #~ required = dict(user_groups='office')
        #~ column_names = 'start_date start_time project summary workflow_buttons *'
        #~ label = _("My events to schedule")
        
    #~ class EventsToConfirm(MyEvents):
        #~ """
        #~ A list of events that need to be confirmed
        #~ (i.e. the user made sure that the guests received 
        #~ their notification and plan to attend to the event). 
        #~ """
        #~ help_text = _("Table of all events that are waiting for confirmation from guests.")
        #~ required = dict(user_level='manager',user_groups='office')
        #~ column_names = 'start_date start_time project user summary workflow_buttons *'
        #~ label = _("Events to confirm")
        #~ order_by = ["start_date","start_time"]
        #~ filter = models.Q(state=EventState.scheduled)
        
    #~ class MyEventsToConfirm(EventsToConfirm):
        #~ help_text = _("Table of all my events that are waiting for confirmation from guests.")
        #~ required = dict(user_groups='office')
        #~ label = _("My events to confirm")
        #~ column_names = 'start_date start_time project summary workflow_buttons *'
        
    class MyEventsToday(MyEvents):
        required = dict(user_groups='office')
        help_text = _("Table of my events per day.")
        column_names = 'start_time summary state workflow_buttons *'
        label = _("My events today")
        order_by = ['start_time']
        
        parameters = dict(
          date = models.DateField(_("Date"),
          blank=True,default=datetime.date.today),
        )
        @classmethod
        def get_request_queryset(self,ar):
            qs = super(MyEventsToday,self).get_request_queryset(ar)
            #~ if ar.param_values.date:
            return qs.filter(start_date=ar.param_values.date)
            #~ return qs
            
        @classmethod
        def create_instance(self,ar,**kw):
            kw.update(start_date=ar.param_values.date)
            return super(MyEventsToday,self).create_instance(ar,**kw)

        #~ @classmethod
        #~ def setup_request(self,rr):
            #~ rr.known_values = dict(start_date=datetime.date.today())
            #~ super(MyEventsToday,self).setup_request(rr)
            

#~ class Task(Component,contacts.PartnerDocument):
class Task(Component):
    """
    A Task is when a user plans to to something 
    (and optionally wants to get reminded about it).
    """
    #~ workflow_state_field = 'state'
    
    class Meta:
        verbose_name = _("Task")
        verbose_name_plural = _("Tasks")
        #~ abstract = True
        
    due_date = models.DateField(
        blank=True,null=True,
        verbose_name=_("Due date"))
    due_time = models.TimeField(
        blank=True,null=True,
        verbose_name=_("Due time"))
    #~ done = models.BooleanField(_("Done"),default=False) # iCal:COMPLETED
    percent = models.IntegerField(_("Duration value"),null=True,blank=True) # iCal:PERCENT
    state = TaskState.field(blank=True) # iCal:STATUS
    #~ status = models.ForeignKey(TaskStatus,verbose_name=_("Status"),blank=True,null=True) # iCal:STATUS
    
    #~ @dd.action(_("Done"),required=dict(states=['','todo','started']))
    #~ @dd.action(TaskState.todo.text,required=dict(states=['']))
    #~ def mark_todo(self,ar):
        #~ self.state = TaskState.todo
        #~ self.save()
        #~ return ar.success_response(refresh=True)
    
    #~ @dd.action(TaskState.done.text,required=dict(states=['','todo','started']))
    #~ def mark_done(self,ar):
        #~ self.state = TaskState.done
        #~ self.save()
        #~ return ar.success_response(refresh=True)
    
    #~ @dd.action(TaskState.started.text,required=dict(states=['','todo']))
    #~ def mark_started(self,ar):
        #~ self.state = TaskState.started
        #~ self.save()
        #~ return ar.success_response(refresh=True)
    
    #~ @dd.action(TaskState.sleeping.text,required=dict(states=['','todo']))
    #~ def mark_sleeping(self,ar):
        #~ self.state = TaskState.sleeping
        #~ self.save()
        #~ return ar.success_response(refresh=True)
    

    def on_user_change(self,request):
        if not self.state:
            self.state = TaskState.todo
        #~ self.user_modified = True
        
    @classmethod
    def site_setup(cls,lino):
        #~ lino.TASK_AUTO_FIELDS = dd.fields_list(cls,
        cls.DISABLED_AUTO_FIELDS = dd.fields_list(cls,
            '''start_date start_time summary''')

    #~ def __unicode__(self):
        #~ return "#" + str(self.pk)
        

class Tasks(dd.Table):
    debug_permissions = True
    model = 'cal.Task'
    required = dict(user_groups='office')
    column_names = 'start_date summary state *'
    #~ hidden_columns = set('owner_id owner_type'.split())
    
    #~ detail_template = """
    #~ start_date status due_date user  
    #~ summary 
    #~ created:20 modified:20 owner #owner_type #owner_id
    #~ description #notes.NotesByTask    
    #~ """
    detail_template = """
    start_date due_date id state workflow_buttons 
    summary 
    user project 
    calendar owner created:20 modified:20   
    description #notes.NotesByTask    
    """
    insert_layout = dd.FormLayout("""
    summary
    user project
    """,window_size=(50,'auto'))
    
class TasksByController(Tasks):
    master_key = 'owner'
    #~ hidden_columns = set('owner_id owner_type'.split())

if settings.LINO.user_model:    
        
    class MyTasks(Tasks,mixins.ByUser):
        help_text = _("Table of all my tasks.")
        order_by = ["start_date","start_time"]
        column_names = 'start_date summary state workflow_buttons *'
    
    class MyTasksToDo(MyTasks):
        help_text = _("Table of my tasks marked 'to do'.")
        column_names = 'start_date summary state workflow_buttons *'
        label = _("To-do list")
        #~ filter = models.Q(state__in=(TaskState.blank_item,TaskState.todo,TaskState.started))
        filter = models.Q(state__in=(TaskState.todo,TaskState.started))
    
if settings.LINO.project_model:    
  
    class TasksByProject(Tasks):
        master_key = 'project'
        column_names = 'start_date user summary state workflow_buttons *'
    

class GuestRole(mixins.PrintableType,outbox.MailableType,babel.BabelNamed):
    """
    A possible value for the `role` field of an :class:`Guest`.
    """
    
    templates_group = 'cal/Guest'
    
    class Meta:
        verbose_name = _("Guest Role")
        verbose_name_plural = _("Guest Roles")


class GuestRoles(dd.Table):
    """
    Table showing all :class:`GuestRole` objects.
    """
    model = GuestRole
    required = dict(user_groups='office')
    detail_template = """
    id name
    build_method template email_template attach_to_email
    cal.GuestsByRole
    """
    

class Guest(mixins.TypedPrintable,outbox.Mailable):
    """
    A Guest is a Partner who is invited to an :class:`Event`.
    """
    
    workflow_state_field = 'state'
    
    class Meta:
        verbose_name = _("Guest")
        verbose_name_plural = _("Guests")
        
        
    event = models.ForeignKey('cal.Event',
        verbose_name=_("Event")) 
        
    partner = models.ForeignKey(contacts.Partner)
        #~ related_name="%(app_label)s_%(class)s_by_contact",
        # related_name="%(app_label)s_%(class)s_related",
        # verbose_name=_("Partner")
        #~ )
    #~ language = babel.LanguageField(default=babel.DEFAULT_LANGUAGE)

    role = models.ForeignKey('cal.GuestRole',
        verbose_name=_("Role"),
        blank=True,null=True) 
        
    state = GuestState.field(blank=True)
    #~ status = models.ForeignKey(GuestStatus,verbose_name=_("Status"),blank=True,null=True)
    
    #~ confirmed = models.DateField(
        #~ blank=True,null=True,
        #~ verbose_name=_("Confirmed"))

    remark = models.CharField(
        _("Remark"),max_length=200,blank=True)
        
    def get_user(self):
        # used to apply `owner` requirement in GuestState
        return self.event.user
    user = property(get_user)

    #~ def __unicode__(self):
        #~ return self._meta.verbose_name + " #" + str(self.pk)
        
    def __unicode__(self):
        return u'%s #%s ("%s")' % (self._meta.verbose_name,self.pk,self.event)

    def get_printable_type(self):
        return self.role
        
    def get_mailable_type(self):  
        return self.role
        

    def get_mailable_recipients(self):
        yield ('to',self.partner)
        
    @dd.displayfield(_("Event"))
    def event_summary(self,ar):
        return ar.renderer.href_to(
            self.event,event_summary(self.event,ar.get_user()))
        #~ return event_summary(self.event,ar.get_user())
        
        

    #~ def get_recipient(self):
        #~ return self.partner
    #~ recipient = property(get_recipient)
        
    #~ @classmethod
    #~ def setup_report(cls,rpt):
        #~ mixins.CachedPrintable.setup_report(rpt)
        #~ outbox.Mailable.setup_report(rpt)
        
    #~ @dd.action(_("Invite"),required=dict(states=['']))
    #~ def invite(self,ar):
        #~ self.state = GuestState.invited
        
    #~ @dd.action(_("Confirm"),required=dict(states=['invited']))
    #~ def confirm(self,ar):
        #~ self.state = GuestState.confirmed
    
#~ class Guests(dd.Table,workflows.Workflowable):
class Guests(dd.Table):
    model = Guest
    required = dict(user_groups='office')
    column_names = 'partner role state workflow_buttons remark event *'
    #~ workflow_state_field = 'state'
    #~ column_names = 'contact role state remark event *'
    #~ workflow_actions = ['invite','notify']
    #~ workflow_owner_field = 'event__user'
    
    #~ def setup_actions(self):
        #~ super(dd.Table,self).setup_actions()
        #~ self.add_action(mails.CreateMailAction())
        
class GuestsByEvent(Guests):
    master_key = 'event'

class GuestsByRole(Guests):
    master_key = 'role'

class GuestsByPartner(Guests):
    master_key = 'partner'
    column_names = 'event role state workflow_buttons remark *'

class MyInvitations(GuestsByPartner):
    order_by = ['event__start_date','event__start_time']
    label = _("My received invitations")
    help_text = _("""Shows all my received invitations, independently of their state.""")
    column_names = 'event__start_date event__start_time event_summary role state workflow_buttons remark *'
    
    @classmethod
    def get_request_queryset(self,ar):
        ar.master_instance = ar.get_user().partner
        return super(MyInvitations,self).get_request_queryset(ar)
        
    
class MyPendingInvitations(MyInvitations):
    help_text = _("""Shows received invitations which I must accept or reject.""")
    label = _("My pending received invitations")
    filter = models.Q(state=GuestState.invited)
    
#~ class MySentInvitations(Guests):
    #~ help_text = _("""Shows invitations which I sent accept or reject.""")
  
    #~ label = _("My Sent Invitations")
    
    #~ order_by = ['event__start_date','event__start_time']
    #~ column_names = 'event__start_date event__start_time event_summary role state workflow_buttons remark *'
    
    #~ @classmethod
    #~ def get_request_queryset(self,ar):
        #~ datelimit = datetime.date.today() + dateutil.relativedelta.relativedelta(days=-7)
        #~ ar.filter = models.Q(event__user=ar.get_user(),event__start_date__gte=datelimit)
        #~ return super(MySentInvitations,self).get_request_queryset(ar)
    
#~ class MyPendingSentInvitations(MySentInvitations):
    #~ help_text = _("""Shows invitations which I sent, and for which I accept or reject.""")
    #~ label = _("My Pending Sent Invitations")
    #~ @classmethod
    #~ def get_request_queryset(self,ar):
        #~ ar.filter = models.Q(state=GuestState.invited,event__user=ar.get_user())
        #~ # ! note that we skip one mro parent:
        #~ return super(MySentInvitations,self).get_request_queryset(ar)
    

    
def tasks_summary(ui,user,days_back=None,days_forward=None,**kw):
    """
    Return a HTML summary of all open reminders for this user.
    May be called from :xfile:`welcome.html`.
    """
    Task = resolve_model('cal.Task')
    Event = resolve_model('cal.Event')
    today = datetime.date.today()
    
    past = {}
    future = {}
    def add(cmp):
        if cmp.start_date < today:
        #~ if task.dt_alarm < today:
            lookup = past
        else:
            lookup = future
        day = lookup.get(cmp.start_date,None)
        if day is None:
            day = [cmp]
            lookup[cmp.start_date] = day
        else:
            day.append(cmp)
            
    #~ filterkw = { 'due_date__lte' : today }
    filterkw = {}
    if days_back is not None:
        filterkw.update({ 
            'start_date__gte' : today - datetime.timedelta(days=days_back)
            #~ 'dt_alarm__gte' : today - datetime.timedelta(days=days_back)
        })
    if days_forward is not None:
        filterkw.update({ 
            'start_date__lte' : today + datetime.timedelta(days=days_forward)
            #~ 'dt_alarm__lte' : today + datetime.timedelta(days=days_forward)
        })
    #~ filterkw.update(dt_alarm__isnull=False)
    filterkw.update(user=user)
    
    for o in Event.objects.filter(
        #~ models.Q(status=None) | models.Q(status__reminder=True),
        models.Q(state=None) | models.Q(state__lte=EventState.scheduled),
        **filterkw).order_by('start_date'):
        add(o)
        
    #~ filterkw.update(done=False)
    filterkw.update(state__in=[TaskState.blank_item,TaskState.todo])
            
    for task in Task.objects.filter(**filterkw).order_by('start_date'):
        add(task)
        
    def loop(lookup,reverse):
        sorted_days = lookup.keys()
        sorted_days.sort()
        if reverse: 
            sorted_days.reverse()
        for day in sorted_days:
            yield '<h3>'+dtosl(day) + '</h3>'
            yield dd.summary(ui,lookup[day],**kw)
            
    #~ cells = ['Ausblick'+':<br>',cgi.escape(u'Rückblick')+':<br>']
    cells = [
      cgi.escape(_('Upcoming reminders')) + ':<br>',
      cgi.escape(_('Past reminders')) + ':<br>'
    ]
    for s in loop(future,False):
        cells[0] += s
    for s in loop(past,True):
        cells[1] += s
    s = ''.join(['<td valign="top" bgcolor="#eeeeee" width="30%%">%s</td>' % s for s in cells])
    s = '<table cellspacing="3px" bgcolor="#ffffff"><tr>%s</tr></table>' % s
    s = '<div class="htmlText">%s</div>' % s
    return s


def update_auto_event(autotype,user,date,summary,owner,**defaults):
    #~ model = resolve_model('cal.Event')
    return update_auto_component(Event,autotype,user,date,summary,owner,**defaults)
  
def update_auto_task(autotype,user,date,summary,owner,**defaults):
    #~ model = resolve_model('cal.Task')
    return update_auto_component(Task,autotype,user,date,summary,owner,**defaults)
    
def update_auto_component(model,autotype,user,date,summary,owner,**defaults):
    """
    Creates, updates or deletes the 
    automatic :class:`calendar component <Component>`
    of the specified `type` and `owner`.
    
    Specifying `None` for `date` means that 
    the automatic component should be deleted.
    """
    #~ print "20111014 update_auto_task"
    #~ if SKIP_AUTO_TASKS: return 
    if settings.LINO.loading_from_dump: 
        #~ print "20111014 loading_from_dump"
        return None
    ot = ContentType.objects.get_for_model(owner.__class__)
    if date and date >= datetime.date.today() + datetime.timedelta(days=-7):
        #~ defaults = owner.get_auto_task_defaults(**defaults)
        defaults.setdefault('user',user)
        obj,created = model.objects.get_or_create(
          defaults=defaults,
          owner_id=owner.pk,
          owner_type=ot,
          auto_type=autotype)
        if not obj.is_user_modified():
            original_state = dict(obj.__dict__)
            if obj.user != user:
                obj.user = user
            summary = force_unicode(summary)
            if obj.summary != summary:
                obj.summary = summary
            if obj.start_date != date:
                obj.start_date = date
            if created or obj.__dict__ != original_state:
                obj.save()
        return obj
    else:
        # delete task if it exists
        try:
            obj = model.objects.get(owner_id=owner.pk,
                    owner_type=ot,auto_type=autotype)
        except model.DoesNotExist:
            pass
        else:
            if not obj.is_user_modified():
                obj.delete()
                
        
def update_reminder(type,owner,user,orig,msg,num,unit):
    """
    Shortcut for calling :func:`update_auto_task` 
    for automatic "reminder tasks".
    A reminder task is a message about something that will 
    happen in the future.
    """
    update_auto_task(
      type,user,
      unit.add_duration(orig,-num),
      msg,
      owner)
            



def migrate_reminder(obj,reminder_date,reminder_text,
                         delay_value,delay_type,reminder_done):
    """
    This was used only for migrating to 1.2.0, 
    see :mod:`lino.apps.pcsw.migrate`.
    """
    raise NotImplementedError("No longer needed (and no longer supported after 20111026).")
    def delay2alarm(delay_type):
        if delay_type == 'D': return DurationUnit.days
        if delay_type == 'W': return DurationUnit.weeks
        if delay_type == 'M': return DurationUnit.months
        if delay_type == 'Y': return DurationUnit.years
      
    #~ # These constants must be unique for the whole Lino Site.
    #~ # Keep in sync with auto types defined in lino.apps.pcsw.models.Person
    #~ REMINDER = 5
    
    if reminder_text:
        summary = reminder_text
    else:
        summary = _('due date reached')
    
    update_auto_task(
      None, # REMINDER,
      obj.user,
      reminder_date,
      summary,obj,
      done = reminder_done,
      alarm_value = delay_value,
      alarm_unit = delay2alarm(delay_type))
      

class ExtDateTimeField(dd.VirtualField):
    """
    An editable virtual field needed for 
    communication with the Ext.ensible CalendarPanel
    because Lino uses two separate fields 
    `start_date` and `start_time`
    or `end_date` and `end_time` while CalendarPanel expects 
    and sends single DateTime values.
    """
    editable = True
    def __init__(self,name_prefix,alt_prefix,label):
        self.name_prefix = name_prefix
        self.alt_prefix = alt_prefix
        rt = models.DateTimeField(label)
        dd.VirtualField.__init__(self,rt,None)
    
    def set_value_in_object(self,request,obj,value):
        obj.set_datetime(self.name_prefix,value)
        
    def value_from_object(self,obj,ar):
        #~ logger.info("20120118 value_from_object() %s",obj2str(obj))
        return obj.get_datetime(self.name_prefix,self.alt_prefix)

class ExtSummaryField(dd.VirtualField):
    """
    An editable virtual field needed for 
    communication with the Ext.ensible CalendarPanel
    because we want a customized "virtual summary" 
    that includes the project name.
    """
    editable = True
    def __init__(self,label):
        rt = models.CharField(label)
        dd.VirtualField.__init__(self,rt,None)
        
    def set_value_in_object(self,request,obj,value):
        if obj.project:
            s = unicode(obj.project)
            if value.startswith(s):
                value = value[len(s):]
        obj.summary = value
        
    def value_from_object(self,obj,ar):
        #~ logger.info("20120118 value_from_object() %s",obj2str(obj))
        return event_summary(obj,ar.get_user())


def event_summary(obj,user):
    s = obj.summary
    if obj.user != user:
        if obj.access_class == AccessClasses.show_busy:
            s = _("Busy")
        s = obj.user.username + ': ' + unicode(s)
    elif settings.LINO.project_model is not None and obj.project is not None:
        s += " " + unicode(_("with")) + " " + unicode(obj.project)
    if obj.state:
        s = ("(%s) " % unicode(obj.state)) + s
    n = obj.guest_set.all().count()
    if n:
        s = ("[%d] " % n) + s
    return s

def user_calendars(qs,user):
    #~ Q = models.Q
    subs = Subscription.objects.filter(user=user).values_list('calendar__id',flat=True)
    #~ print 20120710, subs
    return qs.filter(id__in=subs)

if settings.LINO.use_extensible:
  
    def parsedate(s):
        return datetime.date(*settings.LINO.parse_date(s))
  
    class Panel(dd.Frame):
        required = dict(user_groups='office')
        default_action = dd.Calendar()
        #~ default_action_class = dd.Calendar

    class PanelCalendars(Calendars):
        use_as_default_table = False
        required = dict(user_groups='office')
        column_names = 'id name description color is_hidden'
        
        @classmethod
        def get_request_queryset(self,ar):
            qs = super(PanelCalendars,self).get_request_queryset(ar)
            return user_calendars(qs,ar.get_user())
            
        @dd.virtualfield(models.BooleanField(_('Hidden')))
        def is_hidden(cls,self,ar):
            return False
            #~ if self.user == ar.get_user():
                #~ return False
            #~ sub = Subscription.objects.get(user=ar.get_user(),calendar=self)
            #~ return sub.is_hidden

            
    class PanelEvents(Events):
        """
        The table used for Ext.ensible CalendarPanel.
        """
        required = dict(user_groups='office')
        use_as_default_table = False
        #~ parameters = dict(team_view=models.BooleanField(_("Team View")))
        
        column_names = 'id start_dt end_dt summary description user place calendar #rset url all_day reminder'
        
        start_dt = ExtDateTimeField('start',None,_("Start"))
        end_dt = ExtDateTimeField('end','start',_("End"))
        
        summary = ExtSummaryField(_("Summary"))
        #~ overrides the database field of same name
        
      
        @classmethod
        def parse_req(self,request,rqdata,**kw):
            #~ logger.info('20120710 %s', request.GET[requests.URL_PARAM_TEAM_VIEW])
          
            #~ filter = kw.get('filter',{})
            assert not kw.has_key('filter')
            fkw = {}
            #~ logger.info("20120118 filter is %r", filter)
            endDate = rqdata.get('ed',None)
            if endDate:
                d = parsedate(endDate)
                fkw.update(start_date__lte=d)
            startDate = rqdata.get('sd',None)
            if startDate:
                d = parsedate(startDate)
                #~ logger.info("startDate is %r", d)
                fkw.update(start_date__gte=d)
            #~ logger.info("20120118 filter is %r", filter)
            
            #~ subs = Subscription.objects.filter(user=request.user).values_list('calendar__id',flat=True)
            #~ filter.update(calendar__id__in=subs)
            
            filter = models.Q(**fkw)
            
            # who am i ?
            me = request.subst_user or request.user
            
            # show al my events
            for_me = models.Q(user=me)
            
            # also show events to which i am invited
            if me.partner:
                #~ me_as_guest = Guest.objects.filter(partner=request.user.partner)
                #~ for_me = for_me | models.Q(guest_set__count__gt=0)
                #~ for_me = for_me | models.Q(guest_count__gt=0)
                for_me = for_me | models.Q(guest__partner=me.partner)
            
            # in team view, show also events of all my team members
            tv = rqdata.get(ext_requests.URL_PARAM_TEAM_VIEW,False)
            if tv and ext_requests.parse_boolean(tv):
                # positive list of ACLs for events of team members
                team_classes = (AccessClasses.blank_item,AccessClasses.public,AccessClasses.show_busy)
                #~ logger.info('20120710 %r', tv)
                team_ids = Membership.objects.filter(user=me).values_list('watched_user__id',flat=True)
                #~ team.append(request.user.id)
                for_me = for_me | models.Q(user__id__in=team_ids,access_class__in=team_classes)
                #~ kw.update(exclude = models.Q(user__id__in=team))
            filter = filter & for_me
            #~ logger.info('20120710 %s', filter)
            kw.update(filter=filter)
            return kw
            
        #~ @classmethod
        #~ def get_request_queryset(self,ar):
            #~ qs = super(PanelEvents,self).get_request_queryset(ar)
            #~ return qs
            
            

from lino.utils.babel import dtosl
    
def reminders(ar,days_back=None,days_forward=None,**kw):
    """
    Return a HTML summary of all open reminders for this user.
    
    """
    user = ar.get_user()
    Task = resolve_model('cal.Task')
    Event = resolve_model('cal.Event')
    today = datetime.date.today()
    
    past = {}
    future = {}
    def add(cmp):
        if cmp.start_date < today:
        #~ if task.dt_alarm < today:
            lookup = past
        else:
            lookup = future
        day = lookup.get(cmp.start_date,None)
        if day is None:
            day = [cmp]
            lookup[cmp.start_date] = day
        else:
            day.append(cmp)
            
    #~ filterkw = { 'due_date__lte' : today }
    filterkw = {}
    if days_back is not None:
        filterkw.update({ 
            'start_date__gte' : today - datetime.timedelta(days=days_back)
            #~ 'dt_alarm__gte' : today - datetime.timedelta(days=days_back)
        })
    if days_forward is not None:
        filterkw.update({ 
            'start_date__lte' : today + datetime.timedelta(days=days_forward)
            #~ 'dt_alarm__lte' : today + datetime.timedelta(days=days_forward)
        })
    #~ filterkw.update(dt_alarm__isnull=False)
    filterkw.update(user=user)
    
    for o in Event.objects.filter(
        #~ models.Q(status=None) | models.Q(status__reminder=True),
        models.Q(state=None) | models.Q(state__lte=EventState.scheduled),
        **filterkw).order_by('start_date'):
        add(o)
        
    #~ filterkw.update(done=False)
    filterkw.update(state__in=[TaskState.blank_item,TaskState.todo])
            
    for task in Task.objects.filter(**filterkw).order_by('start_date'):
        add(task)
        
    def loop(lookup,reverse):
        sorted_days = lookup.keys()
        sorted_days.sort()
        if reverse: 
            sorted_days.reverse()
        for day in sorted_days:
            yield '<h3>'+dtosl(day) + '</h3>'
            yield dd.summary(ar,lookup[day],**kw)
            
    if days_back is not None:
        s = ''.join([chunk for chunk in loop(past,True)])
    else:
        s = ''.join([chunk for chunk in loop(future,False)])
        
    #~ s = '<div class="htmlText" width="30%%">%s</div>' % s
    s = '<div class="htmlText" style="margin:5px">%s</div>' % s
    return s
    
    
def update_reminders(user):
    n = 0 
    for obj in settings.LINO.get_reminder_generators_by_user(user):
        obj.update_reminders()
        #~ logger.info("--> %s",unicode(obj))
        n += 1
    return n
      

class UpdateReminders(actions.RowAction):
    """
    Users can invoke this to re-generate their automatic tasks.
    """
    url_action_name = 'UpdateReminders'
    label = _('Update Reminders')
    
    callable_from = (actions.GridEdit, actions.ShowDetailAction)
        
    def run(self,user,ar,**kw):
        logger.info("Updating reminders for %s",user)
        n = update_reminders(user)
        kw.update(success=True)
        msg = _("%(num)d reminders for %(user)s have been updated."
          ) % dict(user=user,num=n)
        kw.update(message=msg)
        logger.info(msg)
        return ar.ui.success_response(**kw)
        
class RemindersByUser(dd.Table):
    """
    Shows the list of automatically generated tasks for this user.
    """
    model = Task
    label = _("Reminders")
    master_key = 'user'
    column_names = "start_date summary *"
    order_by = ["start_date"]
    filter = Q(auto_type__isnull=False)
    

from lino import models as lino

class Home(lino.Home):
  
    #~ debug_permissions = True 

    label = lino.Home.label
    app_label = 'lino'
    detail_template = """
    quick_links:80x1
    coming_reminders:40x16 missed_reminders:40x16
    """
    
    @dd.virtualfield(dd.HtmlBox(_('Missed reminders')))
    def missed_reminders(cls,self,ar):
        return reminders(ar,days_back=90,
          max_items=10,before='<ul><li>',separator='</li><li>',after="</li></ul>")

    @dd.virtualfield(dd.HtmlBox(_('Upcoming reminders')))
    def coming_reminders(cls,self,ar):
        return reminders(ar,days_forward=30,
            max_items=10,before='<ul><li>',separator='</li><li>',after="</li></ul>")


#~ class MissedReminders(dd.Frame):
    #~ label = _('Missed reminders')
    
    #~ @classmethod
    #~ def value(cls,ar):
        #~ return reminders(ar.ui,ar.get_user(),days_back=90,
          #~ max_items=10,before='<ul><li>',separator='</li><li>',after="</li></ul>")
          
#~ class ComingReminders(dd.Frame):
    #~ label = _('Coming reminders')
    
    #~ @classmethod
    #~ def value(cls,ar):
        #~ return reminders(ar.ui,ar.get_user(),days_forward=30,
            #~ max_items=10,before='<ul><li>',separator='</li><li>',after="</li></ul>")



def customize_users():
    """
    Injects application-specific fields to users.User.
    """
    
    dd.inject_field(settings.LINO.user_model,
        'access_class',
        AccessClasses.field(
            default=AccessClasses.public,
            verbose_name=_("Default access class"),
            help_text=_("""The default access class for your calendar events and tasks.""")
    ))
    dd.inject_field(settings.LINO.user_model,
        'calendar',
        models.ForeignKey(Calendar,
            blank=True,null=True,
            verbose_name=_("Default calendar"),
            help_text=_("""The default calendar for your events and tasks.""")
    ))
        

    

def site_setup(site):
    """
    (Called during site setup.)
    
    Adds a "Calendar" tab and the :class:`UpdateReminders` 
    action to `users.User`
    """
    site.modules.users.Users.update_reminders = UpdateReminders()
    
    site.modules.users.Users.add_detail_panel('cal_left',"""
    calendar access_class 
    cal.SubscriptionsByUser
    cal.MembershipsByUser
    """)
    site.modules.users.Users.add_detail_tab('cal',"""
    cal_left:30 cal.RemindersByUser:60
    """,MODULE_LABEL,required=dict(user_groups='office'))
    #~ site.modules.users.Users.add_detail_tab('cal.RemindersByUser')
    
    
    
MODULE_LABEL = _("Calendar")


def setup_main_menu(site,ui,user,m): 
    m  = m.add_menu("cal",MODULE_LABEL)
    if site.use_extensible:
        m.add_action(Panel)
    #~ m  = m.add_menu("events",_("Events"))
    m.add_action(MyEvents)
    #~ m.add_action(MyEventsToday)
    m.add_action(MyEventsSuggested)
    m.add_action(MyEventsNotified)
    #~ m.add_action(MyEventsToSchedule)
    #~ m.add_action(MyEventsToNotify)
    #~ m.add_action(MyEventsToConfirm)
    
    m.add_separator('-')
    m.add_action(Events)
    m.add_action(EventsSuggested)
    m.add_action(EventsNotified)
    #~ m.add_action(EventsToSchedule)
    #~ m.add_action(EventsToNotify)
    #~ m.add_action(EventsToConfirm)
    
    m.add_separator('-')
    #~ m  = m.add_menu("tasks",_("Tasks"))
    m.add_action(MyTasks)
    m.add_action(MyTasksToDo)
    
    m.add_separator('-')
    
    m.add_action(MyInvitations)
    m.add_action(MyPendingInvitations)
    #~ m.add_action(MySentInvitations)
    #~ m.add_action(MyPendingSentInvitations)
    
  
def setup_master_menu(site,ui,user,m): 
    pass
    
def setup_my_menu(site,ui,user,m): 
    pass
    #~ m  = m.add_menu("cal",MODULE_LABEL)
    #~ m.add_action(MySubscriptions)
    
def setup_config_menu(site,ui,user,m): 
    m  = m.add_menu("cal",MODULE_LABEL)
    m.add_action(Places)
    m.add_action(Priorities)
    #~ m.add_action(AccessClasses)
    #~ m.add_action(EventStatuses)
    #~ m.add_action(TaskStatuses)
    #~ m.add_action(EventTypes)
    m.add_action(GuestRoles)
    #~ m.add_action(GuestStatuses)
    m.add_action(Calendars)
  
def setup_explorer_menu(site,ui,user,m):
    m  = m.add_menu("cal",MODULE_LABEL)
    m.add_action(Tasks)
    m.add_action(Guests)
    m.add_action(Subscriptions)
    m.add_action(Memberships)
    #~ m.add_action(RecurrenceSets)

def setup_quicklinks(site,ui,user,m):
    #~ print 20120706
    if site.use_extensible:
        #~ m.add_action(self.modules.cal.Panel)
        m.add_action(Panel)
        m.add_action(MyEventsSuggested)
        m.add_action(MyEventsNotified)
        m.add_action(MyTasksToDo)
        
dd.add_user_group('office',MODULE_LABEL)

customize_users()