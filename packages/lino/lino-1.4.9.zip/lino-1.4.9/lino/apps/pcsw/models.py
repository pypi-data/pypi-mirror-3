# -*- coding: UTF-8 -*-
## Copyright 2008-2012 Luc Saffre
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
Contains PCSW-specific models and tables that have not yet been 
moved into a separate module because they are really very PCSW specific.

See also :doc:`/pcsw/models`.
"""

import logging
logger = logging.getLogger(__name__)

import os
import cgi
import datetime

from django.db import models
from django.db.models import Q
from django.db.utils import DatabaseError
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import string_concat
from django.utils.encoding import force_unicode 
from django.utils.functional import lazy

#~ import lino
#~ logger.debug(__file__+' : started')
#~ from django.utils import translation


#~ from lino import reports
from lino import dd
#~ from lino import layouts
#~ from lino.core import perms
#~ from lino.utils import printable
from lino import mixins
#~ from lino import actions
#~ from lino import fields
from lino.modlib.contacts import models as contacts
from lino.modlib.notes import models as notes
#~ from lino.modlib.links import models as links
from lino.modlib.uploads import models as uploads
from lino.modlib.cal import models as cal
from lino.modlib.users import models as users
from lino.utils.choicelists import HowWell, Gender
from lino.utils.choicelists import ChoiceList
from lino.modlib.users.models import UserLevels
#~ from lino.modlib.properties.utils import KnowledgeField #, StrengthField
#~ from lino.modlib.uploads.models import UploadsByPerson
#~ from lino.models import get_site_config
from lino.core.modeltools import get_field
from lino.core.modeltools import resolve_field
from lino.core.modeltools import range_filter
from lino.utils.babel import DEFAULT_LANGUAGE, babelattr, babeldict_getitem
from lino.utils.babel import language_choices
#~ from lino.utils.babel import add_babel_field, DEFAULT_LANGUAGE, babelattr, babeldict_getitem
from lino.utils import babel 
from lino.utils.choosers import chooser
from lino.utils import mti
from lino.utils.ranges import isrange

from lino.mixins.printable import DirectPrintAction, Printable
#~ from lino.mixins.reminder import ReminderEntry
from lino.core.modeltools import obj2str

from lino.modlib.countries.models import CountryCity
from lino.modlib.cal.models import DurationUnits, update_reminder
from lino.modlib.properties import models as properties
from lino.modlib.cv import models as cv
#~ from lino.modlib.contacts.models import Contact
from lino.core.modeltools import resolve_model, UnresolvedModel

#~ # not used here, but these modules are required in INSTALLED_APPS, 
#~ # and other code may import them using 
#~ # ``from lino.apps.pcsw.models import Property``

#~ from lino.modlib.properties.models import Property
#~ # from lino.modlib.notes.models import NoteType
#~ from lino.modlib.countries.models import Country, City

#~ if settings.LINO.user_model:
    #~ User = resolve_model(settings.LINO.user_model,strict=True)


def is_valid_niss(national_id):
    try:
        niss_validator(national_id)
        return True
    except ValidationError:
        return False
        
def niss_validator(national_id):
    """
    Checks whether the specified `national_id` is a valid 
    Belgian NISS (No. d'identification de sécurité sociale).
    
    Official format is ``YYMMDDx123-97``, where ``YYMMDD`` is the birth date, 
    ``x`` indicates the century (``*`` for the 19th, `` `` (space) for the 20th
    and ``=`` for the 21st century), ``123`` is a sequential number for persons 
    born the same day (odd numbers for men and even numbers for women), 
    and ``97`` is a check digit (remainder of previous digits divided by 97).
    
    """
    national_id = national_id.strip()
    if not national_id:
        return
    if len(national_id) != 13:
        raise ValidationError(
          force_unicode(_('Invalid Belgian SSIN %s : ') % national_id) 
          + force_unicode(_('An SSIN has always 13 positions'))
          ) 
    xtest = national_id[:6] + national_id[7:10]
    if national_id[6] == "=":
        xtest = "2" + xtest
    try:
        xtest = int(xtest)
    except ValueError,e:
        raise ValidationError(
          _('Invalid Belgian SSIN %s : ') % national_id + str(e)
          )
    xtest = abs((xtest-97*(int(xtest/97)))-97)
    if xtest == 0:
        xtest = 97
    found = int(national_id[11:13])
    if xtest != found:
        raise ValidationError(
            force_unicode(_("Invalid Belgian SSIN %s :") % national_id)
            + _("Check digit is %(found)d but should be %(expected)d") % dict(
              expected=xtest, found=found)
            )



#~ CIVIL_STATE_CHOICES = [
  #~ ('1', _("single")   ),
  #~ ('2', _("married")  ),
  #~ ('3', _("divorced") ),
  #~ ('4', _("widowed")  ),
  #~ ('5', _("separated")  ), # Getrennt von Tisch und Bett / 
#~ ]

class CivilState(ChoiceList):
    """
    Civil states, using Belgian codes.
    
    """
    label = _("Civil state")
    
    @classmethod
    def old2new(cls,old):
        if old == '1': return cls.single
        if old == '2': return cls.married
        if old == '3': return cls.divorced
        if old == '4': return cls.widowed
        if old == '5': return cls.separated
        return ''

add = CivilState.add_item
add('10', _("Single"),'single')
add('13', _("Single cohabitating"))
add('18', _("Single with child"))
add('20', _("Married"),'married')
add('21', _("Married (living alone)"))
add('22', _("Married (living with another partner)"))
add('30', _("Widowed"),'widowed')
add('33', _("Widow cohabitating"))
add('40', _("Divorced"),'divorced')
add('50', _("Separated"),'separated')


#~ '10', 'Célibataire', 'Ongehuwd', 'ledig'
#~ '13', 'Célibataire cohab.', NULL, 'ledig mit zus.', 
#~ '18', 'Célibataire avec enf', NULL, 'ledig mit kind', 
#~ '20', 'Marié', 'Gehuwd', 'verheiratet', 
#~ '21', 'Séparé de fait', NULL, 'verheiratet alleine', 
#~ '22', 'Séparé de fait cohab', NULL, 'verheiratet zus.', 
#~ '30', 'Veuf(ve)', NULL, 'Witwe(r)', 
#~ '33', 'Veuf(ve) cohab.', NULL, 'Witwe(r) zus.', 
#~ '40', 'Divorcé', NULL, 'geschieden', 
#~ '50', 'séparé(e) de corps', NULL, 'von Tisch & Bet get.', 








# http://en.wikipedia.org/wiki/European_driving_licence

class ResidenceType(ChoiceList):
    """
    Types of registries for the Belgian residence.
    
    """
    label = _("Residence type")
    
add = ResidenceType.add_item
add('1', _("Registry of citizens"))
add('2', _("Registry of foreigners"))
add('3', _("Waiting for registry"))

#~ RESIDENCE_TYPE_CHOICES = (
  #~ (1  , _("Registry of citizens")   ), # Bevölkerungsregister registre de la population
  #~ (2  , _("Registry of foreigners") ), # Fremdenregister        Registre des étrangers      vreemdelingenregister 
  #~ (3  , _("Waiting for registry")   ), # Warteregister
#~ )

class BeIdCardType(ChoiceList):
    """
    List of Belgian Identification Card Types.
    
    """
    label = _("eID card type")
    
add = BeIdCardType.add_item
add('1',_("Belgian citizen")) 
# ,de=u"Belgischer Staatsbürger",fr=u"Citoyen belge"),
add('6', _("Kids card (< 12 year)")) 
#,de=u"Kind unter 12 Jahren"),
add('8', _("Habilitation")) 
#,fr=u"Habilitation",nl=u"Machtiging")
add('11', _("Foreigner card A"))
        #~ nl=u"Bewijs van inschrijving in het vreemdelingenregister - Tijdelijk verblijf",
        #~ fr=u"Certificat d'inscription au registre des étrangers - Séjour temporaire",
        #~ de=u"Ausländerkarte A Bescheinigung der Eintragung im Ausländerregister - Vorübergehender Aufenthalt",
add('12', _("Foreigner card B"))
        #~ nl=u"Bewijs van inschrijving in het vreemdelingenregister",
        #~ fr=u"Certificat d'inscription au registre des étrangers",
        #~ de=u"Ausländerkarte B (Bescheinigung der Eintragung im Ausländerregister)",
add('13', _("Foreigner card C"))
        #~ nl=u"Identiteitskaart voor vreemdeling",
        #~ fr=u"Carte d'identité d'étranger",
        #~ de=u"C (Personalausweis für Ausländer)",
add('14', _("Foreigner card D"))
        #~ nl=u"EG - langdurig ingezetene",
        #~ fr=u"Résident de longue durée - CE",
        #~ de=u"Daueraufenthalt - EG",
add('15', _("Foreigner card E"))
        #~ nl=u"Verklaring van inschrijving",
        #~ fr=u"Attestation d’enregistrement",
        #~ de=u"Anmeldebescheinigung",
add('16', _("Foreigner card E+"))
add('17', _("Foreigner card F"))
        #~ nl=u"Verblijfskaart van een familielid van een burger van de Unie",
        #~ fr=u"Carte de séjour de membre de la famille d’un citoyen de l’Union",
        #~ de=u"Aufenthaltskarte für Familienangehörige eines Unionsbürgers",
add('18', _("Foreigner card F+"))

#~ BEID_CARD_TYPES = {
  #~ '1' : dict(en=u"Belgian citizen",de=u"Belgischer Staatsbürger",fr=u"Citoyen belge"),
  #~ '6' : dict(en=u"Kids card (< 12 year)",de=u"Kind unter 12 Jahren"),
  #~ '8' : dict(en=u"Habilitation",fr=u"Habilitation",nl=u"Machtiging"),
  #~ '11' : dict(
        #~ en=u"Foreigner card type A",
        #~ nl=u"Bewijs van inschrijving in het vreemdelingenregister - Tijdelijk verblijf",
        #~ fr=u"Certificat d'inscription au registre des étrangers - Séjour temporaire",
        #~ de=u"Bescheinigung der Eintragung im Ausländerregister - Vorübergehender Aufenthalt",
      #~ ),
  #~ '12' : dict(
        #~ en=u"Foreigner card type B",
        #~ nl=u"Bewijs van inschrijving in het vreemdelingenregister",
        #~ fr=u"Certificat d'inscription au registre des étrangers",
        #~ de=u"Bescheinigung der Eintragung im Ausländerregister",
      #~ ),
  #~ '13' : dict(
        #~ en=u"Foreigner card type C",
        #~ nl=u"Identiteitskaart voor vreemdeling",
        #~ fr=u"Carte d'identité d'étranger",
        #~ de=u"Personalausweis für Ausländer",
      #~ ),
  #~ '14' : dict(
        #~ en=u"Foreigner card type D",
        #~ nl=u"EG - langdurig ingezetene",
        #~ fr=u"Résident de longue durée - CE",
        #~ de=u"Daueraufenthalt - EG",
      #~ ),
  #~ '15' : dict(
        #~ en=u"Foreigner card type E",
        #~ nl=u"Verklaring van inschrijving",
        #~ fr=u"Attestation d’enregistrement",
        #~ de=u"Anmeldebescheinigung",
      #~ ),
  #~ '16' : dict(
        #~ en=u"Foreigner card type E+",
      #~ ),
  #~ '17' : dict(
        #~ en=u"Foreigner card type F",
        #~ nl=u"Verblijfskaart van een familielid van een burger van de Unie",
        #~ fr=u"Carte de séjour de membre de la famille d’un citoyen de l’Union",
        #~ de=u"Aufenthaltskarte für Familienangehörige eines Unionsbürgers",
      #~ ),
  #~ '18' : dict(
        #~ en=u"Foreigner card type F+",
      #~ ),
#~ }



class CpasPartner(dd.Model,mixins.DiffingMixin):
#~ class Partner(mixins.DiffingMixin,contacts.Contact):
    """
    """
    
    class Meta:
        abstract = True
        app_label = 'contacts'
  
    #~ id = models.AutoField(primary_key=True,verbose_name=_("Partner #"))
    #~ id = models.CharField(max_length=10,primary_key=True,verbose_name=_("ID"))
    
    is_active = models.BooleanField(
        verbose_name=_("is active"),default=True,
        help_text = "Only active Persons may be used when creating new operations.")
    
    newcomer = models.BooleanField(
        verbose_name=_("newcomer"),default=False)
    """Means that there's no responsible user for this partner yet. 
    New partners may not be used when creating new operations."""
    
    is_deprecated = models.BooleanField(
        verbose_name=_("deprecated"),default=False)
    """Means that data of this partner may be obsolete because 
    there were no confirmations recently. 
    Deprecated partners may not be used when creating new operations."""
    
    activity = models.ForeignKey("pcsw.Activity",
        blank=True,null=True)
    "Pointer to :class:`pcsw.Activity`. May be empty."
    
    bank_account1 = models.CharField(max_length=40,
        blank=True,# null=True,
        verbose_name=_("Bank account 1"))
        
    bank_account2 = models.CharField(max_length=40,
        blank=True,# null=True,
        verbose_name=_("Bank account 2"))
        
    def disable_delete(self):
        #~ if settings.TIM2LINO_IS_IMPORTED_PARTNER(self):
        if settings.LINO.is_imported_partner(self):
            return _("Cannot delete companies and persons imported from TIM")
        return super(CpasPartner,self).disable_delete()
          


#~ class Person(CpasPartner,contacts.PersonMixin,contacts.Partner,contacts.Born,Printable):
class Person(CpasPartner,contacts.Person,contacts.Born,Printable):
    """
    Represents a physical person.
    
    """
    
    class Meta(contacts.PersonMixin.Meta):
        app_label = 'contacts'
        verbose_name = _("Person") # :doc:`/tickets/14`
        verbose_name_plural = _("Persons") # :doc:`/tickets/14`
        
    def get_queryset(self):
        return self.model.objects.select_related(
            'country','city','coach1','coach2','nationality')
        
    remarks2 = models.TextField(_("Remarks (Social Office)"),blank=True) # ,null=True)
    gesdos_id = models.CharField(max_length=40,blank=True,
        #null=True,
        verbose_name=_("Gesdos ID"))
        
    is_cpas = models.BooleanField(verbose_name=_("receives social help"))
    is_senior = models.BooleanField(verbose_name=_("is senior"))
    #~ is_minor = models.BooleanField(verbose_name=_("is minor"))
    group = models.ForeignKey("pcsw.PersonGroup",blank=True,null=True,
        verbose_name=_("Integration phase"))
    #~ is_dsbe = models.BooleanField(verbose_name=_("is coached"),default=False)
    #~ "Indicates whether this Person is coached."
    
    coached_from = models.DateField(
        blank=True,null=True,
        verbose_name=_("Coached from"))
    coached_until = models.DateField(
        blank=True,null=True,
        verbose_name=_("until"))
    
    coach1 = dd.ForeignKey(settings.LINO.user_model,
        blank=True,null=True,
        verbose_name=_("Coach 1"),related_name='coached1')
    coach2 = dd.ForeignKey(settings.LINO.user_model,
        blank=True,null=True,
        verbose_name=_("Coach 2"),related_name='coached2')
        
    birth_place = models.CharField(_("Birth place"),
        max_length=200,
        blank=True,
        #null=True
        )
    birth_country = models.ForeignKey("countries.Country",
        blank=True,null=True,
        verbose_name=_("Birth country"),related_name='by_birth_place')
    #~ civil_state = models.CharField(max_length=1,
        #~ blank=True,# null=True,
        #~ verbose_name=_("Civil state"),
        #~ choices=CIVIL_STATE_CHOICES) 
    civil_state = CivilState.field(blank=True) 
    national_id = models.CharField(max_length=200,
        blank=True,verbose_name=_("National ID")
        #~ ,validators=[niss_validator]
        )
        
    health_insurance = dd.ForeignKey(settings.LINO.company_model,blank=True,null=True,
        verbose_name=_("Health insurance"),related_name='health_insurance_for')
    pharmacy = dd.ForeignKey(settings.LINO.company_model,blank=True,null=True,
        verbose_name=_("Pharmacy"),related_name='pharmacy_for')
    
    nationality = dd.ForeignKey('countries.Country',
        blank=True,null=True,
        related_name='by_nationality',
        verbose_name=_("Nationality"))
    #~ tim_nr = models.CharField(max_length=10,blank=True,null=True,unique=True,
        #~ verbose_name=_("TIM ID"))
    card_number = models.CharField(max_length=20,
        blank=True,#null=True,
        verbose_name=_("eID card number"))
    card_valid_from = models.DateField(
        blank=True,null=True,
        verbose_name=_("ID card valid from"))
    card_valid_until = models.DateField(
        blank=True,null=True,
        verbose_name=_("until"))
        
    #~ card_type = models.CharField(max_length=20,
        #~ blank=True,# null=True,
        #~ verbose_name=_("eID card type"))
    #~ "The type of the electronic ID card. Imported from TIM."
    
    card_type = BeIdCardType.field(blank=True)
    
    card_issuer = models.CharField(max_length=50,
        blank=True,# null=True,
        verbose_name=_("eID card issuer"))
    "The administration who issued this ID card. Imported from TIM."
    
    #~ eid_panel = dd.FieldSet(_("eID card"),
        #~ "card_number card_valid_from card_valid_until card_issuer card_type:20",
        #~ card_number=_("number"),
        #~ card_valid_from=_("valid from"),
        #~ card_valid_until=_("until"),
        #~ card_issuer=_("issued by"),
        #~ card_type=_("eID card type"),
        #~ )
    
    noble_condition = models.CharField(max_length=50,
        blank=True,#null=True,
        verbose_name=_("noble condition"))
    "The eventual noble condition of this person. Imported from TIM."
        
    
    #~ residence_type = models.SmallIntegerField(blank=True,null=True,
        #~ verbose_name=_("Residence type"),
        #~ choices=RESIDENCE_TYPE_CHOICES,
        #~ max_length=1,
        #~ )
    residence_type = ResidenceType.field(blank=True) 
        
    in_belgium_since = models.DateField(_("Lives in Belgium since"),
        blank=True,null=True)
    unemployed_since = models.DateField(_("Seeking work since"),blank=True,null=True)
    #~ work_permit_exempt = models.BooleanField(verbose_name=_("Work permit exemption"))
    needs_residence_permit = models.BooleanField(verbose_name=_("Needs residence permit"))
    needs_work_permit = models.BooleanField(verbose_name=_("Needs work permit"))
    #~ work_permit_valid_until = models.DateField(blank=True,null=True,verbose_name=_("Work permit valid until"))
    work_permit_suspended_until = models.DateField(blank=True,null=True,verbose_name=_("suspended until"))
    aid_type = models.ForeignKey("pcsw.AidType",blank=True,null=True)
        #~ verbose_name=_("aid type"))
        
    income_ag    = models.BooleanField(verbose_name=_("unemployment benefit")) # Arbeitslosengeld
    income_wg    = models.BooleanField(verbose_name=_("waiting pay")) # Wartegeld
    income_kg    = models.BooleanField(verbose_name=_("sickness benefit")) # Krankengeld
    income_rente = models.BooleanField(verbose_name=_("retirement pension")) # Rente
    income_misc  = models.BooleanField(verbose_name=_("other incomes")) # Andere Einkommen
    
    is_seeking = models.BooleanField(_("is seeking work"))
    unavailable_until = models.DateField(blank=True,null=True,verbose_name=_("Unavailable until"))
    unavailable_why = models.CharField(max_length=100,
        blank=True,# null=True,
        verbose_name=_("reason"))
    
    obstacles = models.TextField(_("Obstacles"),blank=True,null=True)
    skills = models.TextField(_("Other skills"),blank=True,null=True)
    job_agents = models.CharField(max_length=100,
        blank=True,# null=True,
        verbose_name=_("Job agents"))
    
    #~ job_office_contact = models.ForeignKey("contacts.Contact",
    #~ job_office_contact = models.ForeignKey("links.Link",
    job_office_contact = models.ForeignKey("contacts.Role",
      blank=True,null=True,
      verbose_name=_("Contact person at local job office"),
      related_name='persons_job_office')
      
    print_eid_content = DirectPrintAction(_("eID sheet"),'eid-content')
    
    @chooser()
    def job_office_contact_choices(cls):
        sc = settings.LINO.site_config # get_site_config()
        if sc.job_office is not None:
            #~ return sc.job_office.contact_set.all()
            #~ return sc.job_office.rolesbyparent.all()
            return sc.job_office.rolesbycompany.all()
            #~ return links.Link.objects.filter(a=sc.job_office)
        return []
        
    #~ @classmethod
    #~ def setup_report(model,table):
        #~ u"""
        #~ rpt.add_action(DirectPrintAction('auskblatt',_("Auskunftsblatt"),'persons/auskunftsblatt.odt'))
        #~ Zur Zeit scheint es so, dass das Auskunftsblatt eher überflüssig wird.
        #~ """
        # table.add_action(DirectPrintAction(table,'eid',_("eID sheet"),'eid-content'))
        #~ table.add_action(DirectPrintAction('eid',_("eID sheet"),'eid-content'))
        # table.add_action(DirectPrintAction('cv',_("Curiculum vitae"),'persons/cv.odt'))
        # table.set_detail_layout(PersonDetail(table))
        
    def __unicode__(self):
        #~ return u"%s (%s)" % (self.get_full_name(salutation=False),self.pk)
        return u"%s %s (%s)" % (self.last_name.upper(),self.first_name,self.pk)
        
    def get_active_contract(self):
        """
        Return the one and only active contract on this client.
        If there are more than 1 active contracts, return None.
        """
        v = datetime.date.today()
        q1 = Q(applies_from__isnull=True) | Q(applies_from__lte=v)
        q2 = Q(applies_until__isnull=True) | Q(applies_until__gte=v)
        q3 = Q(date_ended__isnull=True) | Q(date_ended__gte=v)
        flt = Q(q1,q2,q3)
        #~ flt = range_filter(datetime.date.today(),'applies_from','applies_until')
        qs1 = self.isip_contract_set_by_person.filter(flt)
        qs2 = self.jobs_contract_set_by_person.filter(flt)
        if qs1.count() + qs2.count() == 1:
            if qs1.count() == 1: return qs1[0]
            if qs2.count() == 1: return qs2[0]
        
    def full_clean(self,*args,**kw):
        if not isrange(self.coached_from,self.coached_until):
            raise ValidationError(u'Coaching period ends before it started.')
        super(Person,self).full_clean(*args,**kw)
            
    #~ def clean(self):
        #~ if self.job_office_contact: 
            #~ if self.job_office_contact.b == self:
                #~ raise ValidationError(_("Circular reference"))
        #~ super(Person,self).clean()
        
    #~ def card_type_text(self,request):
        #~ if self.card_type:
            #~ s = babeldict_getitem(BEID_CARD_TYPES,self.card_type)
            #~ if s:
                #~ return s
            #~ return _("Unknown card type %r") % self.card_type
        #~ return _("Not specified") # self.card_type
    #~ card_type_text.return_type = dd.DisplayField(_("eID card type"))
        
    def get_print_language(self,pm):
        "Used by DirectPrintAction"
        return self.language
        
    def save(self,*args,**kw):
        if self.job_office_contact: 
            if self.job_office_contact.person == self:
                raise ValidationError(_("Circular reference"))
        super(Person,self).save(*args,**kw)
        self.update_reminders()
        
    def update_reminders(self):
        """
        Creates or updates automatic tasks controlled directly by this Person.
        """
        user = self.coach2 or self.coach1
        if user:
            def f():
                M = DurationUnits.months
                update_reminder(1,self,user,
                  self.card_valid_until,
                  _("eID card expires in 2 months"),2,M)
                update_reminder(2,self,user,
                  self.unavailable_until,
                  _("becomes available again in 1 month"),1,M)
                update_reminder(3,self,user,
                  self.work_permit_suspended_until,
                  _("work permit suspension ends in 1 month"),1,M)
                update_reminder(4,self,user,
                  self.coached_until,
                  _("coaching ends in 1 month"),1,M)
            babel.run_with_language(user.language,f)
              
          
    #~ def get_auto_task_defaults(self,**kw):
    def update_owned_instance(self,owned):
        owned.project = self
        super(Person,self).update_owned_instance(owned)
        
    @classmethod
    def get_reminders(model,ui,user,today,back_until):
        q = Q(coach1__exact=user) | Q(coach2__exact=user)
        
        def find_them(fieldname,today,delta,msg,**linkkw):
            filterkw = { fieldname+'__lte' : today + delta }
            if back_until is not None:
                filterkw.update({ 
                    fieldname+'__gte' : back_until
                })
            for obj in model.objects.filter(q,**filterkw).order_by(fieldname):
                linkkw.update(fmt='detail')
                url = ui.get_detail_url(obj,**linkkw)
                html = '<a href="%s">%s</a>&nbsp;: %s' % (url,unicode(obj),cgi.escape(msg))
                yield ReminderEntry(getattr(obj,fieldname),html)
            
        #~ delay = 30
        #~ for obj in model.objects.filter(q,
              #~ card_valid_until__lte=date+datetime.timedelta(days=delay)).order_by('card_valid_until'):
            #~ yield ReminderEntry(obj,obj.card_valid_until,_("eID card expires in %d days") % delay,fmt='detail',tab=3)
        for o in find_them('card_valid_until', today, datetime.timedelta(days=30),
            _("eID card expires"),tab=0):
            yield o
        for o in find_them('unavailable_until', today, datetime.timedelta(days=30),
            _("becomes available again"),tab=1):
            yield o
        for o in find_them('work_permit_suspended_until', today, datetime.timedelta(days=30),
              _("work permit suspension ends"),tab=1):
            yield o
        for o in find_them('coached_until', today, datetime.timedelta(days=30),
            _("coaching ends"),tab=1):
            yield o
        
    @dd.virtualfield(dd.HtmlBox())
    def image(self,request):
        url = self.get_image_url(request)
        #~ s = '<img src="%s" width="100%%" onclick="window.open(\'%s\')"/>' % (url,url)
        s = '<img src="%s" width="100%%"/>' % url
        s = '<a href="%s" target="_blank">%s</a>' % (url,s)
        return s
        #~ return '<img src="%s" width="120px"/>' % self.get_image_url()
    #~ image.return_type = dd.HtmlBox()

    def get_image_parts(self):
        if self.card_number:
            return ("beid",self.card_number+".jpg")
        return ("pictures","contacts.Person.jpg")
        
    def get_image_url(self,request):
        #~ return settings.MEDIA_URL + "/".join(self.get_image_parts())
        return request.ui.media_url(*self.get_image_parts())
        
    def get_image_path(self):
        return os.path.join(settings.MEDIA_ROOT,*self.get_image_parts())
        
    def get_skills_set(self):
        return self.personproperty_set.filter(
          group=settings.LINO.site_config.propgroup_skills)
    skills_set = property(get_skills_set)
    
    def properties_list(self,*prop_ids):
        """
        Yields a list of the :class:`PersonProperty <lino.modlib.cv.models.PersonProperty>` 
        properties of this person in the specified order.
        If this person has no entry for a 
        requested :class:`Property`, it is simply skipped.
        Used in notes/Note/cv.odt"""
        for pk in prop_ids:
            try:
                yield self.personproperty_set.get(property__id=pk)
            except cv.PersonProperty.DoesNotExist,e:
                pass
        
    def unused_get_property(self,prop_id):
        """used in notes/Note/cv.odt"""
        return self.personproperty_set.get(property__id=prop_id)
        #~ return PersonProperty.objects.get(property_id=prop_id,person=self)
        
        
            
    def overview(self,request):
        def qsfmt(qs):
            s = qs.model._meta.verbose_name_plural + ': '
            if qs.count():
                s += ', '.join([unicode(lk) for lk in qs])
            else:
                s += '<b>%s</b>' % force_unicode(_("not filled in"))
            return force_unicode(s)
        
        lines = []
        #~ lines.append('<div>')
        lines.append(qsfmt(self.languageknowledge_set.all()))
        lines.append(qsfmt(self.study_set.all()))
        lines.append(qsfmt(self.contract_set.all()))
        #~ from django.utils.translation import string_concat
        #~ lines.append('</div>')
        return '<br/>'.join(lines)
    overview.return_type = dd.HtmlBox(_("Overview"))
    
    @dd.displayfield(_("Residence permit"))
    def residence_permit(self,rr):
        kv = dict(type=settings.LINO.site_config.residence_permit_upload_type)
        r = rr.spawn(uploads.UploadsByController,
              master_instance=self,
              known_values=kv)
        return rr.renderer.quick_upload_buttons(r)
        #~ rrr = uploads.UploadsByPerson().request(rr.ui,master_instance=self,known_values=kv)
        #~ return rr.ui.quick_upload_buttons(rrr)
    #~ residence_permit.return_type = dd.DisplayField(_("Residence permit"))
    
    @dd.displayfield(_("Work permit"))
    def work_permit(self,rr):
        kv = dict(type=settings.LINO.site_config.work_permit_upload_type)
        r = rr.spawn(uploads.UploadsByController,
              master_instance=self,
              known_values=kv)
        return rr.renderer.quick_upload_buttons(r)
    #~ work_permit.return_type = dd.DisplayField(_("Work permit"))
    
    @dd.displayfield(_("driving licence"))
    #~ @dd.virtualfield(dd.DisplayField(_("driving licence")))
    def driving_licence(self,rr):
        kv = dict(type=settings.LINO.site_config.driving_licence_upload_type)
        r = rr.spawn(uploads.UploadsByController,
              master_instance=self,known_values=kv)
        return rr.renderer.quick_upload_buttons(r)
    #~ driving_licence.return_type = dd.DisplayField(_("driving licence"))
    
    #~ @dd.displayfield(_("CBSS Identify Person"))
    #~ def cbss_identify_person(self,rr):
        #~ r = rr.spawn(
              #~ settings.LINO.modules.cbss.IdentifyRequestsByPerson,
              #~ master_instance=self)
        #~ return rr.renderer.quick_add_buttons(r)

    #~ @dd.displayfield(_("CBSS Retrieve TI Groups"))
    #~ def cbss_retrieve_ti_groups(self,rr):
        #~ r = rr.spawn(
              #~ settings.LINO.modules.cbss.RetrieveTIGroupsRequestsByPerson,
              #~ master_instance=self)
        #~ return rr.renderer.quick_add_buttons(r)


class PartnerDetail(contacts.PartnerDetail):
    #~ general = contacts.PartnerDetail.main
    #~ main = "general debts.BudgetsByPartner"
    bottom_box = """
    remarks 
    is_person is_company #is_user is_household
    """
    #~ def setup_handle(self,h):
        #~ h.general.label = _("General")
    

class Partners(contacts.Partners):
    """
    Base class for Companies and Persons tables,
    *and* for households.Households.
    Manages disabled_fields using a list of `imported_fields` 
    defined by subclasses.
    """
    
    #~ app_label = 'contacts'
    
    imported_fields = []
    detail_layout = PartnerDetail()
    
    @classmethod
    def disabled_fields(self,obj,ar):
        if settings.LINO.is_imported_partner(obj):
            return self.imported_fields
        return []
        
    #~ @classmethod
    #~ def disable_delete(self,obj,ar):
        #~ if settings.LINO.is_imported_partner(obj):
            #~ return _("Cannot delete contacts imported from TIM")
        #~ return super(Partners,self).disable_delete(obj,ar)
        
    @classmethod
    def do_setup(self):
        super(Partners,self).do_setup()
        #~ self.imported_fields = dd.fields_list(contacts.Partner,
        self.imported_fields = dd.fields_list(self.model,
          '''name remarks region zip_code city country 
          street_prefix street street_no street_box 
          addr2
          language 
          phone fax email url
          is_person is_company
          ''')
        

class AllPartners(contacts.AllPartners,Partners):
    app_label = 'contacts'
    #~ pass

class Company(CpasPartner,contacts.Company):
  
    """
    Inner class Meta is necessary because of :doc:`/tickets/14`.
    """
    
    class Meta(contacts.Company.Meta):
        app_label = 'contacts'
        
        
    #~ vat_id = models.CharField(max_length=200,blank=True)
    #~ type = models.ForeignKey('contacts.CompanyType',blank=True,null=True,verbose_name=_("Company type"))
    #~ prefix = models.CharField(max_length=200,blank=True) 
    # todo: remove hourly_rate after data migration. this is now in Job
    hourly_rate = dd.PriceField(_("hourly rate"),blank=True,null=True)
    #~ is_courseprovider = mti.EnableChild('pcsw.CourseProvider',verbose_name=_("Course provider"))
    
    #~ def disabled_fields(self,request):
        #~ if settings.TIM2LINO_IS_IMPORTED_PARTNER(self):
            #~ return settings.LINO.COMPANY_TIM_FIELDS
        #~ return []
    
  
    

class CompanyDetail(dd.FormLayout):
  
    box3 = """
    country region
    city zip_code:10
    street_prefix street:25 street_no street_box
    addr2:40
    """

    box4 = """
    email:40 
    url
    phone
    gsm
    """

    address_box = "box3 box4"

    box5 = """
    remarks 
    is_courseprovider is_jobprovider
    """

    bottom_box = "box5 contacts.RolesByCompany"

    intro_box = """
    prefix name id language 
    vat_id:12 activity:20 type:20 #hourly_rate
    """

    general = """
    intro_box
    address_box
    bottom_box
    """
    
    notes = "pcsw.NotesByCompany"
    
    main = "general notes"

    def setup_handle(self,lh):
      
        lh.general.label = _("General")
        lh.notes.label = _("Notes")


#~ if settings.LINO.company_model is None:
    #~ raise Exception("settings.LINO.company_model is None")

#~ class Companies(reports.Report):
#~ class Companies(contacts.Contacts):
class Companies(Partners):
    #~ hide_details = [Contact]
    model = settings.LINO.company_model
    detail_layout = CompanyDetail()
        
    order_by = ["name"]
    app_label = 'contacts'
    #~ column_names = ''
    
    @classmethod
    def do_setup(cls):
        #~ if cls.model is None:
            #~ raise Exception("%r.model is None" % cls)
        super(Companies,cls).do_setup()
        cls.imported_fields = dd.fields_list(cls.model,
            '''name remarks
            zip_code city country street street_no street_box 
            language vat_id
            phone fax email 
            bank_account1 bank_account2 activity''')



class PersonDetail(dd.FormLayout):
    
    #~ actor = 'contacts.Person'
    
    main = "tab1 tab2 tab3 tab4 tab5 tab5b history contracts calendar misc"
    
    tab1 = """
    box1 box2
    box4 image:15 #overview 
    """
    
    box1 = """
    last_name first_name:15 title:10
    country city zip_code:10
    street_prefix street:25 street_no street_box
    addr2:40
    """
    
    box2 = """
    id:12 language
    email
    phone fax
    gsm
    """
    
    box3 = """
    gender:10 birth_date age:10 civil_state:15 noble_condition 
    birth_country birth_place nationality:15 national_id:15 
    """
    
    eid_panel = """
    card_number:12 card_valid_from:12 card_valid_until:12 card_issuer:10 card_type:12
    """

    box4 = """
    box3
    eid_panel
    """


    status = """
    in_belgium_since:15 residence_type gesdos_id health_insurance
    #pharmacy
    coach1:12 coach2:12 group:16 coached_from:12 coached_until:12
    bank_account1:12 bank_account2:12 broker:12 faculty:12
    """
      
    income = """
    aid_type   
    income_ag  income_wg    
    income_kg   income_rente  
    income_misc  
    """
      
    suche = """
    is_seeking unemployed_since work_permit_suspended_until
    unavailable_until:15 unavailable_why:30
    job_office_contact job_agents
    pcsw.ExclusionsByPerson:50x5
    """
      
    papers = """
    needs_residence_permit needs_work_permit 
    residence_permit work_permit driving_licence
    uploads.UploadsByController
    """
    
      
    #~ t2left = """
    #~ status:50
    #~ suche:50 
    #~ """
    
    #~ t2right = """
    #~ income:30
    #~ papers:30
    #~ """
    
    #~ tab2 = "t2left t2right"
    
    tab2 = """
    status:55 income:25
    suche:40  papers:40
    """
    
    
    tab3 = """
    jobs.StudiesByPerson 
    jobs.ExperiencesByPerson:40
    """
    
    tab4 = """
    cv.LanguageKnowledgesByPerson 
    courses.CourseRequestsByPerson  
    # skills obstacles
    """
    
    tab5 = """
    cv.SkillsByPerson cv.SoftSkillsByPerson  skills
    cv.ObstaclesByPerson obstacles 
    """

    tab5b = """
    jobs.CandidaturesByPerson
    """
      
    history = """
    pcsw.NotesByPerson #:60 #pcsw.LinksByPerson:20
    outbox.MailsByProject:60 postings.PostingsByProject:40
    """
    
    contracts = """
    isip.ContractsByPerson
    jobs.ContractsByPerson
    """
    
    calendar = """
    cal.EventsByProject
    cal.TasksByProject
    """
    
    misc = """
    activity pharmacy 
    is_active is_cpas is_senior is_deprecated newcomer
    remarks:30 remarks2:30 contacts.RolesByPerson:30 households.MembersByPerson:30
    # links.LinksToThis:30 links.LinksFromThis:30 
    """
    
    def setup_handle(self,lh):
      
        lh.tab1.label = _("Person")
        lh.tab2.label = _("Status")
        lh.tab3.label = _("Education")
        lh.tab4.label = _("Languages")
        lh.tab5.label = _("Competences")
        lh.tab5b.label = _("Job Requests")
        lh.history.label = _("History")
        lh.contracts.label = _("Contracts")
        lh.calendar.label = _("Calendar")
        lh.misc.label = _("Miscellaneous")
        #~ lh.cbss.label = _("CBSS")
        
      
        lh.box1.label = _("Address")
        lh.box2.label = _("Contact")
        lh.box3.label = _("Birth")
        lh.eid_panel.label = _("eID card")
        
        lh.papers.label = _("Papers")
        #~ lh.income.label = _("Income")
        lh.suche.label = _("Job search")
        
        # override default field labels
        #~ lh.eid_panel.card_number.label = _("number")
        #~ lh.eid_panel.card_valid_from.label = _("valid from")
        #~ lh.eid_panel.card_valid_until.label = _("valid until")
        #~ lh.eid_panel.card_issuer.label = _("issued by")
        #~ lh.eid_panel.card_type.label = _("eID card type")
        
        lh.card_number.label = _("number")
        lh.card_valid_from.label = _("valid from")
        lh.card_valid_until.label = _("valid until")
        lh.card_issuer.label = _("issued by")
        lh.card_type.label = _("eID card type")


            

#~ class AllPersons(contacts.Persons):
class AllPersons(Partners):
    """
    List of all Persons.
    """
    #~ debug_actions = True
    model = settings.LINO.person_model
    detail_layout = PersonDetail()
    insert_layout = dd.FormLayout("""
    title first_name last_name
    gender language
    """,window_size=(60,'auto'))
    
    order_by = "last_name first_name id".split()
    column_names = "name_column:20 national_id:10 gsm:10 address_column age:10 email phone:10 id bank_account1 aid_type coach1 language:10"
    
    app_label = 'contacts'
    
    
    @classmethod
    def get_actor_label(self):
        return string_concat(
          self.model._meta.verbose_name_plural,' ',_("(all)"))
    
    @classmethod
    def do_setup(cls):
        #~ cls.PERSON_TIM_FIELDS = dd.fields_list(cls,
        super(AllPersons,cls).do_setup()
        cls.imported_fields = dd.fields_list(cls.model,
          '''name first_name last_name title remarks remarks2
          zip_code city country street street_no street_box 
          birth_date gender birth_place coach1 language 
          phone fax email 
          card_type card_number card_valid_from card_valid_until
          noble_condition card_issuer
          national_id health_insurance pharmacy 
          bank_account1 bank_account2 activity 
          gesdos_id 
          is_cpas is_senior is_active newcomer is_deprecated nationality''')

    #~ @classmethod
    #~ def disabled_fields(self,request):
        #~ if settings.TIM2LINO_IS_IMPORTED_PARTNER(self):
            #~ # return settings.LINO.PERSON_TIM_FIELDS
            #~ return self.__class__.PERSON_TIM_FIELDS
        #~ return []
        
class Persons(AllPersons):
    """
    All Persons except newcomers and inactive persons.
    """
    app_label = 'contacts'
    #~ use_as_default_table = False 
    known_values = dict(is_active=True,newcomer=False)
    #~ filter = dict(is_active=True,newcomer=False)
    #~ label = Person.Meta.verbose_name_plural + ' ' + _("(unfiltered)")
    
    @classmethod
    def get_actor_label(self):
        return self.model._meta.verbose_name_plural

Person._lino_choices_table = Persons

    
class PersonsByNationality(AllPersons):
    #~ app_label = 'contacts'
    master_key = 'nationality'
    order_by = "city name".split()
    column_names = "city street street_no street_box addr2 name country language *"
    


def only_coached_persons(qs,*args,**kw):
    return qs.filter(only_coached_persons_filter(*args,**kw))
    

def only_coached_persons_filter(today,
      d1field='coached_from',
      d2field='coached_until'):
    """
    coached_from and coached_until
    """
    #~ period_until = period_until or period_from
    # Person with both fields empty is not considered coached:
    q1 = Q(**{d2field+'__isnull':False}) | Q(**{d1field+'__isnull':False})
    return Q(q1,range_filter(today,d1field,d2field))
    
  
def only_my_persons(qs,user):
    #~ return qs.filter(Q(coach1__exact=user) | Q(coach2__exact=user))
    return qs.filter(Q(coach1=user) | Q(coach2=user))

class PersonsByCoach1(Persons):
    master_key = 'coach1'
    label = _("Primary clients by coach")
    
    @classmethod
    def get_title(self,rr):
        return _("Primary clients of %s") % rr.master_instance
        
    @classmethod
    def get_request_queryset(self,rr):
        #~ rr.master_instance = rr.get_user()
        qs = super(PersonsByCoach1,self).get_request_queryset(rr)
        #~ only_my_persons(qs,rr.get_user())
        qs = only_coached_persons(qs,datetime.date.today())
        #~ qs = qs.filter()
        #~ print 20111118, 'get_request_queryset', rr.user, qs.count()
        return qs

#~ class IntegTable(dd.Table):
    #~ """
    #~ Abstract base class for all tables that are visible only to 
    #~ Integration Agents (users with a non-empty `integ_level`).
    #~ """
    #~ @classmethod
    #~ def get_permission(self,action,user,obj):
        #~ if not user.integ_level:
            #~ return False
        #~ return super(IntegTable,self).get_permission(action,user,obj)
        
class MyPersons(Persons):
    u"""
    Show only persons attended 
    by the requesting user (or another user, 
    specified via :attr:`lino.ui.requests.URL_PARAMS_SUBST_USER`),
    either as primary or as secondary attendant.
    
    Damit jemand als begleitet gilt, muss mindestens eines der 
    beiden Daten coached_from und coached_until ausgefüllt sein.
    
    """
    required = dict(user_groups = ['integ'])
    #~ required_user_groups = ['integ']
    #~ required_user_level = UserLevels.manager
    
    #~ app_label = 'contacts'
    use_as_default_table = False
    label = _("My clients")
    #~ order_by = ['last_name','first_name']
    #~ column_names = "name_column:20 coached_from coached_until national_id:10 gsm:10 address_column age:10 email phone:10 id bank_account1 aid_type coach1 language:10 *"
    column_names = "name_column:20 applies_from applies_until national_id:10 gsm:10 address_column age:10 email phone:10 id bank_account1 aid_type coach1 language:10"
    
    @classmethod
    def get_title(self,rr):
        return _("Clients of %s") % rr.get_user()
        
    @classmethod
    def get_request_queryset(self,rr):
        qs = super(MyPersons,self).get_request_queryset(rr)
        qs = only_coached_persons(only_my_persons(qs,rr.get_user()),datetime.date.today())
        #~ print 20111118, 'get_request_queryset', rr.user, qs.count()
        return qs
        #~ today = datetime.date.today()
        #~ Q = models.Q
        #~ q1 = Q(coach1__exact=rr.user) | Q(coach2__exact=rr.user)
        #~ q2 = Q(coached_from__isnull=False) | Q(coached_until__isnull=False,coached_until__gte=today)
        #~ return qs.filter(q1,q2)
        
    @dd.virtualfield(models.DateField(_("Contract starts")))
    def applies_from(self,obj,ar):
        c = obj.get_active_contract()
        if c is not None:
            return c.applies_from
            
    @dd.virtualfield(models.DateField(_("Contract ends")))
    def applies_until(self,obj,ar):
        c = obj.get_active_contract()
        if c is not None:
            return c.applies_until

class MyPersonsByGroup(MyPersons):
    master_key = 'group'
    
    @classmethod
    def get_title(self,rr):
        return _("%(phase)s clients of %(user)s") % dict(
          phase=rr.master_instance, user=rr.get_user())
    
class MyActivePersons(MyPersons):
  
    @classmethod
    def get_title(self,rr):
        return _("Active clients of %s") % rr.get_user()
        
    @classmethod
    def get_request_queryset(self,rr):
        qs = super(MyActivePersons,self).get_request_queryset(rr)
        qs = qs.filter(group__active=True)
        return qs
  

#~ if True: # dd.is_installed('pcsw'):

#~ from lino.core.modeltools import models_by_abc


  
#~ class InvalidClients(Persons):
class ClientsTest(Persons):
    """
    Table of persons whose data seems unlogical or inconsistent.
    """
    required = dict(user_level='manager')
    #~ required_user_level = UserLevels.manager
    label = _("Data Test Clients")
    parameters = dict(
      user = dd.ForeignKey(settings.LINO.user_model,blank=True,verbose_name=_("Coached by")),
      today = models.DateField(_("only active on"),blank=True,default=datetime.date.today),
      invalid_niss = models.BooleanField(_("Check NISS validity"),default=True),
      overlapping_contracts = models.BooleanField(_("Check for overlapping contracts"),default=True),
      #~ coached_period = models.BooleanField(_("Check coaching period"),default=True),
      #~ only_my_persons = models.BooleanField(_("Only my persons"),default=True),
    )
    params_template = """overlapping_contracts invalid_niss user today"""
    #~ params_panel_hidden = False
    column_names = "name_column error_message national_id id"
    
    @classmethod
    def get_data_rows(self,ar):
        """
        We only want the users who actually have at least one client.
        We store the corresponding request in the user object 
        under the name `my_persons`.
        """
        from lino.modlib.isip.models import OverlappingContractsTest
        #~ qs = Person.objects.all()
        qs = self.get_request_queryset(ar)
        
        if ar.param_values.user:
            qs = only_my_persons(qs,ar.param_values.user)
        
        if ar.param_values.today:
            qs = only_coached_persons(qs,ar.param_values.today)
            
        logger.info("Building ClientsTest data rows...")
        #~ for p in qs.order_by('name'):
        for person in qs:
            messages = []
            if ar.param_values.overlapping_contracts:
                messages += OverlappingContractsTest(person).check_all()
              
            if ar.param_values.invalid_niss:
                try:
                    niss_validator(person.national_id)
                except ValidationError,e:
                    messages += e.messages
          
            if messages:
                #~ person.error_message = ';<br/>'.join([cgi.escape(m) for m in messages])
                person.error_message = ';\n'.join(messages)
                #~ logger.info("%s : %s", p, p.error_message)
                yield person
        logger.info("Building ClientsTest data rows: done")
                
        
    @dd.displayfield(_('Error message'))
    def error_message(self,obj,ar):
        #~ return obj.error_message.replace('\n','<br/>')
        return obj.error_message
        
    
#~ class OverviewClientsByUser(dd.VirtualTable):
class UsersWithClients(dd.VirtualTable):
    """
    New implementation of persons_by_user
    A customized overview report.
    """
    required = dict(user_groups='integ newcomers')
    #~ label = _("Overview Clients By User")
    label = _("Users with their Clients")
    #~ column_defaults = dict(width=8)
    
    slave_grid_format = 'html'    
    
    #~ @classmethod
    #~ def before_ui_handle(self,ui):
        #~ """
        #~ Builds columns dynamically from the :class:`PersonGroup` database table.
        #~ Called when kernel setup is done, 
        #~ before the UI handle is being instantiated.
        #~ """
        #~ self.column_names = 'user:10'
        #~ for pg in PersonGroup.objects.filter(ref_name__isnull=False).order_by('ref_name'):
            #~ def w(pg):
                #~ def func(self,obj,ar):
                    #~ return MyPersonsByGroup.request(
                      #~ ar.ui,master_instance=pg,subst_user=obj)
                #~ return func
            #~ vf = dd.RequestField(w(pg),verbose_name=pg.name)
            #~ self.add_virtual_field('G'+pg.ref_name,vf)
            #~ self.column_names += ' ' + vf.name 
            
        #~ self.column_names += ' primary_clients active_clients row_total'
        #~ super(OverviewClientsByUser,self).before_ui_handle(ui)
        
    @classmethod
    def setup_columns(self):
        """
        Builds columns dynamically from the :class:`PersonGroup` database table.
        Called when kernel setup is done, 
        before the UI handle is being instantiated.
        """
        self.column_names = 'user:10'
        try:
            for pg in PersonGroup.objects.filter(ref_name__isnull=False).order_by('ref_name'):
                def w(pg):
                    def func(self,obj,ar):
                        return MyPersonsByGroup.request(
                          ar.ui,master_instance=pg,subst_user=obj)
                    return func
                vf = dd.RequestField(w(pg),verbose_name=pg.name)
                self.add_virtual_field('G'+pg.ref_name,vf)
                self.column_names += ' ' + vf.name 
        except DatabaseError:
            # happens during `make appdocs`
            pass
            
        self.column_names += ' primary_clients active_clients row_total'
    

    @classmethod
    def get_data_rows(self,ar):
        """
        We only want the users who actually have at least one client.
        We store the corresponding request in the user object 
        under the name `my_persons`.
        
        The list displays only integration agents, 
        i.e. users with a nonempty `integ_level`.
        
        With one subtility: system admins also have a nonempty `integ_level`, 
        but normal users don't want to see them. 
        So we add the rule that only system admins see other system admins.
        
        """
        profiles = [p for p in dd.UserProfiles.items() if p.integ_level]
        qs = users.User.objects.filter(profile__in=profiles)
        if ar.get_user().profile.level < UserLevels.admin:
            qs = qs.exclude(profile__gte=UserLevels.admin)
        for user in qs.order_by('username'):
            r = MyPersons.request(ar.ui,subst_user=user)
            if r.get_total_count():
                user.my_persons = r
                #~ user._detail_action = users.MySettings.default_action
                yield user
                
    @dd.virtualfield('contacts.Person.coach1')
    def user(self,obj,ar):
        return obj
        
    @dd.requestfield(_("Total"))
    def row_total(self,obj,ar):
        return obj.my_persons
        
    @dd.requestfield(_("Primary clients"))
    def primary_clients(self,obj,ar):
        return PersonsByCoach1.request(ar.ui,master_instance=obj)
        
    @dd.requestfield(_("Active clients"))
    def active_clients(self,obj,ar):
        return MyActivePersons.request(ar.ui,subst_user=obj)


#
# PERSON GROUP
#
class PersonGroup(dd.Model):
    """Integration Phase (previously "Person Group")
    """
    name = models.CharField(_("Designation"),max_length=200)
    ref_name = models.CharField(_("Reference name"),max_length=20,blank=True)
    active = models.BooleanField(_("Considered active"),default=True)
    #~ text = models.TextField(_("Description"),blank=True,null=True)
    class Meta:
        verbose_name = _("Integration Phase")
        verbose_name_plural = _("Integration Phases")
    def __unicode__(self):
        return self.name

class PersonGroups(dd.Table):
    """List of Integration Phases"""
    model = PersonGroup
    #~ required_user_groups = ['integ']
    #~ required_user_level = UserLevels.manager
    required = dict(user_level='manager',user_groups='integ')

    order_by = ["ref_name"]

    
    
    

#
# ACTIVITIY (Berufscode)
#
class Activity(dd.Model):
    class Meta:
        verbose_name = _("activity")
        verbose_name_plural = _("activities")
    name = models.CharField(max_length=80)
    lst104 = models.BooleanField(_("Appears in Listing 104"))
    
    def __unicode__(self):
        return unicode(self.name)

class Activities(dd.Table):
    model = Activity
    #~ required_user_level = UserLevels.manager
    required = dict(user_level='manager')
    #~ label = _('Activities')

#~ class ActivitiesByPerson(Activities):
    #~ master_key = 'activity'

#~ class ActivitiesByCompany(Activities):
    #~ master_key = 'activity'
    
#
# EXCLUSION TYPES (Sperrgründe)
#
class ExclusionType(dd.Model):
    class Meta:
        verbose_name = _("exclusion type")
        verbose_name_plural = _('exclusion types')
        
    name = models.CharField(max_length=200)
    
    def __unicode__(self):
        return unicode(self.name)

class ExclusionTypes(dd.Table):
    #~ required_user_groups = ['integ']
    required = dict(user_level='manager')
    #~ required_user_level = UserLevels.manager
    model = ExclusionType
    #~ label = _('Exclusion Types')
    
#
# EXCLUSIONS (Arbeitslosengeld-Sperrungen)
#
class Exclusion(dd.Model):
    class Meta:
        verbose_name = _("exclusion")
        verbose_name_plural = _('exclusions')
        
    #~ person = models.ForeignKey("contacts.Person")
    person = models.ForeignKey(settings.LINO.person_model)
    type = models.ForeignKey("pcsw.ExclusionType",verbose_name=_("Reason"))
    excluded_from = models.DateField(blank=True,null=True,verbose_name=_("from"))
    excluded_until = models.DateField(blank=True,null=True,verbose_name=_("until"))
    remark = models.CharField(max_length=200,blank=True,verbose_name=_("Remark"))
    
    def __unicode__(self):
        s = unicode(self.type)
        if self.excluded_from: s += ' ' +unicode(self.excluded_from)
        if self.excluded_until: s += '-'+unicode(self.excluded_until)
        return s

class Exclusions(dd.Table):
    required = dict(user_level='manager')
    #~ required_user_level = UserLevels.manager
    model = Exclusion
    #~ label = _('Exclusions')
    
class ExclusionsByPerson(Exclusions):
    required = dict(user_groups='integ')
    #~ required_user_level = None
    master_key = 'person'
    column_names = 'excluded_from excluded_until type remark'


#
# COACHING TYPES 
#
#~ class CoachingType(dd.Model):
    #~ class Meta:
        #~ verbose_name = _("coaching type")
        #~ verbose_name_plural = _('coaching types')
        
    #~ name = models.CharField(max_length=200)
    
    #~ def __unicode__(self):
        #~ return unicode(self.name)

#~ class CoachingTypes(dd.Table):
    #~ model = CoachingType
    
#
# COACHINGS
#
#~ class Coaching(dd.Model):
    #~ class Meta:
        #~ verbose_name = _("coaching")
        #~ verbose_name_plural = _('coachings')
    #~ person = models.ForeignKey("contacts.Person",verbose_name=_("Client"))
    #~ coach = models.ForeignKey("auth.User",verbose_name=_("Coach"))
    #~ type = models.ForeignKey("pcsw.CoachingType",verbose_name=_("Coaching type"))
    #~ remark = models.CharField(max_length=200,blank=False,verbose_name=_("Remark"))
    

#~ class Coachings(dd.Table):
    #~ model = Coaching
    
#~ class CoachingsByPerson(Coachings):
    #~ master_key = 'person'
    #~ column_names = 'coach type remark *'
    #~ label = _('Coaches')


#
# AID TYPES
#
class AidType(babel.BabelNamed):
    class Meta:
        verbose_name = _("aid type")
        verbose_name_plural = _('aid types')
        
    #~ name = babel.BabelCharField(_("designation"),max_length=200)
    
    #~ def __unicode__(self):
        #~ return unicode(babel.babelattr(self,'name'))
#~ add_babel_field(AidType,'name')

class AidTypes(dd.Table):
    model = AidType
    column_names = 'name *'
    #~ required_user_level = UserLevels.manager
    required = dict(user_level='manager')





#
# SEARCH
#
class PersonSearch(mixins.AutoUser,mixins.Printable):
    """
    Lino creates a new record in this table for each search request.
    """
    class Meta:
        verbose_name = _("Person Search")
        verbose_name_plural = _('Person Searches')
        
    title = models.CharField(max_length=200,
        verbose_name=_("Search Title"))
    aged_from = models.IntegerField(_("Aged from"),
        blank=True,null=True)
    aged_to = models.IntegerField(_("Aged to"),
        blank=True,null=True)
    #~ gender = contacts.GenderField()
    gender = Gender.field()

    
    only_my_persons = models.BooleanField(_("Only my persons")) # ,default=True)
    
    coached_by = dd.ForeignKey(settings.LINO.user_model,
        verbose_name=_("Coached by"),
        related_name='persons_coached',
        blank=True,null=True)
    period_from = models.DateField(
        blank=True,null=True,
        verbose_name=_("Period from"))
    period_until = models.DateField(
        blank=True,null=True,
        verbose_name=_("until"))
    
    def result(self):
        for p in PersonsBySearch().request(master_instance=self):
            yield p
        
    def __unicode__(self):
        return self._meta.verbose_name + ' "%s"' % (self.title or _("Unnamed"))
        
    #~ def get_print_language(self,pm):
        #~ return DEFAULT_LANGUAGE

    print_suchliste = DirectPrintAction(_("Print"),'suchliste')
    
    #~ @classmethod
    #~ def setup_report(model,rpt):
        # rpt.add_action(DirectPrintAction(rpt,'suchliste',_("Print"),'suchliste'))
        #~ rpt.add_action(DirectPrintAction('suchliste',_("Print"),'suchliste'))
        
class PersonSearches(dd.Table):
    required = dict(user_groups='integ')
    model = PersonSearch
    detail_template = """
    id:8 title 
    only_my_persons coached_by period_from period_until aged_from:10 aged_to:10 gender:10
    pcsw.LanguageKnowledgesBySearch pcsw.WantedPropsBySearch pcsw.UnwantedPropsBySearch
    pcsw.PersonsBySearch
    """
    
class MyPersonSearches(PersonSearches,mixins.ByUser):
    #~ model = PersonSearch
    pass
    
class WantedLanguageKnowledge(dd.Model):
    search = models.ForeignKey(PersonSearch)
    language = models.ForeignKey("countries.Language",verbose_name=_("Language"))
    spoken = HowWell.field(verbose_name=_("spoken"))
    written = HowWell.field(verbose_name=_("written"))

class WantedSkill(properties.PropertyOccurence):
    class Meta:
        app_label = 'properties'
        verbose_name = _("Wanted property")
        verbose_name_plural = _("Wanted properties")
        
    search = models.ForeignKey(PersonSearch)
    
class UnwantedSkill(properties.PropertyOccurence):
    class Meta:
        app_label = 'properties'
        verbose_name = _("Unwanted property")
        verbose_name_plural = _("Unwanted properties")
    search = models.ForeignKey(PersonSearch)
    
    
class LanguageKnowledgesBySearch(dd.Table):
    required = dict(user_groups='integ')
    label = _("Wanted language knowledges")
    master_key = 'search'
    model = WantedLanguageKnowledge

class WantedPropsBySearch(dd.Table):
    required = dict(user_groups = 'integ')
    label = _("Wanted properties")
    master_key = 'search'
    model = WantedSkill

class UnwantedPropsBySearch(dd.Table):
    required = dict(user_groups = 'integ')
    label = _("Unwanted properties")
    master_key = 'search'
    model = UnwantedSkill

#~ class PersonsBySearch(dd.Table):
class PersonsBySearch(AllPersons):
    """
    This is the slave report of a PersonSearch that shows the 
    Persons matching the search criteria. 
    
    It is a slave report without 
    :attr:`master_key <lino.dd.Table.master_key>`,
    which is allowed only because it also overrides
    :meth:`get_request_queryset`
    """
  
    required = dict(user_groups = 'integ')
    #~ model = Person
    master = PersonSearch
    #~ 20110822 app_label = 'pcsw'
    label = _("Found persons")
    
    #~ can_add = perms.never
    #~ can_change = perms.never
    
    @classmethod
    def get_request_queryset(self,rr):
        """
        Here is the code that builds the query. It can be quite complex.
        See :srcref:`/lino/apps/pcsw/models.py` 
        (search this file for "PersonsBySearch").
        """
        search = rr.master_instance
        if search is None:
            return []
        kw = {}
        qs = self.model.objects.order_by('name')
        today = datetime.date.today()
        if search.gender:
            qs = qs.filter(gender__exact=search.gender)
        if search.aged_from:
            #~ q1 = models.Q(birth_date__isnull=True)
            #~ q2 = models.Q(birth_date__gte=today-datetime.timedelta(days=search.aged_from*365))
            #~ qs = qs.filter(q1|q2)
            min_date = today - datetime.timedelta(days=search.aged_from*365)
            qs = qs.filter(birth_date__lte=min_date.strftime("%Y-%m-%d"))
            #~ qs = qs.filter(birth_date__lte=today-datetime.timedelta(days=search.aged_from*365))
        if search.aged_to:
            #~ q1 = models.Q(birth_date__isnull=True)
            #~ q2 = models.Q(birth_date__lte=today-datetime.timedelta(days=search.aged_to*365))
            #~ qs = qs.filter(q1|q2)
            max_date = today - datetime.timedelta(days=search.aged_to*365)
            qs = qs.filter(birth_date__gte=max_date.strftime("%Y-%m-%d"))
            #~ qs = qs.filter(birth_date__gte=today-datetime.timedelta(days=search.aged_to*365))
            
        if search.only_my_persons:
            qs = only_my_persons(qs,search.user)
        
        if search.coached_by:
            qs = only_my_persons(qs,search.coached_by)
            
        if search.period_from:
            qs = only_coached_persons(qs,search.period_from)
            
        if search.period_until:
            qs = only_coached_persons(qs,search.period_until)
          
        required_id_sets = []
        
        required_lk = [lk for lk in search.wantedlanguageknowledge_set.all()]
        if required_lk:
            # language requirements are OR'ed
            ids = set()
            for rlk in required_lk:
                fkw = dict(language__exact=rlk.language)
                if rlk.spoken is not None:
                    fkw.update(spoken__gte=rlk.spoken)
                if rlk.written is not None:
                    fkw.update(written__gte=rlk.written)
                q = cv.LanguageKnowledge.objects.filter(**fkw)
                ids.update(q.values_list('person__id',flat=True))
            required_id_sets.append(ids)
            
        rprops = [x for x in search.wantedskill_set.all()]
        if rprops: # required properties
            ids = set()
            for rp in rprops:
                fkw = dict(property__exact=rp.property) # filter keywords
                if rp.value:
                    fkw.update(value__gte=rp.value)
                q = cv.PersonProperty.objects.filter(**fkw)
                ids.update(q.values_list('person__id',flat=True))
            required_id_sets.append(ids)
          
            
        if required_id_sets:
            s = set(required_id_sets[0])
            for i in required_id_sets[1:]:
                s.intersection_update(i)
                # keep only elements found in both s and i.
            qs = qs.filter(id__in=s)
              
        return qs




class OverlappingContracts(dd.Table):
    required = dict(user_groups = 'integ')
    model = Person
    use_as_default_table = False
    #~ base_queryset = only_coached_persons(Person.objects.all())
    label = _("Overlapping Contracts")
    #~ def a(self):
        
    
    #~ def get_title(self,rr):
        #~ return _("Primary clients of %s") % rr.master_instance
        
    @classmethod
    def get_request_queryset(self,rr):
        #~ rr.master_instance = rr.get_user()
        qs = super(OverlappingContracts,self).get_request_queryset(rr)
        #~ only_my_persons(qs,rr.get_user())
        qs = only_coached_persons(qs,datetime.date.today())
        #~ qs = qs.filter()
        #~ print 20111118, 'get_request_queryset', rr.user, qs.count()
        return qs





def customize_siteconfig():
    """
    Injects application-specific fields to :class:`SiteConfig <lino.models.SiteConfig>`.
    
    """
    
    from lino.models import SiteConfig
    dd.inject_field(SiteConfig,
        'job_office',
        #~ models.ForeignKey("contacts.Company",
        models.ForeignKey(settings.LINO.company_model,
            blank=True,null=True,
            verbose_name=_("Local job office"),
            related_name='job_office_sites'),
        """The Company whose contact persons will be 
        choices for `Person.job_office_contact`.
        """)
        
    dd.inject_field(SiteConfig,
        'residence_permit_upload_type',
        #~ UploadType.objects.get(pk=2)
        models.ForeignKey("uploads.UploadType",
            blank=True,null=True,
            verbose_name=_("Upload Type for residence permit"),
            related_name='residence_permit_sites'),
        """The UploadType for `Person.residence_permit`.
        """)
        
    dd.inject_field(SiteConfig,
        'work_permit_upload_type',
        #~ UploadType.objects.get(pk=2)
        models.ForeignKey("uploads.UploadType",
            blank=True,null=True,
            verbose_name=_("Upload Type for work permit"),
            related_name='work_permit_sites'),
        """The UploadType for `Person.work_permit`.
        """)

    dd.inject_field(SiteConfig,
        'driving_licence_upload_type',
        models.ForeignKey("uploads.UploadType",
            blank=True,null=True,
            verbose_name=_("Upload Type for driving licence"),
            related_name='driving_licence_sites'))
    


def customize_contacts():
    """
    Injects application-specific fields to :mod:`contacts <lino.modlib.contacts>`.
    """
    dd.inject_field('contacts.RoleType',
        'use_in_contracts',
        models.BooleanField(
            verbose_name=_("usable in contracts"),
            default=True
        ),"""Whether Links of this type can be used as contact person of a job contract.
        Deserves more documentation.
        """)
        

def customize_notes():
    """
    Application-specific changes to :mod:`lino.modlib.notes`.
    """
    from lino.modlib.notes.models import Note, Notes

    dd.inject_field(Note,'company',
        models.ForeignKey(settings.LINO.company_model,
            blank=True,null=True,
            help_text="""\
    An optional third-party Organization that is related to this Note.
    The note will then be visible in that company's history panel.
    """
        ))
        
    def get_person(self):
        return self.project
    Note.person = property(get_person)
        
      
    class NotesByPerson(Notes):
        master_key = 'project'
        column_names = "date event_type type subject body user company *"
        order_by = ["-date"]
      
    class NotesByCompany(Notes):
        master_key = 'company'
        column_names = "date project event_type type subject body user *"
        order_by = ["-date"]
        


def customize_sqlite():
    """
    Here is how we install case-insensitive sorting in sqlite3.
    Note that this caused noticeable performance degradation...

    Thanks to 
    - http://efreedom.com/Question/1-3763838/Sort-Order-SQLite3-Umlauts
    - http://docs.python.org/library/sqlite3.html#sqlite3.Connection.create_collation
    - http://www.sqlite.org/lang_createindex.html
    """
    from django.db.backends.signals import connection_created

    def belgian(s):
      
        s = s.decode('utf-8').lower()
        
        s = s.replace(u'ä',u'a')
        s = s.replace(u'à',u'a')
        s = s.replace(u'â',u'a')
        
        s = s.replace(u'ç',u'c')
        
        s = s.replace(u'é',u'e')
        s = s.replace(u'è',u'e')
        s = s.replace(u'ê',u'e')
        s = s.replace(u'ë',u'e')
        
        s = s.replace(u'ö',u'o')
        s = s.replace(u'õ',u'o')
        s = s.replace(u'ô',u'o')
        
        s = s.replace(u'ß',u'ss')
        
        s = s.replace(u'ù',u'u')
        s = s.replace(u'ü',u'u')
        s = s.replace(u'û',u'u')
        
        return s
        
    def stricmp(str1, str2):
        return cmp(belgian(str1),belgian(str2))
        
    def my_callback(sender,**kw):
        from django.db.backends.sqlite3.base import DatabaseWrapper
        if sender is DatabaseWrapper:
            db = kw['connection']
            db.connection.create_collation('BINARY', stricmp)

    connection_created.connect(my_callback)



class Home(cal.Home):
    label = cal.Home.label
    app_label = 'lino'
    detail_template = """
    quick_links:80x1
    pcsw.UsersWithClients:80x8
    coming_reminders:40x16 missed_reminders:40x16
    """


def site_setup(site):
    """
    This is the place where we can override or 
    define application-specific things.
    This includes especially those detail layouts 
    which depend on the *combination* of installed modules.
    """
    
    site.modules.lino.SiteConfigs.set_detail_layout("""
    site_company:20 default_build_method:20 next_partner_id:20 job_office:20
    propgroup_skills propgroup_softskills propgroup_obstacles
    residence_permit_upload_type work_permit_upload_type driving_licence_upload_type
    # lino.ModelsBySite
    """)
    
    site.modules.properties.Properties.set_detail_layout("""
    id group type 
    name
    cv.PersonPropsByProp
    """)
    
    site.modules.countries.Cities.set_detail_layout("""
    name country inscode
    contacts.PartnersByCity jobs.StudiesByCity
    """)
    
    #~ site.modules.countries.Cities.detail_layout.update(main="""
    #~ name country 
    #~ contacts.PartnersByCity jobs.StudiesByCity
    #~ """)
    
    site.modules.countries.Countries.set_detail_layout("""
    isocode name short_code inscode
    countries.CitiesByCountry jobs.StudiesByCountry
    """)
    
    site.modules.uploads.Uploads.set_detail_layout("""
    file user
    type description valid_until
    # person company
    # reminder_date reminder_text delay_value delay_type reminder_done
    modified created owner
    cal.TasksByController
    # show_date show_time 
    # show_date time timestamp
    """)

    site.modules.uploads.Uploads.set_insert_layout("""
    file user
    type valid_until
    description 
    # owner
    """,window_size=(60,'auto'))

  
    #~ from lino.modlib.cal import models as cal

    #~ class EventDetail(cal.EventDetail):
        #~ # inherits the start and end panels
        #~ main = """
        #~ type summary user project
        #~ start end #all_day #duration status 
        #~ place priority access_class transparent #rset 
        #~ calendar owner created:20 modified:20 user_modified 
        #~ description GuestsByEvent
        #~ """
    #~ site.modules.cal.Events.set_detail_layout(EventDetail())
    
    #~ site.modules.cal.Events.set_detail_layout("""
    #~ type summary user project
    #~ start end #all_day #duration state workflow_buttons 
    #~ place priority access_class transparent #rset 
    #~ calendar owner created:20 modified:20 user_modified 
    #~ description GuestsByEvent
    #~ """)
    
    site.modules.cal.Events.set_detail_layout("general more")
    site.modules.cal.Events.add_detail_panel("general","""
    calendar summary user project 
    start end 
    place priority access_class transparent #rset 
    owner state workflow_buttons
    description GuestsByEvent 
    """,_("General"))
    site.modules.cal.Events.add_detail_panel("more","""
    id created:20 modified:20  
    outbox.MailsByController postings.PostingsByController
    """,_("More"))
    
    site.modules.cal.Events.set_insert_layout("""
    summary 
    start end 
    calendar project 
    """,
    start="start_date start_time",
    end="end_date end_time",
    window_size=(60,'auto'))
    
    #~ site.modules.users.Users.set_detail_layout(box2 = """
    #~ level
    #~ integ_level
    #~ cbss_level
    #~ newcomers_level newcomer_quota
    #~ debts_level
    #~ """)
    site.modules.users.Users.set_detail_layout("""
    box1:50 box2:25
    remarks AuthoritiesGiven 
    """,
    box2="""
    newcomer_quota
    """)
    
        
    site.modules.notes.Notes.set_detail_layout(
        left = """
        date:10 event_type:25 type:25
        subject 
        project company
        id user:10 language:8 build_time
        body
        """,
        
        right = """
        uploads.UploadsByController
        # thirds.ThirdsByController:30
        outbox.MailsByController
        postings.PostingsByController
        cal.TasksByController
        """,
        
        main = """
        left:60 right:30
        """
    )
    
    site.modules.notes.Notes.set_insert_layout("""
    event_type:25 type:25
    subject 
    project company
    """,window_size=(50,'auto'))
    
    #~ site.modules.outbox.Mails.set_detail_layout("""
    #~ subject project date 
    #~ user sent #build_time id owner
    #~ RecipientsByMail:50x5 AttachmentsByMail:20x5 uploads.UploadsByOwner:20x5
    #~ body:90x10
    #~ """)
        
    #~ site.modules.courses.CourseProviders.set_detail_layout(CourseProviderDetail())
    
    
dd.add_user_group('integ',_("Integration"))
    
    
#~ def customize_user_groups():
    #~ """
    #~ Define application-specific 
    #~ :class:`UserGroups <lino.core.perms.UserGroups>`.
    #~ """
    #~ add = dd.UserGroups.add_item
    #~ add('office',_("Calendar & Outbox"),'office')
    #~ add('integ',_("Integration"),'integ')
    #~ add('cbss',_("CBSS"),'cbss')
    #~ add('newcomers',_("Newcomers"),'newcomers')
    #~ add('debts',_("Debts"),'debts')

#~ def customize_user_profiles():
    
    #~ def add(value,label,*args,**kw):
        #~ dd.UserProfiles.add_item(value,label,None,*args,**kw)
    #~ """
        #~ #     label                            level      office      integ       cbss       newcomers  debts
        #~ ====  ================================ ========== =========== =========== ========== ========== ========"""
    #~ add('100', _("Integration Agent"),          'user',    'user',     'user',    'user',    '',        '')
    #~ add('110', _("Integration Agent (Senior)"), 'user',    'manager',  'manager', 'user',    '',        '')
    #~ add('200', _("Newcomers consultant"),       'user',    'user',     '',        'user',    'user',    '')
    #~ add('300', _("Debts consultant"),           'user',    'user',     '',        '',        '',        'user')
    #~ add('400', _("Readonly Manager"),           'manager', 'manager',  'manager', 'manager', 'manager', 'manager', readonly=True)
    #~ add('500', _("CBSS only"),                  'user',    '',         '',        'user',    '',        '')
    #~ add('900', _("Administrator"),              'admin',   'admin',    'admin',   'admin',   'admin',   'admin')
    
    
    #~ short_levels = dict(A='admin',U='user',_='',M='manager',G='guest')
    #~ keys = ['level'] + [g.value+'_level' for g in UserGroups.items()]
    #~ def add(value,label,name,memberships,**kw):
        #~ if len(memberships.split()) != len(attrs):
            #~ raise Exception(
                #~ "Invalid profile specification %r : must contain %d letters" 
                #~ % (memberships,len(attrs))
        #~ for i,k in enumerate(memberships.split()):
            #~ kw[keys[i]] = short_levels[k]
        #~ dd.UserProfiles.add_item(value,label,None,**kw)
    
    
    
    
    #~ add = dd.UserProfiles.add_item
    
    #~ kw = dict(level='user',office_level='user',integ_level='user',cbss_level='user',
        #~ newcomers_level='',debts_level='')
    #~ add('100',_("Integration Agent"),**kw)
    
    #~ kw.update(integ_level='manager')
    #~ add('110', _("Integration Agent (Senior)"),**kw)
    
    #~ kw.update(integ_level='',newcomers_level='user')
    #~ add('200', _("Newcomers consultant"),**kw)
    
    #~ kw.update(newcomers_level='',debts_level='user')
    #~ add('200', _("Debts consultant"),**kw)
    
    #~ def get_user_profiles(self):
        #~ def add(value,label,*args,**kw):
            #~ dd.UserProfiles.add_item(value,label,None,*args,**kw)
        #~ yield '100', _("Integration Agent"),          'user',    'user',     'user',    'user',    '',        '')


customize_siteconfig()
customize_contacts()        
customize_notes()
customize_sqlite()
#~ customize_user_groups()
#~ customize_user_profiles()
#~ setup_user_profiles()
  
