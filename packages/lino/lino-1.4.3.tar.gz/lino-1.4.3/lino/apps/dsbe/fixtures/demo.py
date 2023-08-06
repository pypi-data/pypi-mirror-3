# -*- coding: UTF-8 -*-
## Copyright 2008-2012 Luc Saffre
## This file is part of the Lino-DSBE project.
## Lino-DSBE is free software; you can redistribute it and/or modify 
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 3 of the License, or
## (at your option) any later version.
## Lino-DSBE is distributed in the hope that it will be useful, 
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
## GNU General Public License for more details.
## You should have received a copy of the GNU General Public License
## along with Lino-DSBE; if not, see <http://www.gnu.org/licenses/>.

import decimal
from dateutil.relativedelta import relativedelta
ONE_DAY = relativedelta(days=1)

from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _


from lino.utils import i2d, Cycler
from lino.utils.instantiator import Instantiator
from lino.tools import resolve_model
from lino.utils.babel import babel_values, default_language
from lino.utils.restify import restify
from lino.utils import dblogger
from lino.models import update_site_config
from lino.utils import mti

#~ from django.contrib.auth import models as auth
from lino.modlib.users import models as auth
#~ from lino.modlib.contacts.utils import GENDER_FEMALE, GENDER_MALE
from lino.utils.choicelists import Gender
from lino.modlib.jobs import models as jobs
from lino.modlib.contacts import models as contacts
from lino.apps.dsbe import models as dsbe

#~ dblogger.info('Loading')


DEMO_LINKS = [
  dict(name="Lino website",url="http://lino.saffre-rumma.net"),
  dict(name="Django website",url="http://www.djangoproject.com"),
  dict(name="ExtJS website",url="http://www.sencha.com"),
  dict(name="Python website",url="http://www.python.org"),
  dict(name="Google",url="http://www.google.com"),
]
ROW_COUNTER = 0
MAX_LINKS_PER_OWNER = 4
DATE = settings.LINO.demo_date() # i2d(20061014)
    


#~ auth = models.get_app('auth')
#~ projects = models.get_app('projects')
#~ contacts = models.get_app('contacts')
#~ notes = models.get_app('notes')
#~ properties = models.get_app('properties')


#char_pv = Instantiator('properties.CharPropValue').build
#CharPropValue = resolve_model('properties.CharPropValue')
#~ from lino.modlib.properties import models as properties # CharPropValue, BooleanPropValue
#~ CHAR = ContentType.objects.get_for_model(properties.CharPropValue)
#BOOL = ContentType.objects.get_for_model(properties.BooleanPropValue)
#~ INT = ContentType.objects.get_for_model(properties.IntegerPropValue)

#~ def fill_choices(p,model):
    #~ i = 0
    #~ choices = p.choices_list()
    #~ if len(choices) == 0:
        #~ return
    #~ for owner in model.objects.all():
        #~ p.set_value_for(owner,choices[i])
        #~ if i + 1 < len(choices): 
            #~ i += 1
        #~ else:
            #~ i = 0

#~ StudyContent = resolve_model('dsbe.StudyContent')

SECTORS_LIST = u"""
Agriculture & horticulture | Agriculture & horticulture | Landwirtschaft & Garten
Maritime | Maritime | Seefahrt
Medical & paramedical | Médical & paramédical | Medizin & Paramedizin
Construction & buildings| Construction & bâtiment | Bauwesen & Gebäudepflege
Tourism | Horeca | Horeca
Education | Enseignement | Unterricht
Cleaning | Nettoyage | Reinigung
Transport | Transport | Transport
Textile | Textile | Textil
Cultural | Culture | Kultur
Information Technology | Informatique | Informatik
Esthetical | Cosmétique | Kosmetik
Sales | Vente | Verkauf 
Administration & Finance | Administration & Finance | Verwaltung & Finanzwesen
"""



def objects():
  
    sector = Instantiator('jobs.Sector').build
    for ln in SECTORS_LIST.splitlines():
        if ln:
            a = ln.split('|')
            if len(a) == 3:
                kw = dict(en=a[0],fr=a[1],de=a[2])
                yield sector(**babel_values('name',**kw))
                
    horeca = jobs.Sector.objects.get(pk=5)
    function = Instantiator('jobs.Function',sector=horeca).build
    yield function(**babel_values('name',
          de=u"Kellner",
          fr=u'Serveur',
          en=u'Waiter',
          ))
    yield function(**babel_values('name',
          de=u"Koch",
          fr=u'Cuisinier',
          en=u'Cook',
          ))
    yield function(**babel_values('name',
          de=u"Küchenassistent",
          fr=u'Aide Cuisinier',
          en=u'Cook assistant',
          ))
    yield function(**babel_values('name',
          de=u"Tellerwäscher",
          fr=u'Plongeur',
          en=u'Dishwasher',
          ))

    contractType = Instantiator('jobs.ContractType',"ref",
        exam_policy=3,
        build_method='appypdf',
        template=u'art60-7.odt').build
    #~ yield contractType('art60-7a',
      #~ **babel_values('name',
          #~ de=u"Konvention Art.60§7 Sozialökonomie",
          #~ fr=u'Convention art.60§7 économie sociale',
          #~ en=u'Convention art.60§7 social economy',
          #~ ))
    yield contractType('art60-7a',
      **babel_values('name',
          de=u"Sozialökonomie",
          fr=u'économie sociale',
          en=u'social economy',
          ))
    yield contractType('art60-7b',
      **babel_values('name',
          de=u"Sozialökonomie - majoré",
          fr=u'économie sociale - majoré',
          en=u'social economy - increased',
          ))
    yield contractType('art60-7c',
      **babel_values('name',
          de=u"mit Rückerstattung",
          fr=u'avec remboursement',
          en=u'social economy with refund',
          ))
    yield contractType('art60-7d',
      **babel_values('name',
          de=u"mit Rückerstattung Schule",
          fr=u'avec remboursement école',
          en=u'social economy school',
          ))
    yield contractType('art60-7e',
      **babel_values('name',
          de=u"Stadt Eupen",
          fr=u"ville d'Eupen",
          en=u'town',
          ))
    
    contractType = Instantiator('isip.ContractType',"ref",
      exam_policy=1,
      build_method='appypdf',template=u'vse.odt').build
    yield contractType("vsea",**babel_values('name',
          de=u"VSE Ausbildung",
          fr=u"VSE Ausbildung",
          en=u"VSE Ausbildung",
          ))
    yield contractType("vseb",**babel_values('name',
          de=u"VSE Arbeitssuche",
          fr=u"VSE Arbeitssuche",
          en=u"VSE Arbeitssuche",
          ))
    yield contractType("vsec",**babel_values('name',
          de=u"VSE Lehre",
          fr=u"VSE Lehre",
          en=u"VSE Lehre",
          ))
    yield contractType("vsed",**babel_values('name',
          de=u"VSE Vollzeitstudium",
          fr=u"VSE Vollzeitstudium",
          en=u"VSE Vollzeitstudium",
          ))
    yield contractType("vsee",**babel_values('name',
          de=u"VSE Sprachkurs",
          fr=u"VSE Sprachkurs",
          en=u"VSE Sprachkurs",
          ))
    #~ yield contractType(u"VSE Integration")
    #~ yield contractType(u"VSE Cardijn")
    #~ yield contractType(u"VSE Work & Job")
    
  
  
    Person = resolve_model(settings.LINO.person_model)
    Company = resolve_model(settings.LINO.company_model)
    #~ Contact = resolve_model('contacts.Contact')
    Role = resolve_model('contacts.Role')
    RoleType = resolve_model('contacts.RoleType')
    #~ Link = resolve_model('links.Link')
    #~ Contract = resolve_model('jobs.Contract')
    JobProvider = resolve_model('jobs.JobProvider')
    Function = resolve_model('jobs.Function')
    Sector = resolve_model('jobs.Sector')
    Note = resolve_model('notes.Note')
    User = resolve_model('users.User')
    Country = resolve_model('countries.Country')
    
    rt = RoleType.objects.get(pk=4) # It manager
    rt.use_in_contracts = False
    rt.save()

    person = Instantiator(Person).build
    company = Instantiator(Company).build
    #~ contact = Instantiator(Contact).build
    role = Instantiator(Role).build
    #~ link = Instantiator(Link).build
    #~ exam_policy = Instantiator('isip.ExamPolicy').build

    City = resolve_model('countries.City')
    Job = resolve_model('jobs.Job')
    #~ City = settings.LINO.modules.countries.City
    StudyType = resolve_model('jobs.StudyType')
    Country = resolve_model('countries.Country')
    Property = resolve_model('properties.Property')
  
    
    #~ country = Instantiator('countries.Country',"isocode name").build
    #~ yield country('SUHH',"Soviet Union")
    
    eupen = City.objects.get(name__exact='Eupen')
    kettenis = City.objects.get(name__exact='Kettenis')
    vigala = City.objects.get(name__exact='Vigala')
    ee = Country.objects.get(pk='EE')
    be = Country.objects.get(isocode__exact='BE')
    #~ luc = person(first_name="Luc",last_name="Saffre",city=vigala,country='EE',card_number='122')
    #~ yield luc
    andreas = Person.objects.get(name__exact="Arens Andreas")
    annette = Person.objects.get(name__exact="Arens Annette")
    hans = Person.objects.get(name__exact="Altenberg Hans")
    ulrike = Person.objects.get(name__exact="Charlier Ulrike")
    erna = Person.objects.get(name__exact=u"Ärgerlich Erna")
    
    cpas = company(name=u"ÖSHZ Eupen",city=eupen,country='BE')
    yield cpas
    bisa = company(name=u"BISA",city=eupen,country='BE')
    yield bisa 
    bisa_dir = role(company=bisa,person=annette,type=1)
    yield bisa_dir 
    rcycle = company(name=u"R-Cycle Sperrgutsortierzentrum",city=eupen,country='BE')
    yield rcycle
    rcycle_dir = role(company=rcycle,person=andreas,type=1)
    yield rcycle_dir
    yield role(company=rcycle,person=erna,type=2)
    yield role(company=rcycle,person=ulrike,type=4) # IT manager : no contracts
    yield company(name=u"Die neue Alternative V.o.G.",city=eupen,country='BE')
    proaktiv = company(name=u"Pro Aktiv V.o.G.",city=eupen,country='BE')
    yield proaktiv
    proaktiv_dir = role(company=proaktiv,person=hans,type=1)
    yield role(company=proaktiv,person=ulrike,type=4) # IT manager : no contracts
    yield proaktiv_dir
    yield company(name=u"Werkstatt Cardijn V.o.G.",city=eupen,country='BE')
    yield company(name=u"Behindertenstätten Eupen",city=eupen,country='BE')
    yield company(name=u"Beschützende Werkstätte Eupen",city=eupen,country='BE')
    
    luc = Person.objects.get(name__exact="Saffre Luc")
    luc.birth_place = 'Eupen'
    luc.birth_country = be
    luc.save()
    
    ly = person(first_name="Ly",last_name="Rumma",
      city=vigala,country='EE',card_number='123',birth_country=ee,
      birth_date='0000-04-27',
      #~ birth_date=i2d(19680101),birth_date_circa=True,
      #~ newcomer=True,
      gender=Gender.female)
    yield ly
    mari = person(first_name="Mari",last_name="Saffre",
      city=vigala,country='EE',card_number='124',birth_country=ee,
      birth_date=i2d(20020405),
      #~ newcomer=True,
      gender=Gender.female)
    yield mari
    iiris = person(first_name="Iiris",last_name="Saffre",
      city=vigala,country='EE',card_number='125',birth_country=ee,
      birth_date=i2d(20080324),
      #~ newcomer=True,
      gender=Gender.female)
    yield iiris
    
    gerd = person(first_name="Gerd",
      last_name="Xhonneux",city=kettenis,
      name="Xhonneux Gerd",country='BE',gender=Gender.male)
    yield gerd
    yield role(company=cpas,person=gerd,type=4)
    #~ yield link(a=cpas,b=gerd,type=4)
    
    # see :doc:`/blog/2011/1007`
    tatjana = person(
        first_name=u"Tatjana",last_name=u"Kasennova",
        #~ first_name=u"Татьяна",last_name=u"Казеннова",
        # name="Казеннова Татьяна",
        city=kettenis,country='BE', 
        birth_place="Moskau", # birth_country='SUHH',
        newcomer=True,
        gender=Gender.female)
    yield tatjana
    
    from django.core.exceptions import ValidationError
    # a circular reference: bernard is contact for company adg and also has himself as `job_office_contact`
    bernard = Person.objects.get(name__exact="Bodard Bernard")
    adg = company(name=u"Arbeitsamt der D.G.",city=eupen,country='BE')
    update_site_config(job_office=adg)
    yield adg
    adg_dir = role(company=adg,person=bernard,type=1)
    #~ adg_dir = link(a=adg,b=bernard,type=1)
    yield adg_dir
    try:
      bernard.job_office_contact = adg_dir
      bernard.clean()
      bernard.save()
    except ValidationError:
        pass
    else:
        raise Exception("Expected ValidationError")
      
    DIRECTORS = (annette,hans,andreas,bernard)
    
    user = auth.User.objects.get(username='user')
    root = auth.User.objects.get(username='root')
    root.is_spis = True
    root.save()
    user.is_spis = True
    user.save()
    
    USERS = Cycler(root,user)
    
    #~ CLIENTS = Cycler(andreas,annette,hans,ulrike,erna,tatjana)
    count = 0
    for client in Person.objects.all():
        if not client in DIRECTORS:
            count += 1
            if count % 3:
                client.is_active = True
                client.coached_from = settings.LINO.demo_date(-7 * count)
                if count % 6:
                    client.coached_until = settings.LINO.demo_date(-7 * count)
                if count % 2:
                    client.coach1 = USERS.pop()
                else:
                    client.coach2 = USERS.pop()
                    
            elif count % 8:
                client.newcomer = True
            client.clean()
            client.save()
            
    CLIENTS = Cycler(Person.objects.filter(is_active=True,newcomer=False))
    
    #~ oshz = Company.objects.get(name=u"ÖSHZ Eupen")
    
    
    #~ project = Instantiator('projects.Project').build
    note = Instantiator('notes.Note').build
    langk = Instantiator('dsbe.LanguageKnowledge').build

    #~ prj = project(name="Testprojekt",company=oshz)
    #~ yield prj 
    #~ yield note(user=user,project=prj,date=i2d(20091006),subject="Programmierung",company=oshz)
    
    #~ prj = project(name="Testprojekt",company=oshz)
    #~ yield prj 
    #~ yield note(user=user,project=prj,date=i2d(20091007),subject="Anschauen",company=oshz)
    
    
    #~ yield note(user=root,date=settings.LINO.demo_date(),
    yield note(user=root,date=i2d(20091006),
        subject="Programmierung",company=cpas,
        type=1,event_type=1)
    yield note(user=user,date=i2d(20091007),subject="Testen",company=cpas)
    yield note(user=root,date=i2d(20100517),subject="Programmierung",company=cpas)
    yield note(user=user,date=i2d(20100518),subject="Testen",company=cpas)
    yield note(user=user,date=i2d(20110526),subject="Formatted notes",
        company=cpas,body=restify(u"""\
Formatted notes
===============

Lino has now a WYSIWYG text editor. 

Examples
--------

- Enumerations like this list
- Character formatting : **bold**, *italics*, ``typewriter``.
- External `Links <http://lino.saffre-rumma.net/todo.html>`_
- Tables:

  ============ =======
  Package      Version
  ============ =======
  mercurial    1
  apache2      2 
  tinymce      3
  ============ =======
  
Lorem ipsum 
-----------

Lorem ipsum dolor sit amet, consectetur adipisici elit, sed eiusmod tempor incidunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquid ex ea commodi consequat. Quis aute iure reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint obcaecat cupiditat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

Duis autem vel eum iriure dolor in hendrerit in vulputate velit esse molestie consequat, vel illum dolore eu feugiat nulla facilisis at vero eros et accumsan et iusto odio dignissim qui blandit praesent luptatum zzril delenit augue duis dolore te feugait nulla facilisi. Lorem ipsum dolor sit amet, consectetuer adipiscing elit, sed diam nonummy nibh euismod tincidunt ut laoreet dolore magna aliquam erat volutpat.  

"""))
    
    schule = StudyType.objects.get(pk=1)
    uni = StudyType.objects.get(pk=4)
    #~ abi = StudyContent.objects.get(name=u"Abitur")
    abi = u"Abitur"
    study = Instantiator('jobs.Study').build
        
    yield study(person=luc,type=schule,content=abi,
      started='19740901',stopped='19860630')
    yield study(person=gerd,type=schule,content=abi,
      started='19740901',stopped='19860630')

    yield langk(person=luc,language='ger',written='4',spoken='4')
    yield langk(person=gerd,language='ger',written='4',spoken='4')
    yield langk(person=mari,language='ger',written='2',spoken='4')
    yield langk(person=iiris,language='ger',written='0',spoken='4')
    yield langk(person=ly,language='ger',written='2',spoken='1')
    
    yield langk(person=luc,language='fre',written='4',spoken='3')
    yield langk(person=gerd,language='fre',written='4',spoken='3')
    
    yield langk(person=luc,language='eng',written='4',spoken='3')
    yield langk(person=gerd,language='eng',written='4',spoken='3')
    yield langk(person=ly,language='eng',written='3',spoken='3')
    
    yield langk(person=gerd,language='dut',written='3',spoken='3')
    
    yield langk(person=luc,language='est',written='3',spoken='3')
    yield langk(person=ly,language='est',written='4',spoken='4')
    yield langk(person=mari,language='est',written='3',spoken='4')
    yield langk(person=iiris,language='est',written='0',spoken='3')
    
    
    from lino.modlib.isip.models import ContractType, Contract
    
    
    def check_contract(cont):
      
        modified = False
        if cont.person.coached_from is None or cont.person.coached_from > cont.applies_from:
            cont.person.coached_from = cont.applies_from
            modified = True
        if cont.applies_until is None:
            cont.person.coached_until = None 
            modified = True
        else:
            if cont.person.coached_until is None or cont.person.coached_until < cont.applies_until:
                cont.person.coached_until = cont.applies_until
                modified = True
        if modified:
            cont.person.full_clean()
            cont.person.save()
        return cont
    
    CTYPES = Cycler(ContractType.objects.all())
    
    #~ contract = Instantiator(Contract,
      #~ 'type applies_from applies_until',
      #~ user=root).build
    #~ yield contract(1,i2d(20110906),i2d(20111206),person=hans)
    #~ yield contract(1,settings.LINO.demo_date(days=-5*30),
        #~ settings.LINO.demo_date(days=30),person=hans)
        
        
    DURATIONS = Cycler(30,312,480)
    CTYPES = Cycler(ContractType.objects.all())
    
    for i in range(20):
        yield check_contract(Contract(type=CTYPES.pop(),
            applies_from=settings.LINO.demo_date(-100+i*7),
            applies_until=settings.LINO.demo_date(-i*7+DURATIONS.pop()),
            person=CLIENTS.pop(),user=USERS.pop()))
        
    
    jobtype = Instantiator('jobs.JobType','name').build
    art607 = jobtype(u'Sozialwirtschaft = "majorés"')
    yield art607 
    yield jobtype(u'Intern')
    yield jobtype(u'Extern (Öffentl. VoE mit Kostenrückerstattung)')
    yield jobtype(u'Extern (Privat Kostenrückerstattung)')
    #~ yield jobtype(u'VSE')
    yield jobtype(u'Sonstige')
    
    from lino.modlib.jobs.models import ContractType, JobType, Job, Contract, Candidature
    #~ CTYPES = Cycler(*[x for x in ContractType.objects.all()])
    #~ JTYPES = Cycler(*[x for x in JobType.objects.all()])
    CTYPES = Cycler(ContractType.objects.all())
    JTYPES = Cycler(JobType.objects.all())
    
    
    rcycle = mti.insert_child(rcycle,JobProvider)
    yield rcycle 
    bisa = mti.insert_child(bisa,JobProvider)
    yield bisa 
    proaktiv = mti.insert_child(proaktiv,JobProvider)
    yield proaktiv
    
    #~ PROVIDERS = Cycler(*[x for x in JobProvider.objects.all()])
    #~ SECTORS = Cycler(*[x for x in Sector.objects.all()])
    #~ FUNCTIONS = Cycler(*[x for x in Function.objects.all()])
    PROVIDERS = Cycler(JobProvider.objects.all())
    SECTORS = Cycler(Sector.objects.all())
    FUNCTIONS = Cycler(Function.objects.all())
    
    job = Instantiator('jobs.Job','provider type contract_type name').build
    bisajob = job(bisa,art607,1,"bisa")
    yield bisajob
    rcyclejob = job(rcycle,art607,2,"rcycle")
    yield rcyclejob 
    proaktivjob = job(proaktiv,art607,2,"proaktiv",sector=horeca,function=1)
    yield proaktivjob
    
    for i in range(5):
        f = FUNCTIONS.pop()
        yield Job(provider=PROVIDERS.pop(),
          type=JTYPES.pop(),
          contract_type=CTYPES.pop(),
          name=unicode(f),
          sector=SECTORS.pop(),function=f)
    
    #~ JOBS = Cycler(*[x for x in Job.objects.all()])
    JOBS = Cycler(Job.objects.all())
    if False:
        contract = Instantiator('jobs.Contract',
          'type applies_from applies_until job contact',
          user=root).build
        yield contract(1,settings.LINO.demo_date(-30),
            settings.LINO.demo_date(+60),rcyclejob,rcycle_dir,person=hans)
        yield contract(1,settings.LINO.demo_date(-29),
            settings.LINO.demo_date(+61),bisajob,bisa_dir,person=ulrike)
        yield contract(1,settings.LINO.demo_date(-29),None,bisajob,bisa_dir,person=andreas)
        yield contract(1,settings.LINO.demo_date(-28),None,
            rcyclejob,rcycle_dir,person=annette)
        yield contract(1,
            settings.LINO.demo_date(-10),settings.LINO.demo_date(+20),
            bisajob,bisa_dir,person=tatjana)
        yield contract(2,
            settings.LINO.demo_date(20),settings.LINO.demo_date(+120),
            proaktivjob,proaktiv_dir,person=tatjana)
        yield contract(2,
            settings.LINO.demo_date(-120),settings.LINO.demo_date(-20),
            proaktivjob,proaktiv_dir,person=ulrike)
        
    DURATIONS = Cycler(312,480,624)
    contract = Instantiator('jobs.Contract').build
    for i in range(20):
        yield check_contract(Contract(
            type=CTYPES.pop(),
            applies_from=settings.LINO.demo_date(-600+i*40),
            duration=DURATIONS.pop(),
            job=JOBS.pop(),person=CLIENTS.pop(),user=USERS.pop()))

    
    #~ jobrequest = Instantiator('jobs.Candidature','job person date_submitted').build
    #~ yield jobrequest(bisajob,tatjana,settings.LINO.demo_date(-5))
    #~ yield jobrequest(rcyclejob,luc,settings.LINO.demo_date(-30))
    
    for i in range(30):
        yield Candidature(job=JOBS.pop(),person=CLIENTS.pop(),
          date_submitted=settings.LINO.demo_date(-30+i))
    

    
    if False: # this was lino.modlib.links before December 2011
      
        link = Instantiator('links.Link').build
        
        users = User.objects.all()
        
        
        def demo_links(**kw):
            global ROW_COUNTER
            global DATE
            for x in range(1 + (ROW_COUNTER % MAX_LINKS_PER_OWNER)):
                kw.update(date=DATE)
                kw.update(DEMO_LINKS[ROW_COUNTER % len(DEMO_LINKS)])
                kw.update(user=users[ROW_COUNTER % users.count()])
                DATE += ONE_DAY
                ROW_COUNTER += 1
                yield link(**kw)
            
      
        for obj in Person.objects.all():
            for x in demo_links(person=obj):
                yield x
                
        for obj in Company.objects.all():
            for x in demo_links(company=obj):
                yield x
            
    

    #~ from lino.sites.dsbe.models import Course, CourseContent, CourseRequest
    
    courseprovider = Instantiator('dsbe.CourseProvider').build
    #~ oikos = company(name=u"Oikos",city=eupen,country='BE',
      #~ is_courseprovider=True)
    oikos = courseprovider(name=u"Oikos",city=eupen,country='BE')
    yield oikos
    
    #~ kap = company(name=u"KAP",city=eupen,country='BE',
      #~ is_courseprovider=True)
    kap = courseprovider(name=u"KAP",city=eupen,country='BE')
    yield kap
    
    CourseContent = resolve_model('dsbe.CourseContent')
    yield CourseContent(id=1,name=u"Deutsch")
    yield CourseContent(id=2,name=u"Französisch")
    
    creq = Instantiator('dsbe.CourseRequest').build
    yield creq(person=ulrike,content=1,date_submitted=settings.LINO.demo_date(-30))
    yield creq(person=tatjana,content=1,date_submitted=settings.LINO.demo_date(-30))
    yield creq(person=erna,content=2,date_submitted=settings.LINO.demo_date(-30))
    
    offer = Instantiator('dsbe.CourseOffer').build
    course = Instantiator('dsbe.Course').build
    yield offer(provider=oikos,title=u"Deutsch für Anfänger",content=1)
    #~ yield course(offer=1,start_date=i2d(20110110))
    yield course(offer=1,start_date=settings.LINO.demo_date(+30))
    
    yield offer(provider=kap,title=u"Deutsch fur Anfanger",content=1)
    #~ yield course(offer=2,start_date=i2d(20110117))
    yield course(offer=2,start_date=settings.LINO.demo_date(+16))
    
    yield offer(provider=kap,title=u"Français pour débutants",content=2)
    #~ yield course(offer=3,start_date=i2d(20110124))
    yield course(offer=3,start_date=settings.LINO.demo_date(+16))
    
    #~ baker = Properties.objects.get(pk=1)
    #~ baker.save()
    #~ yield baker

    """
    Distribute properties to persons. The distribution should be
    "randomly", but independant of site's language setting.
    """
    pp = Instantiator('properties.PersonProperty',
        'person property value').build
    props = [p for p in Property.objects.order_by('id')]
    i = 0
    L = len(props)
    assert L > 10 
    for p in Person.objects.all():
        for n in range(3):
            if i >= L: 
                i = 0
            prop = props[i]
            i += 1
            yield pp(p,prop,prop.type.default_value)
            
    langk = Instantiator('dsbe.LanguageKnowledge',
        'person:name language written spoken').build
    yield langk(u"Ausdemwald Alfons",'est','1','1')
    yield langk(u"Ausdemwald Alfons",'ger','4','3')
    yield langk(u"Bastiaensen Laurent",'ger','4','3')
    yield langk(u"Bastiaensen Laurent",'fre','4','3')
    yield langk(u"Eierschal Emil",'ger','4','3')
    yield langk(u"Ärgerlich Erna",'ger','4','4')
    
    persongroup = Instantiator('dsbe.PersonGroup','name').build
    #~ pg1 = persongroup(u"Art. 60 § 7",ref_name='1')
    pg1 = persongroup(u"Bilan",ref_name='1')
    yield pg1
    pg2 = persongroup(u"Préformation",ref_name='2')
    yield pg2
    yield persongroup(u"Formation",ref_name='3')
    yield persongroup(u"Recherche active emplois",ref_name='4')
    yield persongroup(u"Travail",ref_name='4bis')
    standby = persongroup(u"Standby",ref_name='9',active=False)
    yield standby
    
    for p in Person.objects.all():
        if p.zip_code == '4700':
            p.languageknowledge_set.create(language_id='ger',native=True)
            p.is_cpas = True
            p.is_active = True
            #~ p.native_language_id = 'ger'
            p.birth_country_id = 'BE'
            p.nationality_id = 'BE'
            p.save()

    for short_code,isocode in (
        ('B', 'BE'),
        ('D', 'DE'),
        ('F', 'FR'),
      ):
      c = Country.objects.get(pk=isocode)
      c.short_code = short_code
      c.save()
      
    p = Person.objects.get(name=u"Ärgerlich Erna")
    p.birth_date = i2d(19800301)
    #~ p.coached_from = i2d(20100301)
    p.coached_from = settings.LINO.demo_date(-7*30)
    p.coached_until = None
    p.coach1 = User.objects.get(username='root')
    p.coach2 = User.objects.get(username='user')
    p.gender = Gender.female 
    p.group = pg1
    p.save()
    
    task = Instantiator('cal.Task').build
    yield task(user=root,start_date=i2d(20110717),
        summary=u"Anrufen Termin",
        owner=p)
    
    p = Person.objects.get(name=u"Eierschal Emil")
    p.birth_date = i2d(19800501)
    #~ p.coached_from = i2d(20100801)
    p.coached_from = settings.LINO.demo_date(-2*30)
    #~ p.coached_until = i2d(20101031)
    p.coached_until = settings.LINO.demo_date(10*30)
    p.coach1 = User.objects.get(username='root')
    #~ p.coach2 = User.objects.get(username='user')
    p.group = pg2
    p.gender = Gender.male
    p.national_id = 'INVALID-45'
    p.save()

    p = Person.objects.get(name=u"Bastiaensen Laurent")
    p.birth_date = i2d(19810601)
    p.coached_from = None
    #~ p.coached_until = i2d(20101031)
    p.coached_until = settings.LINO.demo_date(-2*30)
    #~ p.unavailable_until = i2d(20110712)
    p.unavailable_until = settings.LINO.demo_date(2*30)
    p.coach1 = User.objects.get(username='root')
    p.coach2 = User.objects.get(username='user')
    p.group = pg1
    p.gender = Gender.male
    p.national_id = '931229 211-83'
    p.save()

    p = Person.objects.get(name=u"Chantraine Marc")
    p.birth_date = i2d(19500301)
    p.coached_from = settings.LINO.demo_date(10)
    p.coached_until = None
    p.coach1 = User.objects.get(username='root')
    #~ p.coach2 = User.objects.get(username='user')
    p.group = pg2
    p.gender = Gender.male
    p.save()

    p = Person.objects.get(name=u"Charlier Ulrike")
    p.birth_date = i2d(19600401)
    p.coached_from = settings.LINO.demo_date(-3*30)
    p.coached_until = None
    p.coach1 = User.objects.get(username='user')
    #~ p.coach2 = User.objects.get(username='user')
    p.gender = Gender.female
    p.group = pg1
    p.save()


    p = Person.objects.get(name=u"Collard Charlotte")
    p.birth_date = i2d(19800401)
    p.coached_from = settings.LINO.demo_date(-6*30)
    p.coached_until = None
    p.coach1 = User.objects.get(username='root')
    #~ p.coach2 = User.objects.get(username='user')
    p.gender = Gender.female
    p.group = standby
    p.save()



    #~ etype = Instantiator('cal.EventType','name').build
    #~ yield etype("interner Termin")
    #~ yield etype("Termin beim Klienten")
    #~ yield etype("Termin beim Arbeitgeber")
    
    event = Instantiator('cal.Event',
      'type start_date project summary',
      user=root).build
    #~ yield event(1,i2d(20100727),hans,u"Stand der Dinge")
    #~ yield event(2,i2d(20100727),annette,u"Problem Kühlschrank")
    #~ yield event(3,i2d(20100727),andreas,u"Mein dritter Termin")
    yield event(1,settings.LINO.demo_date(+1),hans,u"Stand der Dinge")
    yield event(2,settings.LINO.demo_date(+1),annette,u"Problem Kühlschrank")
    yield event(3,settings.LINO.demo_date(+2),andreas,u"Mein dritter Termin")

    i = dsbe.Person.objects.order_by('name').__iter__()
    p = i.next()
    offset = 0
    for f in jobs.Function.objects.all():
        yield jobs.Candidature(person=p,function=f,sector=f.sector,
            #~ date_submitted=i2d(20111019))
            date_submitted=settings.LINO.demo_date(offset))
        p = i.next()
        offset -= 1
