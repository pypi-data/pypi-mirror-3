# -*- coding: UTF-8 -*-
## Copyright 2009-2012 Luc Saffre
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

import logging
logger = logging.getLogger(__name__)

import os
import sys
import cgi
import time
import datetime
#import traceback
import cPickle as pickle
from urllib import urlencode
import codecs

#~ from lxml import etree


#~ import Cheetah
from Cheetah.Template import Template as CheetahTemplate

from django import http
from django.db import models
from django.db import IntegrityError
from django.conf import settings
from django.http import HttpResponse, Http404
from django import http
from django.core import exceptions
from django.utils import functional
from django.utils.encoding import force_unicode
#~ from django.utils.functional import Promise

from django.template.loader import get_template
from django.template import RequestContext

from django.utils.translation import ugettext as _
from django.utils import simplejson as json
from django.utils import translation

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.conf.urls.defaults import patterns, url, include


import lino
from lino.ui.extjs3 import ext_elems
from lino.ui.extjs3 import ext_store
from lino.ui.extjs3 import ext_windows
#~ from . import ext_viewport
#~ from . import ext_requests
from lino.ui import requests as ext_requests

#~ from lino.ui import store as ext_store
from lino import dd
from lino.core import actions #, layouts #, commands
#~ from lino.core.actions import action2str
from lino.core import table
from lino.core import layouts
from lino.utils import tables
#~ from lino.utils.xmlgen import xhtml as xhg
from lino.core import fields
from lino.ui import base
from lino.core import actors
from lino.core.modeltools import makedirs_if_missing
from lino.core.modeltools import full_model_name
from lino.core.modeltools import is_devserver
    
from lino.utils import dblogger
from lino.utils import ucsv
from lino.utils import choosers
from lino.utils import babel
from lino.utils import choicelists
from lino.core import menus
from lino.utils import jsgen
from lino.utils import isiterable
from lino.utils.config import find_config_file
from lino.utils.jsgen import py2js, js_code, id2js
from lino.utils.xmlgen import html as xghtml

from lino.utils.jscompressor import JSCompressor
if False:
    jscompress = JSCompressor().compress
else:    
    def jscompress(s): return s
      
from lino.mixins import printable

from lino.core.modeltools import app_labels

from lino.utils.babel import LANGUAGE_CHOICES

from lino.utils.choicelists import DoYouLike, HowWell
STRENGTH_CHOICES = DoYouLike.get_choices()
KNOWLEDGE_CHOICES = HowWell.get_choices()

from lino.core.modeltools import resolve_model, obj2str, obj2unicode
#~ from lino.ui.extjs.ext_windows import WindowConfig # 20100316 backwards-compat window_confics.pck 

if settings.LINO.user_model:
    #~ User = resolve_model(settings.LINO.user_model)
    from lino.modlib.users import models as users

MAX_ROW_COUNT = 300


    

class HtmlRenderer(object):
    """
    Deserves more documentation.
    """
    def __init__(self,ui):
        self.ui = ui
        
    def href(self,url,text):
        return '<a href="%s">%s</a>' % (url,text)
        
    def href_button(self,url,text,title=None):
        if title:
            return '[<a href="%s" title="%s">%s</a>]' % (
                url,cgi.escape(unicode(title)),text)
        return '[<a href="%s">%s</a>]' % (url,text)
        
    def quick_add_buttons(self,ar):
        """
        Returns a HTML chunk that displays "quick add buttons"
        for the given :class:`action request <lino.core.table.TableRequest>`:
        a button  :guilabel:`[New]` followed possibly 
        (if the request has rows) by a :guilabel:`[Show last]` 
        and a :guilabel:`[Show all]` button.
        
        See also :doc:`/tickets/56`.
        
        """
        s = ''
        #~ params = dict(base_params=ar.request2kw(self))
        params = None
        after_show = ar.get_status(self)
        
        #~ params = ar.get_status(self)
        #~ after_show = dict()
        #~ a = ar.actor.get_action('insert')
        a = ar.actor.insert_action
        if a is not None:
            if a.get_action_permission(ar.get_user(),None,None):
                elem = ar.create_instance()
                after_show.update(data_record=elem2rec_insert(ar,ar.ah,elem))
                #~ after_show.update(record_id=-99999)
                # see tickets/56
                s += self.action_href_js(a,after_show,_("New"))
                after_show = ar.get_status(self)
        n = ar.get_total_count()
        #~ print 20120702, [o for o in ar]
        if n > 0:
            obj = ar.data_iterator[n-1]
            after_show.update(record_id=obj.pk)
            s += ' ' + self.action_href_js(
                ar.ah.actor.detail_action,after_show,_("Show Last"))
            #~ s += ' ' + self.href_to_request(ar,"[%s]" % unicode(_("Show All")))
            s += ' ' + self.href_to_request(ar,_("Show All"))
        #~ return '<p>%s</p>' % s
        return s
                
    def quick_upload_buttons(self,rr):
        """
        Returns a HTML chunk that displays "quick upload buttons":
        either one button :guilabel:`[Upload]` 
        (if the given :class:`TableTequest <lino.core.table.TableRequest>`
        has no rows)
        or two buttons :guilabel:`[Show]` and :guilabel:`[Edit]` 
        if it has one row.
        
        See also :doc:`/tickets/56`.
        
        """
        #~ params = dict(base_params=rr.request2kw(self))
        #~ params = rr.get_status(self)
        params = None
        after_show = rr.get_status(self)
        #~ after_show = dict(base_params=rr.get_status(self))
        #~ after_show = dict()
        if rr.get_total_count() == 0:
            #~ a = rr.actor.get_action('insert')
            a = rr.actor.insert_action
            if a is not None:
                elem = rr.create_instance()
                after_show.update(data_record=elem2rec_insert(rr,rr.ah,elem))
                #~ after_show.update(record_id=-99999)
                # see tickets/56
                return self.action_href_js(a,after_show,_("Upload"))
        if rr.get_total_count() == 1:
            obj = rr.data_iterator[0]
            s = ''
            s += ' [<a href="%s" target="_blank">show</a>]' % (self.ui.media_url(obj.file.name))
            if True:
                after_show.update(record_id=obj.pk)
                s += ' ' + self.action_href_js(rr.ah.actor.detail_action,after_show,_("Edit"))
            else:
                after_show.update(record_id=obj.pk)
                s += ' ' + self.action_href_http(rr.ah.actor.detail_action,_("Edit"),params,after_show)
            return s
        return '[?!]'

  
#~ class PdfRenderer(HtmlRenderer):
    #~ """
    #~ Deserves more documentation.
    #~ """
    #~ def href_to_request(self,rr,text=None):
        #~ return text or ("<b>%s</b>" % cgi.escape(force_unicode(rr.label)))
    #~ def href_to(self,obj,text=None):
        #~ text = text or cgi.escape(force_unicode(obj))
        #~ return "<b>%s</b>" % text
    #~ def instance_handler(self,obj):
        #~ return None
    #~ def request_handler(self,ar,*args,**kw):
        #~ return ''
        

#~ class ExtRendererPermalink(HtmlRenderer):
    #~ """
    #~ Deserves more documentation.
    #~ """
    #~ def href_to_request(self,rr,text=None):
        #~ """
        #~ Returns a HTML chunk with a clickable link to 
        #~ the given :class:`TableTequest <lino.core.table.TableRequest>`.
        #~ """
        #~ return self.href(
            #~ self.get_request_url(rr),
            #~ text or cgi.escape(force_unicode(rr.label)))
    #~ def href_to(self,obj,text=None):
        #~ """
        #~ Returns a HTML chunk with a clickable link to 
        #~ the given model instance.
        #~ """
        #~ return self.href(
            #~ self.get_detail_url(obj),
            #~ text or cgi.escape(force_unicode(obj)))
            
class ExtRenderer(HtmlRenderer):
    """
    Deserves more documentation.
    """
    def href_to(self,obj,text=None):
        h = self.instance_handler(obj)
        if h is None:
            return cgi.escape(force_unicode(obj))
        url = self.js2url(h)
        return self.href(url,text or cgi.escape(force_unicode(obj)))

    def py2js_converter(self,v):
        """
        Additional converting logic for serializing Python values to json.
        """
        if v is LANGUAGE_CHOICES:
            return js_code('LANGUAGE_CHOICES')
        if v is STRENGTH_CHOICES:
            return js_code('STRENGTH_CHOICES')
        if v is KNOWLEDGE_CHOICES:
            return js_code('KNOWLEDGE_CHOICES')
        if isinstance(v,choicelists.Choice):
            """
            This is special. We don't render the text but the value. 
            """
            return v.value
        #~ if isinstance(v,babel.BabelText):
            #~ return unicode(v)
        #~ if isinstance(v,Promise):
            #~ return unicode(v)
        if isinstance(v,dd.Model):
            return v.pk
        if isinstance(v,Exception):
            return unicode(v)
        if isinstance(v,menus.Menu):
            if v.parent is None:
                return v.items
                #kw.update(region='north',height=27,items=v.items)
                #return py2js(kw)
            return dict(text=prepare_label(v),menu=dict(items=v.items))
        if isinstance(v,menus.MenuItem):
            if v.params is not None:
                ar = v.action.actor.request(self.ui,None,v.action,**v.params)
                return handler_item(v,self.request_handler(ar),v.action.help_text)
                #~ return dict(text=prepare_label(v),handler=js_code(handler))
            if v.action:
                if True:
                    #~ handler = self.action_call(v.action,params=v.params)
                    return handler_item(v,self.action_call(None,v.action),v.action.help_text)
                    #~ handler = "function(){%s}" % self.action_call(
                        #~ v.action,None,v.params)
                    #~ return dict(text=prepare_label(v),handler=js_code(handler))
                else:
                    url = self.action_url_http(v.action)
            #~ elif v.params is not None:
                #~ ar = v.action.actor.request(self,None,v.action,**v.params)
                #~ url = self.get_request_url(ar)
            elif v.href is not None:
                url = v.href
            elif v.request is not None:
                url = self.get_request_url(v.request)
            elif v.instance is not None:
                h = self.instance_handler(v.instance)
                assert h is not None
                return handler_item(v,h,None)
                #~ handler = "function(){%s}" % self.instance_handler(v.instance)
                #~ return dict(text=prepare_label(v),handler=js_code(handler))
              
                #~ url = self.get_detail_url(v.instance,an='detail')
                #~ url = self.get_detail_url(v.instance)
            else:
                # a separator
                #~ return dict(text=v.label)
                return v.label
                #~ url = self.build_url('api',v.action.actor.app_label,v.action.actor.__name__,fmt=v.action.name)
            if v.parent.parent is None:
                # special case for href items in main menubar
                return dict(
                  xtype='button',text=prepare_label(v),
                  #~ handler=js_code("function() { window.location='%s'; }" % url))
                  handler=js_code("function() { location.replace('%s'); }" % url))
            return dict(text=prepare_label(v),href=url)
        return v
        
    def action_call(self,request,a,after_show={}):
        if a.opens_a_window:
            if request and request.subst_user:
                after_show[ext_requests.URL_PARAM_SUBST_USER] = request.subst_user
            if isinstance(a,actions.ShowEmptyTable):
                after_show.update(record_id=-99998)
            if after_show:
                return "Lino.%s.run(%s)" % (a,py2js(after_show))
            return "Lino.%s.run()" % a
        return "?"

    def js2url(self,js):
        js = cgi.escape(js)
        js = js.replace('"','&quot;')
        return 'javascript:' + js
        
    #~ def action_url_js(self,a,after_show):
        #~ return self.js2url(self.action_call(a,after_show))

    def action_href_js(self,a,after_show={},label=None):
        """
        Return a HTML chunk for a button that will execute this 
        action using a *Javascript* link to this action.
        """
        label = cgi.escape(force_unicode(label or a.get_button_label()))
        #~ url = self.action_url_js(a,after_show)
        url = self.js2url(self.action_call(None,a,after_show))
        return self.href_button(url,label,a.help_text)
        
    def row_action_button(self,obj,ar,a):
        """
        Return a HTML fragment that displays a button-like link 
        which runs the action when clicked.
        """
        if a.opens_a_window:
            #~ params = None
            after_show = ar.get_status(self)
            after_show.update(record_id=obj.pk)
            return self.action_href_js(a,after_show,a.label)
        else:
            label = cgi.escape(unicode(a.label))
            #~ url = self.js2url('Lino.%s(%s,Lino.%s_window.main_item)' % (a,py2js(obj.pk),ar.action))
            #~ print 20120624, ar.requesting_panel
            #~ status = ar.get_status(self)
            # call the function generated by js_render_workflow_action():
            url = self.js2url(
                'Lino.%s(%r,%s,Lino.%s)' % (
                    a,str(ar.requesting_panel),
                    py2js(obj.pk),ar.action))
            #~ url = self.js2url('Lino.row_action(%s,%s)' % (py2js(obj.pk),py2js(a.name)))
            return self.href_button(url,label,a.help_text)
        
    def instance_handler(self,obj):
        #~ a = obj.__class__._lino_default_table.get_action('detail')
        a = obj.__class__._lino_default_table.detail_action
        if a is not None:
            #~ raise Exception("No detail action for %s" % obj.__class__._lino_default_table)
            return self.action_call(None,a,dict(record_id=obj.pk))
        
    def request_handler(self,ar,*args,**kw):
        #~ bp = rr.request2kw(self.ui,**kw)
        st = ar.get_status(self.ui,**kw)
        return self.action_call(ar.request,ar.action,after_show=st)
        
    def href_to_request(self,rr,text=None):
        url = self.js2url(self.request_handler(rr))
        #~ if 'Lino.pcsw.MyPersonsByGroup' in url:
        #~ print 20120618, url
        return self.href(url,text or cgi.escape(force_unicode(rr.label)))
        #~ return self.href_button(url,text or cgi.escape(force_unicode(rr.label)))
            
    def action_href_http(self,a,label=None,**params):
        """
        Return a HTML chunk for a button that will execute 
        this action using a *HTTP* link to this action.
        """
        label = cgi.escape(force_unicode(label or a.get_button_label()))
        return '[<a href="%s">%s</a>]' % (self.action_url_http(a,**params),label)
        
    #~ def get_action_url(self,action,*args,**kw):
    def action_url_http(self,action,*args,**kw):
        #~ if not action is action.actor.default_action:
        if action != action.actor.default_action:
            kw.update(an=action.name)
        return self.build_url("api",action.actor.app_label,action.actor.__name__,*args,**kw)
            
    def get_actor_url(self,actor,*args,**kw):
        return self.build_url("api",actor.app_label,actor.__name__,*args,**kw)
        
    def get_request_url(self,ar,*args,**kw):
        """
        Called from ActionRequest.absolute_url() used in Team.eml.html
        
        http://127.0.0.1:8000/api/cal/MyPendingInvitations?base_params=%7B%7D
        http://127.0.0.1:8000/api/cal/MyPendingInvitations
        
        """
        kw = ar.get_status(self,**kw)
        if not kw['base_params']:
            del kw['base_params']
        #~ kw = self.request2kw(rr,**kw)
        return ar.ui.build_url('api',ar.actor.app_label,ar.actor.__name__,*args,**kw)
        
    def get_detail_url(self,obj,*args,**kw):
        #~ rpt = obj._lino_default_table
        #~ return self.build_url('api',rpt.app_label,rpt.__name__,str(obj.pk),*args,**kw)
        return self.build_url('api',obj._meta.app_label,obj.__class__.__name__,str(obj.pk),*args,**kw)
        
    #~ def request_href_js(self,rr,text=None):
        #~ url = self.request_handler(rr)
        #~ return self.href(url,text or cgi.escape(force_unicode(rr.label)))
        
    
            





class HttpResponseDeleted(HttpResponse):
    status_code = 204
    
def prepare_label(mi):
    return mi.label
    """
    The original idea doesn't work any more with lazy translation.
    See :doc:`/blog/2011/1112`
    """
    #~ label = unicode(mi.label) # trigger translation
    #~ n = label.find(mi.HOTKEY_MARKER)
    #~ if n != -1:
        #~ label = label.replace(mi.HOTKEY_MARKER,'')
        #~ #label=label[:n] + '<u>' + label[n] + '</u>' + label[n+1:]
    #~ return label
    
def handler_item(mi,handler,help_text):
    handler = "function(){%s}" % handler
    #~ d = dict(text=prepare_label(mi),handler=js_code(handler),tooltip="Foo")
    d = dict(text=prepare_label(mi),handler=js_code(handler))
    if settings.LINO.use_quicktips and help_text:
        d.update(listeners=dict(render=js_code(
          "Lino.quicktip_renderer(%s,%s)" % (py2js('Foo'),py2js(help_text)))
        ))
    
    return d


#~ def element_name(elem):
    #~ return u"%s (#%s in %s.%s)" % (elem,elem.pk,elem._meta.app_label,elem.__class__.__name__)


def parse_bool(s):
    return s == 'true'
    
def parse_int(s,default=None):
    if s is None: return None
    return int(s)

def json_response_kw(**kw):
    return json_response(kw)
    
def json_response(x,content_type='application/json'):
    #~ logger.info("20120208")
    #s = simplejson.dumps(kw,default=unicode)
    #return HttpResponse(s, mimetype='text/html')
    s = py2js(x)
    #~ logger.info("20120208 json_response(%r)\n--> %s",x,s)
    #~ logger.debug("json_response() -> %r", s)
    """
    Theroretically we should send content_type='application/json'
    (http://stackoverflow.com/questions/477816/the-right-json-content-type),
    but "File uploads are not performed using Ajax submission, 
    that is they are not performed using XMLHttpRequests. (...) 
    If the server is using JSON to send the return object, then 
    the Content-Type header must be set to "text/html" in order 
    to tell the browser to insert the text unchanged into the 
    document body." 
    (http://docs.sencha.com/ext-js/3-4/#!/api/Ext.form.BasicForm)
    See 20120209.
    """
    return HttpResponse(s, content_type=content_type)
    #~ return HttpResponse(s, content_type='text/html')
    #~ return HttpResponse(s, content_type='application/json')
    #~ return HttpResponse(s, content_type='text/json')
    



def elem2rec1(ar,rh,elem,**rec):
    rec.update(data=rh.store.row2dict(ar,elem))
    return rec

#~ def elem2rec_empty(ar,ah,**rec):
    #~ rec.update(data=dict())
    #~ rec.update(title='Empty detail')
    #~ return rec
    
def elem2rec_insert(ar,ah,elem):
    """
    Returns a dict of this record, designed for usage by an InsertWindow.
    """
    rec = elem2rec1(ar,ah,elem)
    #~ rec.update(title=_("Insert into %s...") % ar.get_title())
    rec.update(title=ar.get_action_title())
    rec.update(phantom=True)
    #~ rec.update(id=elem.pk) or -99999)
    return rec

def elem2rec_empty(ar,ah,elem,**rec):
    """
    Returns a dict of this record, designed for usage by an EmptyTable.
    """
    #~ rec.update(data=rh.store.row2dict(ar,elem))
    rec.update(data=elem._data)
    #~ rec = elem2rec1(ar,ah,elem)
    #~ rec.update(title=_("Insert into %s...") % ar.get_title())
    rec.update(title=ar.get_action_title())
    rec.update(id=-99998)
    #~ rec.update(id=elem.pk) or -99999)
    return rec

def elem2rec_detailed(ar,elem,**rec):
    """
    Adds additional information for this record, used only by detail views.
    
    The "navigation information" is a set of pointers to the next, previous, 
    first and last record relative to this record in this report. 
    (This information can be relatively expensive for records that are towards 
    the end of the report. 
    See :doc:`/blog/2010/0716`,
    :doc:`/blog/2010/0721`,
    :doc:`/blog/2010/1116`,
    :doc:`/blog/2010/1207`.)
    
    recno 0 means "the requested element exists but is not contained in the requested queryset".
    This can happen after changing the quick filter (search_change) of a detail view.
    
    """
    rh = ar.ah
    rec = elem2rec1(ar,rh,elem,**rec)
    if ar.actor.hide_top_toolbar:
        rec.update(title=unicode(elem))
    else:
        rec.update(title=ar.get_title() + u" » " + unicode(elem))
    #~ rec.update(title=ar.actor.get_detail_title(ar,elem))
    #~ rec.update(title=rh.actor.model._meta.verbose_name + u"«%s»" % unicode(elem))
    #~ rec.update(title=unicode(elem))
    rec.update(id=elem.pk)
    #~ if rh.actor.disable_delete:
    #~ rec.update(disabled_actions=rh.actor.disabled_actions(ar,elem))
    rec.update(disable_delete=rh.actor.disable_delete(elem,ar))
    if rh.actor.show_detail_navigator:
        first = None
        prev = None
        next = None
        last = None
        #~ ar = ext_requests.ViewReportRequest(request,rh,rh.actor.default_action)
        recno = 0
        #~ if len(ar.data_iterator) > 0:
        LEN = ar.get_total_count()
        if LEN > 0:
            if True:
                # this algorithm is clearly quicker on reports with a few thousand Persons
                id_list = list(ar.data_iterator.values_list('pk',flat=True))
                """
                Uncommented the following assert because it failed in certain circumstances 
                (see :doc:`/blog/2011/1220`)
                """
                #~ assert len(id_list) == ar.total_count, \
                    #~ "len(id_list) is %d while ar.total_count is %d" % (len(id_list),ar.total_count)
                #~ print 20111220, id_list
                first = id_list[0]
                last = id_list[-1]
                try:
                    i = id_list.index(elem.pk)
                except ValueError:
                    pass
                else:
                    recno = i + 1
                    if i > 0:
                        #~ prev = ar.queryset[i-1]
                        prev = id_list[i-1]
                    if i < len(id_list) - 1:
                        #~ next = ar.queryset[i+1]
                        next = id_list[i+1]
            else:
                first = ar.queryset[0]
                last = ar.queryset.reverse()[0]
                if ar.get_total_count() > 200:
                    #~ TODO: check performance
                    pass
                g = enumerate(ar.queryset) # a generator
                try:
                    while True:
                        index, item = g.next()
                        if item == elem:
                            if index > 0:
                                prev = ar.queryset[index-1]
                            recno = index + 1
                            index,next = g.next()
                            break
                except StopIteration:
                    pass
                if first is not None: first = first.pk
                if last is not None: last = last.pk
                if prev is not None: prev = prev.pk
                if next is not None: next = next.pk
        rec.update(navinfo=dict(
            first=first,prev=prev,next=next,last=last,recno=recno,
            message=_("Row %(rowid)d of %(rowcount)d") % dict(
              rowid=recno,rowcount=LEN)))
    return rec
            
    

  
    
class ExtUI(base.UI):
    """The central instance of Lino's ExtJS3 User Interface.
    """
    _handle_attr_name = '_extjs3_handle'
    #~ _response = None
    name = 'extjs3'
    verbose_name = "ExtJS with Windows"
    #~ Panel = ext_elems.Panel
    
    
    #~ USE_WINDOWS = False  # If you change this, then change also Lino.USE_WINDOWS in lino.js

    #~ def __init__(self,*args,**kw):
    def __init__(self):
        #~ raise Exception("20120614")
        #~ self.pdf_renderer = PdfRenderer(self) # 20120624
        self.ext_renderer = ExtRenderer(self)
        self.reserved_names = [getattr(ext_requests,n) for n in ext_requests.URL_PARAMS]
        jsgen.register_converter(self.ext_renderer.py2js_converter)
        #~ self.window_configs = {}
        #~ if os.path.exists(self.window_configs_file):
            #~ logger.info("Loading %s...",self.window_configs_file)
            #~ wc = pickle.load(open(self.window_configs_file,"rU"))
            #~ #logger.debug("  -> %r",wc)
            #~ if type(wc) is dict:
                #~ self.window_configs = wc
        #~ else:
            #~ logger.warning("window_configs_file %s not found",self.window_configs_file)
            
        #~ base.UI.__init__(self,*args,**kw) # will create a.window_wrapper for all actions
        base.UI.__init__(self) 
        
        #~ self.welcome_template = get_template('welcome.html')
        
        #~ from django.template.loader import find_template
        #~ source, origin = find_template('welcome.html')
        #~ print source, origin
        
        if False:
            fn = find_config_file('welcome.html')
            logger.info("Using welcome template %s",fn)
            self.welcome_template = CheetahTemplate(file(fn).read())
        
        #~ self.build_site_cache()
            
        #~ self.generate_linolib_messages()
        
    def create_layout_element(self,lh,name,**kw):
        if False: 
            de = lh.get_data_elem(name)
        else:
            try:
                de = lh.get_data_elem(name)
            except Exception, e:
                de = None
                name += " (" + str(e) + ")"
            
        #~ if isinstance(de,fields.FieldSet):
            #~ # return lh.desc2elem(ext_elems.FieldSetPanel,name,de.desc)
            #~ return lh.desc2elem(name,de.desc,**kw)
            
        #~ if isinstance(de,fields.NullField):
            #~ return None
            
        if isinstance(de,fields.DummyField):
            return None
        if isinstance(de,fields.Constant):
            return ext_elems.ConstantElement(lh,de,**kw)
            
        if isinstance(de,fields.RemoteField):
            return self.create_field_element(lh,de,**kw)
        if isinstance(de,models.Field):
            if isinstance(de,(babel.BabelCharField,babel.BabelTextField)):
                if len(babel.BABEL_LANGS) > 0:
                    elems = [ self.create_field_element(lh,de,**kw) ]
                    for lang in babel.BABEL_LANGS:
                        bf = lh.get_data_elem(name+'_'+lang)
                        elems.append(self.create_field_element(lh,bf,**kw))
                    return elems
            return self.create_field_element(lh,de,**kw)
            
        if isinstance(de,fields.LinkedForeignKey):
            de.primary_key = False # for ext_store.Store()
            lh.add_store_field(de)
            return ext_elems.LinkedForeignKeyElement(lh,de,**kw)
            
        if isinstance(de,generic.GenericForeignKey):
            # create a horizontal panel with 2 comboboxes
            #~ print 20111123, name,de.ct_field + ' ' + de.fk_field
            #~ return lh.desc2elem(panelclass,name,de.ct_field + ' ' + de.fk_field,**kw)
            #~ return ext_elems.GenericForeignKeyField(lh,name,de,**kw)
            de.primary_key = False # for ext_store.Store()
            lh.add_store_field(de)
            return ext_elems.GenericForeignKeyElement(lh,de,**kw)
            
        #~ if isinstance(de,type) and issubclass(de,dd.Table):
        if isinstance(de,type) and issubclass(de,tables.AbstractTable):
            kw.update(master_panel=js_code("this"))
            if isinstance(lh.layout,layouts.FormLayout):
                """a Table in a DetailWindow"""
                kw.update(tools=[
                  js_code("Lino.show_in_own_window_button(Lino.%s)" % de.default_action)
                  #~ js_code("Lino.report_window_button(Lino.%s)" % de.default_action)
                  #~ js_code("Lino.report_window_button(ww,Lino.%s)" % de.default_action)
                ])
                if de.slave_grid_format == 'grid':
                    if not de.parameters:
                        kw.update(hide_top_toolbar=True)
                    e = ext_elems.GridElement(lh,name,de,**kw)
                    return e
                elif de.slave_grid_format == 'summary':
                    # a Table in a DetailWindow, displayed as a summary in a HtmlBox 
                    o = dict(drop_zone="FooBar")
                    #~ a = de.get_action('insert')
                    a = de.insert_action
                    if a is not None:
                        kw.update(ls_insert_handler=js_code("Lino.%s" % a))
                        kw.update(ls_bbar_actions=[self.a2btn(a)])
                    #~ else:
                        #~ print 20120619, de, 'has no insert_action'
                    field = fields.HtmlBox(verbose_name=de.label,**o)
                    field.name = de.__name__
                    field._return_type_for_method = de.slave_as_summary_meth(self,'<br>')
                    lh.add_store_field(field)
                    e = ext_elems.HtmlBoxElement(lh,field,**kw)
                    return e
                    
                elif de.slave_grid_format == 'html':
                    #~ a = de.get_action('insert')
                    a = de.insert_action
                    if a is not None:
                        kw.update(ls_insert_handler=js_code("Lino.%s" % a))
                        kw.update(ls_bbar_actions=[self.a2btn(a)])
                    field = fields.HtmlBox(verbose_name=de.label)
                    field.name = de.__name__
                    field._return_type_for_method = de.slave_as_html_meth(self)
                    lh.add_store_field(field)
                    e = ext_elems.HtmlBoxElement(lh,field,**kw)
                    return e
            else:
                #~ field = fields.TextField(verbose_name=de.label)
                field = fields.HtmlBox(verbose_name=de.label)
                field.name = de.__name__
                field._return_type_for_method = de.slave_as_summary_meth(self,', ')
                lh.add_store_field(field)
                e = ext_elems.HtmlBoxElement(lh,field,**kw)
                return e
                
        if isinstance(de,fields.VirtualField):
            return self.create_vurt_element(lh,name,de,**kw)
            
        if callable(de):
            rt = getattr(de,'return_type',None)
            if rt is not None:
                return self.create_meth_element(lh,name,de,rt,**kw)
                
        if not name in ('__str__','__unicode__','name','label'):
            value = getattr(lh,name,None)
            if value is not None:
                return value
                
        if hasattr(lh,'rh'):
            msg = "Unknown element %r referred in layout %s of %s." % (
                name,lh.layout,lh.rh.actor)
            l = [de.name for de in lh.rh.actor.wildcard_data_elems()]
            model = getattr(lh.rh.actor,'model',None) # VirtualTables don't have a model
            if getattr(model,'_lino_slaves',None):
                l += [str(rpt) for rpt in model._lino_slaves.values()]
            msg += " Possible names are %s." % ', '.join(l)
        else:
            msg = "Unknown element %r referred in layout %s." % (
                name,lh.layout)
            msg += "Cannot handle %r" % de
        raise KeyError(msg)
        

    def create_vurt_element(self,lh,name,vf,**kw):
        #~ assert vf.get.func_code.co_argcount == 2, (name, vf.get.func_code.co_varnames)
        e = self.create_field_element(lh,vf,**kw)
        if not vf.is_enabled(lh):
            e.editable = False
        return e
        
    def create_meth_element(self,lh,name,meth,rt,**kw):
        #~ if hasattr(rt,'_return_type_for_method'):
            #~ raise Exception(
              #~ "%s.%s : %r has already an attribute '_return_type_for_method'" % (
                #~ lh,name,rt))
        rt.name = name
        rt._return_type_for_method = meth
        if meth.func_code.co_argcount < 2:
            raise Exception("Method %s has %d arguments (must have at least 2)" % (meth,meth.func_code.co_argcount))
            #~ , (name, meth.func_code.co_varnames)
        #~ kw.update(editable=False)
        e = self.create_field_element(lh,rt,**kw)
        #~ if lh.rh.actor.actor_id == 'contacts.Persons':
            #~ print 'ext_ui.py create_meth_element',name,'-->',e
        #~ if name == 'preview':
            #~ print 20110714, 'ext_ui.create_meth_element', meth, repr(e)
        return e
        #~ e = lh.main_class.field2elem(lh,return_type,**kw)
        #~ assert e.field is not None,"e.field is None for %s.%s" % (lh.layout,name)
        #~ lh._store_fields.append(e.field)
        #~ return e
            
        #~ if rt is None:
            #~ rt = models.TextField()
            
        #~ e = ext_elems.MethodElement(lh,name,meth,rt,**kw)
        #~ assert e.field is not None,"e.field is None for %s.%s" % (lh.layout,name)
        #~ lh._store_fields.append(e.field)
        #~ return e
          
    def create_field_element(self,lh,field,**kw):
        #~ e = lh.main_class.field2elem(lh,field,**kw)
        e = ext_elems.field2elem(lh,field,**kw)
        assert e.field is not None,"e.field is None for %s.%s" % (lh.layout,name)
        lh.add_store_field(e.field)
        return e
        #return FieldElement(self,field,**kw)
        

    #~ def save_window_config(self,a,wc):
        #~ self.window_configs[str(a)] = wc
        #~ #a.window_wrapper.config.update(wc=wc)
        #~ a.window_wrapper.update_config(wc)
        #~ f = open(self.window_configs_file,'wb')
        #~ pickle.dump(self.window_configs,f)
        #~ f.close()
        #~ logger.debug("save_window_config(%r) -> %s",wc,a)
        #~ self.build_site_cache()
        #~ lh = actors.get_actor(name).get_handle(self)
        #~ if lh is not None:
            #~ lh.window_wrapper.try_apply_window_config(wc)
        #~ self._response = None

    #~ def load_window_config(self,action,**kw):
        #~ wc = self.window_configs.get(str(action),None)
        #~ if wc is not None:
            #~ logger.debug("load_window_config(%r) -> %s",str(action),wc)
            #~ for n in ('x','y','width','height'):
                #~ if wc.get(n,0) is None:
                    #~ del wc[n]
                    #~ #raise Exception('invalid window configuration %r' % wc)
            #~ kw.update(**wc)
        #~ return kw

  
    def get_urls(self):
        rx = '^'
        urlpatterns = patterns('',
            (rx+'$', self.index_view),
            #~ (rx+r'grid_action/(?P<app_label>\w+)/(?P<rptname>\w+)/(?P<grid_action>\w+)$', self.json_report_view),
            (rx+r'grid_config/(?P<app_label>\w+)/(?P<actor>\w+)$', self.grid_config_view),
            #~ (rx+r'detail_config/(?P<app_label>\w+)/(?P<actor>\w+)$', self.detail_config_view),
            (rx+r'api/(?P<app_label>\w+)/(?P<actor>\w+)$', self.api_list_view),
            (rx+r'api/(?P<app_label>\w+)/(?P<actor>\w+)/(?P<pk>.+)$', self.api_element_view),
            (rx+r'restful/(?P<app_label>\w+)/(?P<actor>\w+)$', self.restful_view),
            (rx+r'restful/(?P<app_label>\w+)/(?P<actor>\w+)/(?P<pk>.+)$', self.restful_view),
            (rx+r'choices/(?P<app_label>\w+)/(?P<rptname>\w+)$', self.choices_view),
            (rx+r'choices/(?P<app_label>\w+)/(?P<rptname>\w+)/(?P<fldname>\w+)$', self.choices_view),
        )
        if settings.LINO.use_tinymce:
            urlpatterns += patterns('',
                (rx+r'templates/(?P<app_label>\w+)/(?P<actor>\w+)/(?P<pk>\w+)/(?P<fldname>\w+)$', 
                    self.templates_view),
                (rx+r'templates/(?P<app_label>\w+)/(?P<actor>\w+)/(?P<pk>\w+)/(?P<fldname>\w+)/(?P<tplname>\w+)$', 
                    self.templates_view),
            )

        from os.path import exists, join, abspath, dirname
        
        logger.info("Checking /media URLs ")
        prefix = settings.MEDIA_URL[1:]
        assert prefix.endswith('/')
        
        def setup_media_link(short_name,attr_name=None,source=None):
            target = join(settings.MEDIA_ROOT,short_name)
            if exists(target):
                return
            #~ if settings.LINO.extjs_root:
            if attr_name:
                source = getattr(settings.LINO,attr_name)
                if not source:
                    raise Exception(
                      "%s does not exist and LINO.%s is not set." % (
                      target,attr_name))
            if not exists(source):
                raise Exception("LINO.%s (%s) does not exist" % (attr_name,p))
            if is_devserver():
                #~ urlpatterns += patterns('django.views.static',
                urlpatterns.extend(patterns('django.views.static',
                (r'^%s%s/(?P<path>.*)$' % (prefix,short_name), 
                    'serve', {
                    'document_root': source,
                    'show_indexes': False })))
            else:
                logger.info("Setting up symlink %s -> %s.",target,source)
                symlink = getattr(os,'symlink',None)
                if symlink is not None:
                    symlink(source,target)
            
        setup_media_link('extjs','extjs_root')
        if settings.LINO.use_extensible:
            setup_media_link('extensible','extensible_root')
        if settings.LINO.use_tinymce:
            setup_media_link('tinymce','tinymce_root')
            
        #~ lino_root = join(settings.LINO.project_dir,'using','lino')
        #~ if not exists(lino_root):
            #~ lino_root = 
        #~ setup_media_link('lino',source=join(lino_root,'media'))
        setup_media_link('lino',source=join(dirname(lino.__file__),'..','media'))

        if is_devserver():
            urlpatterns += patterns('django.views.static',
                (r'^%s(?P<path>.*)$' % prefix, 'serve', 
                  { 'document_root': settings.MEDIA_ROOT, 
                    'show_indexes': True }),
            )

        return urlpatterns

    def html_page(self,*args,**kw):
        return '\n'.join([ln for ln in self.html_page_lines(*args,**kw)])
        
    def html_page_lines(self,request,title=None,on_ready='',**kw):
        """Generates the lines of Lino's HTML reponse.
        """
        yield '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">'
        yield '<html><head>'
        yield '<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />'
        #~ if title:
            #~ yield '<title id="title">%s (%s) </title>' % (unicode(title),settings.LINO.title)
        #~ else:
        yield '<title id="title">%s</title>' % settings.LINO.title
        #~ yield '<!-- ** CSS ** -->'
        #~ yield '<!-- base library -->'
        
        def stylesheet(url):
            url = self.media_url() + url
            return '<link rel="stylesheet" type="text/css" href="%s" />' % url
            
        #~ yield '<link rel="stylesheet" type="text/css" href="%s/extjs/resources/css/ext-all.css" />' % self.media_url()
        yield stylesheet('/extjs/resources/css/ext-all.css')
        #~ yield '<!-- overrides to base library -->'
        if settings.LINO.use_extensible:
            yield stylesheet("/extensible/resources/css/extensible-all.css")
          
        if settings.LINO.use_vinylfox:
            p = self.media_url() + '/lino/vinylfox/'
            yield '<link rel="stylesheet" type="text/css" href="%sresources/css/htmleditorplugins.css" />' % p
          
        if settings.LINO.use_filterRow:
            p = self.media_url() + '/lino/filterRow'
            yield '<link rel="stylesheet" type="text/css" href="%s/filterRow.css" />' % p
            
        if settings.LINO.use_gridfilters:
            yield '<link rel="stylesheet" type="text/css" href="%s/extjs/examples/ux/statusbar/css/statusbar.css" />' % self.media_url() 
            yield '<link rel="stylesheet" type="text/css" href="%s/extjs/examples/ux/gridfilters/css/GridFilters.css" />' % self.media_url() 
            yield '<link rel="stylesheet" type="text/css" href="%s/extjs/examples/ux/gridfilters/css/RangeMenu.css" />' % self.media_url() 
            
        yield '<link rel="stylesheet" type="text/css" href="%s/extjs/examples/ux/fileuploadfield/css/fileuploadfield.css" />' % self.media_url() 
        
        yield '<link rel="stylesheet" type="text/css" href="%s/lino/extjs/lino.css">' % self.media_url()
        
        if settings.LINO.use_awesome_uploader:
            yield '<link rel="stylesheet" type="text/css" href="%s/lino/AwesomeUploader/AwesomeUploader.css">' % self.media_url()
            yield '<link rel="stylesheet" type="text/css" href="%s/lino/AwesomeUploader/AwesomeUploader Progress Bar.css">' % self.media_url()
         
        #~ yield '<!-- ** Javascript ** -->'
        #~ yield '<!-- ExtJS library: base/adapter -->'
        def javascript(url):
            url = self.media_url() + url
            return '<script type="text/javascript" src="%s"></script>' % url
            
        if settings.DEBUG:
            yield javascript('/extjs/adapter/ext/ext-base-debug.js')
            yield javascript('/extjs/ext-all-debug.js')
            if settings.LINO.use_extensible:
                yield javascript('/extensible/extensible-all-debug.js')
        else:
            yield javascript('/extjs/adapter/ext/ext-base.js')
            yield javascript('/extjs/ext-all.js')
            #~ yield '<script type="text/javascript" src="%s/extjs/adapter/ext/ext-base.js"></script>' % self.media_url() 
            #~ yield '<script type="text/javascript" src="%s/extjs/ext-all.js"></script>' % self.media_url()
            
            if settings.LINO.use_extensible:
                yield javascript('/extensible/extensible-all.js')
        if translation.get_language() != 'en':
            yield javascript('/extjs/src/locale/ext-lang-'+translation.get_language()+'.js')
            if settings.LINO.use_extensible:
                yield javascript('/extensible/src/locale/extensible-lang-'+translation.get_language()+'.js')
            
        #~ yield '<!-- ExtJS library: all widgets -->'
        #~ if True:
            #~ yield '<style type="text/css">'
            #~ # http://stackoverflow.com/questions/2106104/word-wrap-grid-cells-in-ext-js 
            #~ yield '.x-grid3-cell-inner, .x-grid3-hd-inner {'
            #~ yield '  white-space: normal;' # /* changed from nowrap */
            #~ yield '}'
            #~ yield '</style>'
        if False:
            yield '<script type="text/javascript" src="%s/extjs/Exporter-all.js"></script>' % self.media_url() 
            
        if False:
            yield '<script type="text/javascript" src="%s/extjs/examples/ux/CheckColumn.js"></script>' % self.media_url() 

        yield '<script type="text/javascript" src="%s/extjs/examples/ux/statusbar/StatusBar.js"></script>' % self.media_url()
        
        if settings.LINO.use_tinymce:
            p = self.media_url() + '/tinymce'
            #~ yield '<script type="text/javascript" src="Ext.ux.form.FileUploadField.js"></script>'
            yield '<script type="text/javascript" src="%s/tiny_mce.js"></script>' % p
            yield '<script type="text/javascript" src="%s/lino/tinymce/Ext.ux.TinyMCE.js"></script>' % self.media_url()
            yield '''<script language="javascript" type="text/javascript">
tinymce.init({
        theme : "advanced"
        // , mode : "textareas"
});
</script>'''

        yield '<script type="text/javascript" src="%s/lino/extjs/Ext.ux.form.DateTime.js"></script>' % self.media_url()

        if settings.LINO.use_gridfilters:
            p = self.media_url() + '/extjs/examples/ux/gridfilters'
            #~ yield '<script type="text/javascript" src="%s/extjs/examples/ux/RowEditor.js"></script>' % self.media_url()
            yield '<script type="text/javascript" src="%s/menu/RangeMenu.js"></script>' % p
            yield '<script type="text/javascript" src="%s/menu/ListMenu.js"></script>' % p
            yield '<script type="text/javascript" src="%s/GridFilters.js"></script>' % p
            yield '<script type="text/javascript" src="%s/filter/Filter.js"></script>' % p
            yield '<script type="text/javascript" src="%s/filter/StringFilter.js"></script>' % p
            yield '<script type="text/javascript" src="%s/filter/DateFilter.js"></script>' % p
            yield '<script type="text/javascript" src="%s/filter/ListFilter.js"></script>' % p
            yield '<script type="text/javascript" src="%s/filter/NumericFilter.js"></script>' % p
            yield '<script type="text/javascript" src="%s/filter/BooleanFilter.js"></script>' % p
            
        yield '<script type="text/javascript" src="%s/extjs/examples/ux/fileuploadfield/FileUploadField.js"></script>' % self.media_url()
        
        if settings.LINO.use_filterRow:
            p = self.media_url() + '/lino/filterRow'
            yield '<script type="text/javascript" src="%s/filterRow.js"></script>' % p
            
        if settings.LINO.use_vinylfox:
            p = self.media_url() + '/lino/vinylfox/src/Ext.ux.form.HtmlEditor'
            #~ yield '<script type="text/javascript" src="Ext.ux.form.FileUploadField.js"></script>'
            yield '<script type="text/javascript" src="%s.MidasCommand.js"></script>' % p
            yield '<script type="text/javascript" src="%s.Divider.js"></script>' % p
            yield '<script type="text/javascript" src="%s.HR.js"></script>' % p
            yield '<script type="text/javascript" src="%s.Image.js"></script>' % p
            yield '<script type="text/javascript" src="%s.RemoveFormat.js"></script>' % p
            yield '<script type="text/javascript" src="%s.IndentOutdent.js"></script>' % p
            yield '<script type="text/javascript" src="%s.SubSuperScript.js"></script>' % p
            yield '<script type="text/javascript" src="%s.FindAndReplace.js"></script>' % p
            yield '<script type="text/javascript" src="%s.Table.js"></script>' % p
            yield '<script type="text/javascript" src="%s.Word.js"></script>' % p
            yield '<script type="text/javascript" src="%s.Link.js"></script>' % p
            yield '<script type="text/javascript" src="%s.SpecialCharacters.js"></script>' % p
            yield '<script type="text/javascript" src="%s.UndoRedo.js"></script>' % p
            yield '<script type="text/javascript" src="%s.Heading.js"></script>' % p
            yield '<script type="text/javascript" src="%s.Plugins.js"></script>' % p
            
        if settings.LINO.use_awesome_uploader:
            p = self.media_url() + '/lino/AwesomeUploader/'
            #~ yield '<script type="text/javascript" src="Ext.ux.form.FileUploadField.js"></script>'
            yield '<script type="text/javascript" src="%s/Ext.ux.XHRUpload.js"></script>' % p
            yield '<script type="text/javascript" src="%s/swfupload.js"></script>' % p
            yield '<!-- <script type="text/javascript" src="%s/swfupload.swfobject.js"></script> -->' % p
            yield '<script type="text/javascript" src="%s/Ext.ux.AwesomeUploaderLocalization.js"></script>' % p
            yield '<script type="text/javascript" src="%s/Ext.ux.AwesomeUploader.js"></script>' % p

        #~ yield '<!-- overrides to library -->'
        #~ yield '<script type="text/javascript" src="%slino/extjs/lino.js"></script>' % self.media_url()
        
        if not settings.LINO.build_js_cache_on_startup:
            self.build_js_cache_for_user(request.user)
            
        yield '<script type="text/javascript" src="%s"></script>' % (
            self.media_url(*self.lino_js_parts(request.user)))

        #~ yield '<!-- page specific -->'
        yield '<script type="text/javascript">'

        yield 'Ext.onReady(function(){'
        
        #~ yield "console.time('onReady');"
        
        if settings.LINO.user_model:
        
            if request.subst_user:
                #~ yield "Lino.subst_user = %s;" % py2js(request.subst_user.id)
                yield "Lino.set_subst_user(%s,%s);" % (
                    py2js(request.subst_user.id),
                    py2js(unicode(request.subst_user)))
                user_text = unicode(request.user) + " (" + _("as") + " " + unicode(request.subst_user) + ")"
            else:
                #~ yield "Lino.subst_user = null;"
                yield "Lino.set_subst_user(null);"
                user_text = unicode(request.user) 
                
            user = request.user
            
            yield "Lino.user = %s;" % py2js(dict(id=user.id,name=unicode(user)))
            
            if user.profile.level >= dd.UserLevels.admin:
                authorities = [(u.id,unicode(u)) 
                    for u in users.User.objects.exclude(profile=dd.UserProfiles.blank_item)]
            else:
                authorities = [(u.id,unicode(u)) 
                    for u in users.Authority.objects.filter(user=user)]
            
            #~ handler = self.ext_renderer.instance_handler(user)
            a = users.MySettings.default_action
            handler = self.ext_renderer.action_call(None,a,dict(record_id=user.pk))
            handler = "function(){%s}" % handler
            if len(authorities):
                mysettings = dict(text=_("My settings"),handler=js_code(handler))
                #~ act_as = [
                    #~ dict(text=unicode(u),handler=js_code("function(){Lino.set_subst_user(%s)}" % i)) 
                        #~ for i,u in user.get_received_mandates()]
                act_as = [
                    dict(text=t,handler=js_code("function(){Lino.set_subst_user(%s,%s)}" % (v,py2js(t)))) 
                        for v,t in authorities]
                        #~ for v,t in user.get_received_mandates()]
                act_as.insert(0,dict(
                    text=_("Myself"),
                    handler=js_code("function(){Lino.set_subst_user(null)}")))
                act_as = dict(text=_("Act as..."),menu=dict(items=act_as))
                login_menu = dict(
                    text=user_text,
                    menu=dict(items=[act_as,mysettings]))
            else:
                login_menu = dict(text=user_text,handler=js_code(handler))
                
            yield "Lino.login_menu = %s;" % py2js(login_menu)
            yield "Lino.main_menu = Lino.main_menu.concat(['->',Lino.login_menu]);"
                
        
        #~ yield "Lino.load_mask = new Ext.LoadMask(Ext.getBody(), {msg:'Immer mit der Ruhe...'});"
          
        main=dict(
          id="main_area",
          xtype='container',
          region="center",
          autoScroll=True,
          layout='fit',
          #~ html=self.welcome_template.render(c),
          #~ html=html,
          #~ html=self.site.index_html.encode('ascii','xmlcharrefreplace'),
        )
        
        win = dict(
          layout='fit',
          #~ maximized=True,
          items=main,
          #~ closable=False,
          bbar=dict(xtype='toolbar',items=js_code('Lino.status_bar')),
          #~ title=self.site.title,
          tbar=js_code('Lino.main_menu'),
          #~ tbar=settings.LINO.get_site_menu(self,request.user),
        )
        jsgen.set_for_user(request.user)
        for ln in jsgen.declare_vars(win):
            yield ln
        #~ yield '  new Ext.Viewport({layout:"fit",items:%s}).render("body");' % py2js(win)
        yield '  Lino.viewport = new Ext.Viewport({layout:"fit",items:%s});' % py2js(win)
        yield '  Lino.viewport.render("body");'
            
        #~ yield '  Ext.QuickTips.init();'
        
        yield on_ready
        #~ for ln in on_ready:
            #~ yield ln
        
        #~ yield "console.timeEnd('onReady');"
        yield "}); // end of onReady()"
        yield '</script></head><body>'
        if settings.LINO.use_davlink:
            yield '<applet name="DavLink" code="davlink.DavLink.class"'
            yield '        archive="%s/lino/applets/DavLink.jar"' % self.media_url()
            yield '        width="1" height="1"></applet>'
            # Note: The value of the ARCHIVE attribute is a URL of a JAR file.
        yield '<div id="body"></div>'
        #~ yield '<div id="tbar"/>'
        #~ yield '<div id="main"/>'
        #~ yield '<div id="bbar"/>'
        #~ yield '<div id="konsole"></div>'
        yield "</body></html>"
        
    def linolib_intro(self):
        """
        Called from :xfile:`linolib.js`.
        """
        def fn():
            yield """// lino.js --- generated %s by Lino version %s.""" % (time.ctime(),lino.__version__)
            #~ // $site.title ($lino.welcome_text())
            yield "Ext.BLANK_IMAGE_URL = '%s/extjs/resources/images/default/s.gif';" % self.media_url()
            yield "LANGUAGE_CHOICES = %s;" % py2js(list(LANGUAGE_CHOICES))
            # TODO: replace the following lines by a generic method for all ChoiceLists
            yield "STRENGTH_CHOICES = %s;" % py2js(list(STRENGTH_CHOICES))
            yield "KNOWLEDGE_CHOICES = %s;" % py2js(list(KNOWLEDGE_CHOICES))
            yield "MEDIA_URL = %r;" % (self.media_url())
            #~ yield "ROOT_URL = %r;" % settings.LINO.root_url
            yield "ROOT_URL = %r;" % self.root_url
            
            #~ yield "API_URL = %r;" % self.build_url('api')
            #~ yield "TEMPLATES_URL = %r;" % self.build_url('templates')
            #~ yield "Lino.status_bar = new Ext.ux.StatusBar({defaultText:'Lino version %s.'});" % lino.__version__
        
        #~ return '\n'.join([ln for ln in fn()])
        return '\n'.join(fn())


    def index_view(self, request,**kw):
        #~ from lino.lino_site import lino_site
        #~ if settings.LINO.index_view_action:
            #~ kw.update(on_ready=self.ext_renderer.action_call(
              #~ settings.LINO.index_view_action))
        #~ logger.info("20120706 index_view() %s %r",request.user, request.user.profile)
        kw.update(on_ready=self.ext_renderer.action_call(
          request,
          settings.LINO.modules.lino.Home.default_action))
        #~ kw.update(title=settings.LINO.modules.pcsw.Home.label)
        #~ kw.update(title=lino_site.title)
        #~ mnu = py2js(lino_site.get_site_menu(request.user))
        #~ print mnu
        #~ tbar=ext_elems.Toolbar(items=lino_site.get_site_menu(request.user),region='north',height=29)# renderTo='tbar')
        return HttpResponse(self.html_page(request,**kw))
        #~ html = '\n'.join(self.html_page(request,main,konsole,**kw))
        #~ return HttpResponse(html)


    #~ def form2obj_and_save(self,request,rh,data,elem,is_new,include_rows): # **kw2save):
    def form2obj_and_save(self,ar,data,elem,is_new,restful,file_upload=False): # **kw2save):
        """
        """
        request = ar.request
        rh = ar.ah
        #~ logger.info('20111217 form2obj_and_save %r', data)
        #~ print 'form2obj_and_save %r' % data
        
        #~ logger.info('20120228 before store.form2obj , elem is %s' % obj2str(elem))
        # store normal form data (POST or PUT)
        try:
            rh.store.form2obj(ar,data,elem,is_new)
        except exceptions.ValidationError,e:
            #~ raise
            return self.error_response(e)
           #~ return error_response(e,_("There was a problem while validating your data : "))
        #~ logger.info('20120228 store.form2obj passed, elem is %s' % obj2str(elem))
        
        if not is_new:
            dblogger.log_changes(request,elem)
            
        try:
            elem.full_clean()
        except exceptions.ValidationError, e:
            return self.error_response(e) #,_("There was a problem while validating your data : "))
            
        kw2save = {}
        if is_new:
            kw2save.update(force_insert=True)
        else:
            kw2save.update(force_update=True)
            
        try:
            elem.save(**kw2save)
            
        #~ except Exception,e:
        except IntegrityError,e:
            return self.error_response(e) # ,_("There was a problem while saving your data : "))
            #~ return json_response_kw(success=False,
                  #~ msg=_("There was a problem while saving your data:\n%s") % e)
        kw = dict(success=True)
        if is_new:
            dblogger.log_created(request,elem)
            kw.update(
                message=_("%s has been created.") % obj2unicode(elem))
                #~ record_id=elem.pk)
        else:
            kw.update(message=_("%s has been saved.") % obj2unicode(elem))
            
        kw = elem.after_ui_save(ar,**kw)
        #~ m = getattr(elem,"after_ui_save",None)
        #~ if m is not None:
            #~ kw = m(ar,**kw)
            
        if restful:
            # restful mode (used only for Ext.ensible) needs list_fields, not detail_fields
            kw.update(rows=[rh.store.row2dict(ar,elem,rh.store.list_fields)])
        elif file_upload:
            kw.update(record_id=elem.pk)
            return json_response(kw,content_type='text/html')
        else:
            kw.update(data_record=elem2rec_detailed(ar,elem))
        #~ logger.info("20120208 form2obj_and_save --> %r",kw)
        return json_response(kw)
                
            
        #~ return self.success_response(
            #~ _("%s has been saved.") % obj2unicode(elem),
            #~ rows=[elem])


      
    def grid_config_view(self,request,app_label=None,actor=None):
        rpt = actors.get_actor2(app_label,actor)
        if request.method == 'PUT':
            if not rpt.can_config.passes(request.user):
                msg = _("User %(user)s cannot configure %(report)s.") % dict(
                    user=request.user,report=rpt)
                return self.error_response(None,msg)
            #~ return http.HttpResponseForbidden(msg)
            PUT = http.QueryDict(request.raw_post_data)
            gc = dict(
              widths = [int(x) for x in PUT.getlist(ext_requests.URL_PARAM_WIDTHS)],
              columns = [str(x) for x in PUT.getlist(ext_requests.URL_PARAM_COLUMNS)],
              hiddens=[(x == 'true') for x in PUT.getlist(ext_requests.URL_PARAM_HIDDENS)],
              #~ hidden_cols=[str(x) for x in PUT.getlist('hidden_cols')],
            )
            
            filter = PUT.get('filter',None)
            if filter is not None:
                filter = json.loads(filter)
                gc['filters'] = [ext_requests.dict2kw(flt) for flt in filter]
            
            name = PUT.get('name',None)
            if name is None:
                name = ext_elems.DEFAULT_GC_NAME                 
            else:
                name = int(name)
                
            gc.update(label=PUT.get('label',"Standard"))
            try:
                msg = rpt.save_grid_config(name,gc)
            except IOError,e:
                msg = _("Error while saving GC for %(report)s: %(error)s") % dict(
                    report=rpt,error=e)
                return self.error_response(None,msg)
            #~ logger.info(msg)
            self.build_site_cache(True)            
            return self.success_response(msg)
            
        raise NotImplementedError
        
        
    def api_list_view(self,request,app_label=None,actor=None):
        """
        - GET : List the members of the collection. 
        - PUT : Replace the entire collection with another collection. 
        - POST : Create a new entry in the collection where the ID is assigned automatically by the collection. 
          The ID created is included as part of the data returned by this operation. 
        - DELETE : Delete the entire collection.
        
        (Source: http://en.wikipedia.org/wiki/Restful)
        """
        rpt = self.requested_report(request,app_label,actor)
        
        #~ action_name = request.GET.get(
        action_name = request.REQUEST.get(
            ext_requests.URL_PARAM_ACTION_NAME,
            rpt.default_list_action_name)
        a = rpt.get_url_action(action_name)
        if a is None:
            raise Http404("%s has no url action %r" % (rpt,action_name))
            
        ar = rpt.request(self,request,a)
        ar.renderer = self.ext_renderer
        rh = ar.ah
        
        if request.method == 'POST':
            #~ data = rh.store.get_from_form(request.POST)
            #~ instance = ar.create_instance(**data)
            #~ ar = ext_requests.ViewReportRequest(request,rh,rh.actor.list_action)
            #~ ar = ext_requests.ViewReportRequest(request,rh,rh.actor.default_action)
            elem = ar.create_instance()
            # store uploaded files. 
            # html forms cannot send files with PUT or GET, only with POST
            #~ logger.info("20120208 list POST %s",obj2str(elem,force_detailed=True))
            if rh.actor.handle_uploaded_files is not None:
                rh.actor.handle_uploaded_files(elem,request)
                file_upload = True
            else:
                file_upload = False
            return self.form2obj_and_save(ar,request.POST,elem,True,False,file_upload)
            #~ return self.form2obj_and_save(request,rh,request.POST,instance,True,ar)
            
        if request.method == 'GET':
            #~ print 20120630, 'api_list_view'
            fmt = request.GET.get(
                ext_requests.URL_PARAM_FORMAT,
                ar.action.default_format)
          
            if fmt == ext_requests.URL_FORMAT_JSON:
                ar.renderer = self.ext_renderer
                rows = [ rh.store.row2list(ar,row) for row in ar.sliced_data_iterator]
                #~ return json_response_kw(msg="20120124")
                #~ total_count = len(ar.data_iterator)
                total_count = ar.get_total_count()
                #~ if ar.create_rows:
                row = ar.create_phantom_row()
                if row is not None:
                    d = rh.store.row2list(ar,row)
                    rows.append(d)
                    total_count += 1
                return json_response_kw(count=total_count,
                  rows=rows,
                  title=unicode(ar.get_title()),
                  #~ disabled_actions=rpt.disabled_actions(ar,None),
                  gc_choices=[gc.data for gc in rpt.grid_configs])
                    
            if fmt == ext_requests.URL_FORMAT_HTML:
                ar.renderer = self.ext_renderer
                after_show = ar.get_status(self)
                if isinstance(ar.action,actions.InsertRow):
                    elem = ar.create_instance()
                    #~ print 20120630
                    #~ print elem.national_id
                    rec = elem2rec_insert(ar,rh,elem)
                    after_show.update(data_record=rec)

                kw = dict(on_ready=
                    self.ext_renderer.action_call(ar.request,ar.action,after_show))
                #~ print '20110714 on_ready', params
                kw.update(title=ar.get_title())
                return HttpResponse(self.html_page(request,**kw))
            
            if fmt == 'csv':
                #~ response = HttpResponse(mimetype='text/csv')
                charset = settings.LINO.csv_params.get('encoding','utf-8')
                response = HttpResponse(
                  content_type='text/csv;charset="%s"' % charset)
                if False:
                    response['Content-Disposition'] = \
                        'attachment; filename="%s.csv"' % ar.actor
                else:
                    #~ response = HttpResponse(content_type='application/csv')
                    response['Content-Disposition'] = \
                        'inline; filename="%s.csv"' % ar.actor
                  
                #~ response['Content-Disposition'] = 'attachment; filename=%s.csv' % ar.get_base_filename()
                w = ucsv.UnicodeWriter(response,**settings.LINO.csv_params)
                w.writerow(ar.ah.store.column_names())
                for row in ar.data_iterator:
                    w.writerow([unicode(v) for v in rh.store.row2list(ar,row)])
                return response
                
            #~ if fmt == ext_requests.URL_FORMAT_ODT:
                #~ if ar.get_total_count() > MAX_ROW_COUNT:
                    #~ raise Exception(_("List contains more than %d rows") % MAX_ROW_COUNT)
                #~ target_parts = ['cache', 'odt', str(rpt) + '.odt']
                #~ target_file = os.path.join(settings.MEDIA_ROOT,*target_parts)
                #~ target_url = self.media_url(*target_parts)
                #~ ar.renderer = self.pdf_renderer
                #~ if os.path.exists(target_file):
                    #~ os.remove(target_file)
                #~ logger.info(u"odfpy render %s -> %s",rpt,target_file)
                #~ self.table2odt(ar,target_file)
                #~ return http.HttpResponseRedirect(target_url)
            
            if fmt in (ext_requests.URL_FORMAT_PDF,ext_requests.URL_FORMAT_ODT):
                if ar.get_total_count() > MAX_ROW_COUNT:
                    raise Exception(_("List contains more than %d rows") % MAX_ROW_COUNT)
            
                #~ from lino.utils.appy_pod import setup_renderer
                from lino.utils.appy_pod import Renderer
                #~ from appy.pod.renderer import Renderer
                
                tpl_leaf = "Table.odt" 
                #~ tplgroup = rpt.app_label + '/' + rpt.__name__
                tplgroup = None
                tplfile = find_config_file(tpl_leaf,tplgroup)
                if not tplfile:
                    raise Exception("No file %s / %s" % (tplgroup,tpl_leaf))
                    
                #~ target_parts = ['cache', 'appypdf', str(rpt) + '.odt']
                #~ target_parts = ['cache', 'appypdf', str(rpt) + '.pdf']
                target_parts = ['cache', 'appypdf', str(rpt) + '.' + fmt]
                target_file = os.path.join(settings.MEDIA_ROOT,*target_parts)
                target_url = self.media_url(*target_parts)
                #~ ar.renderer = self.pdf_renderer
                ar.renderer = self.ext_renderer # 20120624
                #~ body = ar.table2xhtml().toxml()
                """
                [NOTE] :doc:`/blog/2012/0211`:
                
                """
                #~ body = etree.tostring(self.table2xhtml(ar))
                #~ logger.info("20120122 body is %s",body)
                context = dict(
                    ar=ar,
                    title=unicode(ar.get_title()),
                    #~ table_body=body,
                    dtos=babel.dtos,
                    dtosl=babel.dtosl,
                    dtomy=babel.dtomy,
                    babelattr=babel.babelattr,
                    babelitem=babel.babelitem,
                    tr=babel.babelitem,
                    #~ iif=iif,
                    settings=settings,
                    #~ restify=restify,
                    #~ site_config = get_site_config(),
                    #~ site_config = settings.LINO.site_config,
                    _ = _,
                    #~ knowledge_text=fields.knowledge_text,
                    )
                #~ lang = str(elem.get_print_language(self))
                if os.path.exists(target_file):
                    os.remove(target_file)
                logger.info(u"appy.pod render %s -> %s (params=%s",
                    tplfile,target_file,settings.LINO.appy_params)
                renderer = Renderer(tplfile, context, target_file,**settings.LINO.appy_params)
                #~ setup_renderer(renderer)
                #~ renderer.context.update(restify=debug_restify)
                renderer.run()
                return http.HttpResponseRedirect(target_url)
                
            if fmt == ext_requests.URL_FORMAT_PRINTER:
                if ar.get_total_count() > MAX_ROW_COUNT:
                    raise Exception(_("List contains more than %d rows") % MAX_ROW_COUNT)
                #~ ar.renderer = self.pdf_renderer # 20120624
                ar.renderer = self.ext_renderer
                
                if False:
                    response = HttpResponse(content_type='text/html;charset="utf-8"')
                    doc = xhg.HTML()
                    doc.set_title(ar.get_title())
                    t = self.table2xhtml(ar)
                    doc.add_to_body(t)
                    xhg.Writer(response).render(doc)
                    return response
                
                if True:
                    response = HttpResponse(content_type='text/html;charset="utf-8"')
                    doc = xghtml.Document(force_unicode(ar.get_title()))
                    doc.body.append(xghtml.E.h1(doc.title))
                    t = doc.add_table()
                    self.ar2html(ar,t)
                    doc.write(response,encoding='utf-8')
                    #~ xhg.Writer(response).render(doc)
                    return response
                
                if False:
                    from lxml.html import builder as html
                    title = unicode(ar.get_title())
                    doc = html.BODY(
                      html.HEAD(html.TITLE(title)),
                      html.BODY(
                        html.H1(title),
                        self.table2xhtml(ar)
                      )
                    )
                    return HttpResponse(etree.tostring(doc),content_type='text/html;charset="utf-8"')
                
            raise Http404("Format %r not supported for GET on %s" % (fmt,rpt))

        raise Http404("Method %s not supported for container %s" % (request.method,rh))
    
    
    def requested_report(self,request,app_label,actor):
        x = getattr(settings.LINO.modules,app_label)
        cl = getattr(x,actor)
        if issubclass(cl,dd.Model):
            return cl._lino_default_table
        return cl
        
    def parse_params(self,rh,request):
        return rh.store.parse_params(request)
        
    #~ def rest2form(self,request,rh,data):
        #~ d = dict()
        #~ logger.info('20120118 rest2form %r', data)
        #~ for i,f in enumerate(rh.store.list_fields):
        #~ return d
        
    def delete_element(self,ar,elem):
        assert elem is not None
        #~ if rpt.disable_delete is not None:
        msg = ar.actor.disable_delete(elem,ar)
        if msg is not None:
            return self.error_response(None,msg)
                
        dblogger.log_deleted(ar.request,elem)
        
        try:
            elem.delete()
        except Exception,e:
            dblogger.exception(e)
            msg = _("Failed to delete %(record)s : %(error)s."
                ) % dict(record=obj2unicode(elem),error=e)
            #~ msg = "Failed to delete %s." % element_name(elem)
            return self.error_response(None,msg)
            #~ raise Http404(msg)
        return HttpResponseDeleted()
        
    def restful_view(self,request,app_label=None,actor=None,pk=None):
        """
        Used to collaborate with a restful Ext.data.Store.
        """
        rpt = self.requested_report(request,app_label,actor)
        a = rpt.default_action
        
        if pk is None:
            elem = None
        else:
            elem = rpt.get_row_by_pk(pk)
        
        ar = rpt.request(self,request,a)
        #~ if not ar.ah.actor.__name__.startswith('Panel'):
            #~ raise Exception("actor is %s" % ar.ah.actor)
        rh = ar.ah
            
        if request.method == 'GET':
            if pk:
                pass
            else:
                rows = [ 
                  rh.store.row2dict(ar,row,rh.store.list_fields) 
                    for row in ar.sliced_data_iterator ]
                return json_response_kw(count=ar.get_total_count(),rows=rows)
        
        if request.method == 'DELETE':
            return self.delete_element(ar,elem)
              
        if request.method == 'POST':
            #~ data = rh.store.get_from_form(request.POST)
            #~ instance = ar.create_instance(**data)
            #~ ar = ext_requests.ViewReportRequest(request,rh,rh.actor.list_action)
            #~ ar = ext_requests.ViewReportRequest(request,rh,rh.actor.default_action)
            instance = ar.create_instance()
            # store uploaded files. 
            # html forms cannot send files with PUT or GET, only with POST
            if ar.actor.handle_uploaded_files is not None:
                ar.actor.handle_uploaded_files(instance,request)
                
            data = request.POST.get('rows')
            #~ logger.info("20111217 Got POST %r",data)
            data = json.loads(data)
            #~ data = self.rest2form(request,rh,data)
            return self.form2obj_and_save(ar,data,instance,True,True)
            
        if request.method == 'PUT':
            if elem:
                data = http.QueryDict(request.raw_post_data).get('rows')
                #~ logger.info('20120118 PUT 1 %r', data)
                data = json.loads(data)
                #~ logger.info('20120118 PUT 2 %r', data)
                #~ data = self.rest2form(request,rh,data)
                #~ print 20111021, data
                #~ fmt = data.get('fmt',None)
                a = rpt.get_url_action(rpt.default_list_action_name)
                ar = rpt.request(self,request,a)
                #~ if not ar.ah.actor.__name__.startswith('Panel'):
                    #~ raise Exception("actor is %s" % ar.ah.actor)
                ar.renderer = self.ext_renderer
                return self.form2obj_and_save(ar,data,elem,False,True) # force_update=True)
            else:
                raise Http404("PUT without element")
          
    def api_element_view(self,request,app_label=None,actor=None,pk=None):
        """
        GET : Retrieve a representation of the addressed member of the collection expressed in an appropriate MIME type.
        PUT : Update the addressed member of the collection or create it with the specified ID. 
        POST : Treats the addressed member as a collection and creates a new subordinate of it. 
        DELETE : Delete the addressed member of the collection. 
        
        (Source: http://en.wikipedia.org/wiki/Restful)
        """
        rpt = self.requested_report(request,app_label,actor)
        #~ if not ah.actor.can_view.passes(request.user):
            #~ msg = "User %s cannot view %s." % (request.user,ah.actor)
            #~ return http.HttpResponseForbidden()
        
        if pk and pk != '-99999' and pk != '-99998':
            elem = rpt.get_row_by_pk(pk)
            if elem is None:
                raise Http404("%s has no row with prmiary key %r" % (rpt,pk))
                #~ raise Exception("20120327 %s.get_row_by_pk(%r)" % (rpt,pk))
        else:
            elem = None
        
        if request.method == 'DELETE':
            ar = rpt.request(self,request)
            return self.delete_element(ar,elem)
            
        if request.method == 'PUT':
            #~ ah = rpt.get_handle(self)
            if elem is None:
                raise Http404('Tried to PUT on element -99999')
            #~ print 20110301, request.raw_post_data
            data = http.QueryDict(request.raw_post_data)
            #~ print 20111021, data
            #~ fmt = data.get('fmt',None)
            a = rpt.get_url_action(rpt.default_list_action_name)
            ar = rpt.request(self,request,a)
            ar.renderer = self.ext_renderer
            return self.form2obj_and_save(ar,data,elem,False,False) # force_update=True)
            
        if request.method == 'GET':
                    
            action_name = request.GET.get(ext_requests.URL_PARAM_ACTION_NAME,
              rpt.default_elem_action_name)
            a = rpt.get_url_action(action_name)
            if a is None:
                raise Http404("%s has no action %r" % (rpt,action_name))
                
            ar = rpt.request(self,request,a)
            ar.renderer = self.ext_renderer
            ah = ar.ah
            
            #~ fmt = request.GET.get('fmt',a.default_format)
            fmt = request.GET.get(ext_requests.URL_PARAM_FORMAT,a.default_format)

            #~ if isinstance(a,actions.OpenWindowAction):
            if a.opens_a_window:
              
                if fmt == ext_requests.URL_FORMAT_JSON:
                    if pk == '-99999':
                        assert elem is None
                        elem = ar.create_instance()
                        datarec = elem2rec_insert(ar,ah,elem)
                    elif pk == '-99998':
                        assert elem is None
                        elem = ar.create_instance()
                        datarec = elem2rec_empty(ar,ah,elem)
                    else:
                        datarec = elem2rec_detailed(ar,elem)
                    
                    return json_response(datarec)
                    
                #~ after_show = dict(data_record=datarec)
                #~ after_show = dict()
                #~ params = dict()
                after_show = ar.get_status(self,record_id=pk)
                #~ bp = self.request2kw(ar)
                
                #~ if a.window_wrapper.tabbed:
                #~ if rpt.get_detail().tabbed:
                #~ if rpt.model._lino_detail.get_handle(self).tabbed:
                if True:
                    tab = request.GET.get(ext_requests.URL_PARAM_TAB,None)
                    if tab is not None: 
                        tab = int(tab)
                        after_show.update(active_tab=tab)
                #~ params.update(base_params=bp)
                
                return HttpResponse(self.html_page(request,a.label,
                  on_ready=self.ext_renderer.action_call(request,a,after_show)))
                
            if isinstance(a,actions.RedirectAction):
                target = a.get_target_url(elem)
                if target is None:
                    raise Http404("%s failed for %r" % (a,elem))
                return http.HttpResponseRedirect(target)
                
            if isinstance(a,actions.RowAction):
                #~ return a.run(ar,elem)
                if pk == '-99998':
                    assert elem is None
                    elem = ar.create_instance()
                
                try:
                    rv = a.run(elem,ar)
                    if rv is None:
                        return self.success_response()
                    return rv
                except actions.ConfirmationRequired,e:
                    r = dict(
                      success=True,
                      confirm_message='\n'.join([unicode(m) for m in e.messages]),
                      step=e.step)
                    return self.action_response(r)
                except actions.Warning,e:
                    r = dict(
                      success=False,
                      message=unicode(e),
                      alert=True)
                    return self.action_response(r)
                except Exception,e:
                    if elem is None:
                        msg = unicode(e)
                    else:
                        msg = _(
                          "Action \"%(action)s\" failed for %(record)s:") % dict(
                          action=a,
                          record=obj2unicode(elem))
                        msg += "\n" + unicode(e)
                    msg += '.\n' + _(
                      "An error report has been sent to the system administrator.")
                    logger.warning(msg)
                    logger.exception(e)
                    return self.error_response(e,msg)
              
            raise NotImplementedError("Action %s is not implemented)" % a)
                
              
        return self.error_response(None,
            "Method %r not supported for elements of %s." % (
                request.method,ah.actor))
        #~ raise Http404("Method %r not supported for elements of %s" % (request.method,ah.actor))
        
        
    def unused_error_response(self,e=None,message=None,**kw):
        kw.update(success=False)
        #~ if e is not None:
        if isinstance(e,Exception):
            if False: # useful when debugging, but otherwise rather disturbing
                logger.exception(e)
            if hasattr(e,'message_dict'):
                kw.update(errors=e.message_dict)
        #~ kw.update(alert_msg=cgi.escape(message_prefix+unicode(e)))
        #~ 20120628b kw.update(alert=True)
        #~ kw.update(message=message)
        if message is None:
            message = unicode(e)
        kw.update(message=cgi.escape(message))
        #~ kw.update(message=message_prefix+unicode(e))
        #~ logger.debug('error_response %s',kw)
        return self.action_response(kw)
    

    def action_response(self,kw):
        """
        Builds a JSON response from given dict, 
        checking first whether there are only allowed keys 
        (defined in :attr:`ACTION_RESPONSES`)
        """
        self.check_action_response(kw)
        return json_response(kw)
            
    def lino_js_parts(self,user):
    #~ def js_cache_name(self):
        #~ return ('cache','js','site.js')
        #~ return ('cache','js','lino.js')
        #~ return ('cache','js','lino_'+user.get_profile()+'_'+translation.get_language()+'.js')
        #~ return ('cache','js','lino_'+(user.profile.name or user.username)+'_'+translation.get_language()+'.js')
        return ('cache','js','lino_' + user.profile.value + '_' + translation.get_language()+'.js')
        
    def build_site_cache(self,force=False):
        """
        Build the site cache files under `/media/cache`,
        especially the :xfile:`lino*.js` files, one per user profile and language.
        """
        if settings.LINO.never_build_site_cache:
            logger.info("Not building site cache because `settings.LINO.never_build_site_cache` is True")
            return 
        if not os.path.isdir(settings.MEDIA_ROOT):
            logger.warning("Not building site cache because "+
            "directory '%s' (settings.MEDIA_ROOT) does not exist.", 
            settings.MEDIA_ROOT)
            return
        
        started = time.time()
        
        settings.LINO.on_each_app('setup_site_cache',force)
        
        makedirs_if_missing(os.path.join(settings.MEDIA_ROOT,'upload'))
        makedirs_if_missing(os.path.join(settings.MEDIA_ROOT,'webdav'))
        
        if force or settings.LINO.build_js_cache_on_startup:
            count = 0
            langs = babel.AVAILABLE_LANGUAGES
            qs = users.User.objects.exclude(profile=dd.UserProfiles.blank_item) # .exclude(level='')
            for lang in langs:
                babel.set_language(lang)
                for user in qs:
                    count += self.build_js_cache_for_user(user,force)
            babel.set_language(None)
                
            logger.info("%d lino*.js files have been built in %s seconds.",
                count,time.time()-started)
          
    def build_js_cache_for_user(self,user,force=False):
        """
        Build the lino*.js file for the specified user and the current language.
        If the file exists and is up to date, don't generate it unless 
        `force=False` is specified.
        
        This is called 
        - on each request if :attr:`lino.Lino.build_js_cache_on_startup` is `False`.
        - with `force=True` by :class:`lino.modles.BuildSiteCache`
        """
        jsgen.set_for_user(user)
        
        fn = os.path.join(settings.MEDIA_ROOT,*self.lino_js_parts(user)) 
        if not force and os.path.exists(fn):
            mtime = os.stat(fn).st_mtime
            if mtime > settings.LINO.mtime:
                if not user.modified or user.modified < datetime.datetime.fromtimestamp(mtime):
                    logger.debug("%s is up to date.",fn)
                    return 0
                    
        logger.info("Building %s ...", fn)
        makedirs_if_missing(os.path.dirname(fn))
        f = codecs.open(fn,'w',encoding='utf-8')
        try:
            self.write_lino_js(f,user)
            #~ f.write(jscompress(js))
            f.close()
            return 1
        except Exception, e:
            """
            If some error occurs, remove the half generated file 
            to make sure that Lino will try to generate it again on next request
            (and report the same error message again).
            """
            f.close()
            os.remove(fn)
            raise
        #~ logger.info("Wrote %s ...", fn)
            
    def write_lino_js(self,f,user):
        tpl = self.linolib_template()
        f.write(jscompress(unicode(tpl)+'\n'))
        
        actors_list = [
            rpt for rpt in table.master_reports \
               + table.slave_reports \
               + table.generic_slaves.values() \
               + table.custom_tables \
               + table.frames_list ]
               
        """
        Call Ext.namespace for *all* actors because e.g. outbox.Mails.FormPanel 
        is defined in ns outbox.Mails which is not directly used by non-expert users.
        """
        
        f.write("Lino.main_menu = %s;\n" % py2js(settings.LINO.get_site_menu(self,user)))
            

        for a in actors_list:
            f.write("Ext.namespace('Lino.%s')\n" % a)
            
        # actors with an own `get_handle_name` don't have a js implementation
        #~ print '20120605 dynamic actors',[a for a in actors_list if a.get_handle_name is not None]
        actors_list = [a for a in actors_list if a.get_handle_name is None]

        actors_list = [a for a in actors_list if a.get_view_permission(jsgen._for_user)]
          
                 
        #~ logger.info('20120120 table.all_details:\n%s',
            #~ '\n'.join([str(d) for d in table.all_details]))
        
        details = set()
        def add(actor,fl,nametpl):
            if fl is not None:
                if not fl in details:
                    fl._formpanel_name = nametpl % actor
                    details.add(fl)
                    
        for a in actors_list:
            add(a,a.detail_layout, "Lino.%s.DetailFormPanel")
            add(a,a.insert_layout, "Lino.%s.InsertFormPanel")
            
        for fl in details:
            lh = fl.get_layout_handle(self)
            for ln in self.js_render_FormPanel(lh,user):
                f.write(ln + '\n')
        
        for rpt in actors_list:
            rh = rpt.get_handle(self) 
            if isinstance(rpt,type) and issubclass(rpt,table.AbstractTable):
                #~ if rpt.model is None:
                #~ f.write('// 20120621 %s\n' % rpt)
                    #~ continue
                
                for ln in self.js_render_GridPanel_class(rh,user):
                    f.write(ln + '\n')
                
            for a in rpt.get_actions():
                if a.opens_a_window:
                    if isinstance(a,(actions.ShowDetailAction,actions.InsertRow)):
                        for ln in self.js_render_detail_action_FormPanel(rh,a):
                              f.write(ln + '\n')
                    for ln in self.js_render_window_action(rh,a,user):
                        f.write(ln + '\n')
                elif a.show_in_workflow:
                    for ln in self.js_render_workflow_action(rh,a,user):
                        f.write(ln + '\n')
        return 1
          
        
    #~ def make_linolib_messages(self):
        #~ """
        #~ Called from :term:`dtl2py`.
        #~ """
        #~ from lino.utils.config import make_dummy_messages_file
        #~ tpl = self.linolib_template()
        #~ messages = set()
        #~ def mytranslate(s):
            #~ messages.add(s)
            #~ return _(s)
        #~ tpl._ = mytranslate
        #~ unicode(tpl) # just to execute the template. result is not needed
        #~ return make_dummy_messages_file(self.linolib_template_name(),messages)
        
    #~ def make_dtl_messages(self):
        #~ from lino.core.kernel import make_dtl_messages
        #~ return make_dtl_messages(self)
        
    def linolib_template_name(self):
        return os.path.join(os.path.dirname(__file__),'linolib.js')
        
    def linolib_template(self):
        def docurl(ref):
            if not ref.startswith('/'):
                raise Exception("Invalid docref %r" % ref)
            # todo: check if file exists...
            return "http://lino.saffre-rumma.net" + ref + ".html"
            
        libname = self.linolib_template_name()
        tpl = CheetahTemplate(codecs.open(libname,encoding='utf-8').read())
        tpl.ui = self
            
        tpl._ = _
        #~ tpl.user = request.user
        tpl.site = settings.LINO
        tpl.settings = settings
        tpl.lino = lino
        tpl.docurl = docurl
        tpl.ui = self
        tpl.ext_requests = ext_requests
        for k in ext_requests.URL_PARAMS:
            setattr(tpl,k,getattr(ext_requests,k))
        return tpl
            
    def templates_view(self,request,
        app_label=None,actor=None,pk=None,fldname=None,tplname=None,**kw):
      
        if request.method == 'GET':
            from lino.models import TextFieldTemplate
            if tplname:
                tft = TextFieldTemplate.objects.get(pk=int(tplname))
                return HttpResponse(tft.text)
                
            rpt = self.requested_report(request,app_label,actor)
            #~ rpt = actors.get_actor2(app_label,actor)
            #~ if rpt is None:
                #~ model = models.get_model(app_label,actor,False)
                #~ rpt = model._lino_default_table
                
            elem = rpt.get_row_by_pk(pk)

            #~ try:
                #~ elem = rpt.model.objects.get(pk=pk)
            #~ except ValueError:
                #~ msg = "Invalid primary key %r for %s.%s." % (pk,rpt.model._meta.app_label,rpt.model.__name__)
                #~ raise Http404(msg)
            #~ except rpt.model.DoesNotExist:
                #~ raise Http404("%s %s does not exist." % (rpt,pk))
                
            if elem is None:
                raise Http404("%s %s does not exist." % (rpt,pk))
                
            #~ TextFieldTemplate.templates
            m = getattr(elem,"%s_templates" % fldname,None)
            #~ m = getattr(rpt.model,"%s_templates" % fldname,None)
            if m is None:
                q = models.Q(user=request.user) | models.Q(user=None)
                #~ q = models.Q(user=request.user)
                qs = TextFieldTemplate.objects.filter(q).order_by('name')
            else:
                qs = m(request)
                
            templates = []
            for obj in qs:
                url = self.build_url('templates',
                    app_label,actor,pk,fldname,unicode(obj.pk))
                templates.append([
                    unicode(obj.name),url,unicode(obj.description)])
            js = "var tinyMCETemplateList = %s;" % py2js(templates)
            return HttpResponse(js,content_type='text/json')
        raise Http404("Method %r not supported" % request.method)
        
    def choices_view(self,request,app_label=None,rptname=None,fldname=None,**kw):
        """
        Return a JSON object with two attributes `count` and `rows`,
        where `rows` is a list of `(display_text,value)` tuples.
        Used by ComboBoxes or similar widgets.
        If `fldname` is not specified, returns the choices for the `jumpto` widget.
        """
        rpt = self.requested_report(request,app_label,rptname)
        #~ rpt = actors.get_actor2(app_label,rptname)
        ar = rpt.request(self,request,rpt.default_action)
        if fldname is None:
            #~ rh = rpt.get_handle(self)
            #~ ar = ViewReportRequest(request,rh,rpt.default_action)
            #~ ar = table.TableRequest(self,rpt,request,rpt.default_action)
            #~ rh = ar.ah
            #~ qs = ar.get_data_iterator()
            qs = ar.data_iterator
            #~ qs = rpt.request(self).get_queryset()
            def row2dict(obj,d):
                d[ext_requests.CHOICES_TEXT_FIELD] = unicode(obj)
                d[ext_requests.CHOICES_VALUE_FIELD] = obj.pk # getattr(obj,'pk')
                return d
        else:
            """
            NOTE: if you define a *parameter* with the same name 
            as some existing *data element* name, then the parameter 
            will override the data element. At least here in choices view.
            """
            #~ field = find_field(rpt.model,fldname)
            field = rpt.get_param_elem(fldname)
            if field is None:
                field = rpt.get_data_elem(fldname)
            #~ logger.info("20120202 %r",field)
            chooser = choosers.get_for_field(field)
            if chooser:
                #~ logger.info('20120710 choices_view() : has chooser')
                qs = chooser.get_request_choices(ar,rpt)
                #~ qs = list(chooser.get_request_choices(ar,rpt))
                #~ logger.info("20120213 %s",qs)
                #~ if qs is None:
                    #~ qs = []
                assert isiterable(qs), \
                      "%s.%s_choices() returned %r which is not iterable." % (
                      rpt.model,fldname,qs)
                if chooser.simple_values:
                    def row2dict(obj,d):
                        #~ d[ext_requests.CHOICES_TEXT_FIELD] = unicode(obj)
                        d[ext_requests.CHOICES_VALUE_FIELD] = unicode(obj)
                        return d
                elif chooser.instance_values:
                    # same code as for ForeignKey
                    def row2dict(obj,d):
                        d[ext_requests.CHOICES_TEXT_FIELD] = unicode(obj)
                        d[ext_requests.CHOICES_VALUE_FIELD] = obj.pk # getattr(obj,'pk')
                        return d
                else:
                    def row2dict(obj,d):
                        d[ext_requests.CHOICES_TEXT_FIELD] = unicode(obj[1])
                        d[ext_requests.CHOICES_VALUE_FIELD] = obj[0]
                        return d
            elif field.choices:
                qs = field.choices
                def row2dict(obj,d):
                    if type(obj) is list or type(obj) is tuple:
                        d[ext_requests.CHOICES_TEXT_FIELD] = unicode(obj[1])
                        d[ext_requests.CHOICES_VALUE_FIELD] = obj[0]
                    else:
                        d[ext_requests.CHOICES_TEXT_FIELD] = unicode(obj)
                        d[ext_requests.CHOICES_VALUE_FIELD] = unicode(obj)
                    return d
                
            elif isinstance(field,models.ForeignKey):
                m = field.rel.to
                t = getattr(m,'_lino_choices_table',m._lino_default_table)
                qs = t.request(self,request).data_iterator
                #~ logger.info('20120710 choices_view(FK) %s --> %s',t,qs)
                def row2dict(obj,d):
                    d[ext_requests.CHOICES_TEXT_FIELD] = unicode(obj)
                    d[ext_requests.CHOICES_VALUE_FIELD] = obj.pk # getattr(obj,'pk')
                    return d
            else:
                raise Http404("No choices for %s" % fldname)
                
                
        #~ quick_search = request.GET.get(ext_requests.URL_PARAM_FILTER,None)
        #~ if quick_search is not None:
            #~ qs = table.add_quick_search_filter(qs,quick_search)
            
        count = len(qs)
            
        offset = request.GET.get(ext_requests.URL_PARAM_START,None)
        if offset:
            qs = qs[int(offset):]
            #~ kw.update(offset=int(offset))
        limit = request.GET.get(ext_requests.URL_PARAM_LIMIT,None)
        if limit:
            #~ kw.update(limit=int(limit))
            qs = qs[:int(limit)]
            
        rows = [ row2dict(row,{}) for row in qs ]
        return json_response_kw(count=count,rows=rows) 
        #~ return json_response_kw(count=len(rows),rows=rows) 
        #~ return json_response_kw(count=len(rows),rows=rows,title=_('Choices for %s') % fldname)
        

    #~ def quicklink(self,request,app_label,actor,**kw):
        #~ rpt = self.requested_report(request,app_label,actor)
        #~ return self.action_href(rpt.default_action,**kw)

    def setup_handle(self,h,ar):
        """
        ar is usually None, except for actors with dynamic handle
        """
        #~ logger.info('20120621 ExtUI.setup_handle() %s',h)
        if isinstance(h,tables.TableHandle):
            if issubclass(h.actor,table.Table):
                if h.actor.model is None \
                    or h.actor.model is dd.Model \
                    or h.actor.model._meta.abstract:
                    #~ logger.info('20120621 %s : no real table',h)
                    return
            ll = layouts.ListLayout(h.actor.get_column_names(ar),h.actor,hidden_elements=h.actor.hidden_columns)
            #~ h.list_layout = layouts.ListLayoutHandle(h,ll,hidden_elements=h.actor.hidden_columns)
            h.list_layout = ll.get_layout_handle(self)
        else:
            h.list_layout = None
                
        if h.actor.parameters:
            if h.actor.params_template:
                params_template = h.actor.params_template
            else:
                #~ params_template= ' '.join([pf.name for pf in h.actor.params])
                params_template= ' '.join(h.actor.parameters.keys())
            pl = layouts.ParamsLayout(params_template,h.actor)
            h.params_layout = pl.get_layout_handle(self)
            #~ h.params_layout.main.update(hidden = h.actor.params_panel_hidden)
            #~ h.params_layout = layouts.LayoutHandle(self,pl)
            #~ logger.info("20120121 %s params_layout is %s",h,h.params_layout)
        
        h.store = ext_store.Store(h)
        
        #~ if h.store.param_fields:
            #~ logger.info("20120121 %s param_fields is %s",h,h.store.param_fields)
        
        #~ 20120614 if h.list_layout:
            #~ h.on_render = self.build_on_render(h.list_layout.main)
            
        #~ elif isinstance(h,table.FrameHandle):
            #~ if issubclass(h.report,table.EmptyTable):
                #~ h.store = ext_store.Store(h)
          
                
                      
    def source_dir(self):
        return os.path.abspath(os.path.dirname(__file__))
        
    def a2btn(self,a,**kw):
        if isinstance(a,actions.SubmitDetail):
            kw.update(panel_btn_handler=js_code('function(panel){panel.save()}'))
            
        elif isinstance(a,actions.ShowDetailAction):
            kw.update(panel_btn_handler=js_code('Lino.show_detail'))
        elif isinstance(a,actions.InsertRow):
            kw.update(must_save=True)
            kw.update(panel_btn_handler=js_code(
                'function(panel){Lino.show_insert(panel)}'))
        elif isinstance(a,actions.DuplicateRow):
            kw.update(panel_btn_handler=js_code(
                'function(panel){Lino.show_insert_duplicate(panel)}'))
        elif isinstance(a,actions.DeleteSelected):
            kw.update(panel_btn_handler=js_code("Lino.delete_selected"))
                #~ "Lino.delete_selected" % a))
        elif isinstance(a,actions.RowAction):
            if a.url_action_name is None:
                raise Exception("Action %r has no url_action_name" % a)
            kw.update(must_save=True)
            kw.update(
              panel_btn_handler=js_code("Lino.row_action_handler(%r)" % a.url_action_name))
        elif isinstance(a,actions.ListAction):
            if a.url_action_name is None:
                raise Exception("Action %r has no url_action_name" % a)
            kw.update(
              panel_btn_handler=js_code("Lino.list_action_handler(%r)" % a.url_action_name))
            kw.update(must_save=True)
        else:
            kw.update(panel_btn_handler=js_code("Lino.%s" % a))
        kw.update(
          text=a.label,
          #~ name=a.name,
          auto_save=a.auto_save,
          itemId=a.name,
          #~ text=unicode(a.label),
        )
        if a.help_text:
            kw.update(tooltip=a.help_text)
        return kw
        
    def unused_setup_detail_handle(self,dh):
        """
        Adds UI-specific information to a DetailHandle.
        """
        lh_list = dh.lh_list
        if len(lh_list) == 1:
            dh.tabbed = False
            lh = lh_list[0]
            #~ lh.label = None
            dh.main = lh.main
            #~ main.update(autoScroll=True)
        else:
            dh.tabbed = True
            tabs = [lh.main for lh in lh_list]
            #~ for t in tabs: t.update(autoScroll=True)
            dh.main = ext_elems.TabPanel(tabs)
            
        dh.on_render = self.build_on_render(dh.main)
            
    def build_on_render(self,main):
        "dh is a FormLayout or a ListLayout"
        on_render = []
        elems_by_field = {}
        field_elems = []
        for e in main.active_children:
            if isinstance(e,ext_elems.FieldElement):
                field_elems.append(e)
                l = elems_by_field.get(e.field.name,None)
                if l is None:
                    l = []
                    elems_by_field[e.field.name] = l
                l.append(e)
            
        for e in field_elems:
            #~ if isinstance(e,FileFieldElement):
                #~ kw.update(fileUpload=True)
            chooser = choosers.get_for_field(e.field)
            if chooser:
                #~ logger.debug("20100615 %s.%s has chooser", self.lh.layout, e.field.name)
                for f in chooser.context_fields:
                    for el in elems_by_field.get(f.name,[]):
                        #~ if main.has_field(f):
                        #~ varname = varname_field(f)
                        #~ on_render.append("%s.on('change',Lino.chooser_handler(%s,%r));" % (varname,e.ext_name,f.name))
                        on_render.append(
                            "%s.on('change',Lino.chooser_handler(%s,%r));" % (
                            el.as_ext(),e.as_ext(),f.name))
        return on_render
        
    #~ def formpanel_name(self,layout):
        #~ if isinstance(layout,layouts.FormLayout
            #~ return "Lino.%s.InsertFormPanel" % self._table
        #~ elif isinstance(layout,layouts.FormLayout):
            #~ return "Lino.%s.DetailFormPanel" % self._table
        #~ raise Exception("Unknown Form Layout %s" % layout)
      
        
      
    def js_render_FormPanel(self,dh,user):
        
        tbl = dh.layout._table
        
        yield ""
        yield "%s = Ext.extend(Lino.FormPanel,{" % dh.layout._formpanel_name
        yield "  layout: 'fit',"
        yield "  auto_save: true,"
        if dh.layout.window_size and dh.layout.window_size[1] == 'auto':
            yield "  autoHeight: true,"
        if settings.LINO.is_installed('contenttypes') and issubclass(tbl,table.Table):
            yield "  content_type: %s," % py2js(ContentType.objects.get_for_model(tbl.model).pk)
        yield "  initComponent : function() {"
        yield "    var containing_panel = this;"
        for ln in jsgen.declare_vars(dh.main):
            yield "    " + ln
        yield "    this.items = %s;" % dh.main.as_ext()
        yield "    this.before_row_edit = function(record) {"
        for ln in ext_elems.before_row_edit(dh.main):
            yield "      " + ln
        yield "    }"
        on_render = self.build_on_render(dh.main)
        if on_render:
            yield "    this.onRender = function(ct, position) {"
            for ln in on_render:
                yield "      " + ln
            #~ yield "      Lino.%s.FormPanel.superclass.onRender.call(this, ct, position);" % tbl
            yield "      %s.superclass.onRender.call(this, ct, position);" % dh.layout._formpanel_name
            yield "    }"

        #~ yield "    Lino.%s.FormPanel.superclass.initComponent.call(this);" % tbl
        yield "    %s.superclass.initComponent.call(this);" % dh.layout._formpanel_name
        
        if tbl.active_fields:
            yield '    // active_fields:'
            for name in tbl.active_fields:
                e = dh.main.find_by_name(name)
                if e is not None: # 20120715
                    yield '    %s.on("%s",function(){this.save()},this);' % (py2js(e),e.active_change_event)
                    """
                    Seems that checkboxes don't emit a change event when they are changed.
                    http://www.sencha.com/forum/showthread.php?43350-2.1-gt-2.2-OPEN-Checkbox-missing-the-change-event
                    """
        yield "  }"
        yield "});"
        yield ""
        
        
    def js_render_detail_action_FormPanel(self,rh,action):
        rpt = rh.actor
        yield ""
        #~ yield "// js_render_detail_action_FormPanel %s" % action
        dtl = action.get_window_layout()
        #~ dtl = rpt.detail_layout
        if dtl is None:
            raise Exception("action %s on table %r == %r without detail?" % (action,action.actor,rpt))
        #~ yield "Lino.%sPanel = Ext.extend(Lino.%s.FormPanel,{" % (action,dtl._table)
        yield "Lino.%sPanel = Ext.extend(%s,{" % (action,dtl._formpanel_name)
        yield "  empty_title: %s," % py2js(action.get_button_label())
        #~ if not isinstance(action,actions.InsertRow):
        if action.hide_navigator:
            yield "  hide_navigator: true,"
            
        if rh.actor.params_panel_hidden:
            yield "  params_panel_hidden: true,"

        yield "  ls_bbar_actions: %s," % py2js([
            rh.ui.a2btn(a) for a in rpt.get_actions(action) 
                if a.show_in_bbar and a.get_action_permission(jsgen._for_user,None,None)]) 
        yield "  ls_url: %s," % py2js(ext_elems.rpt2url(rpt))
        if action != rpt.default_action:
            yield "  action_name: %s," % py2js(action.url_action_name)
        #~ yield "  active_fields: %s," % py2js(rpt.active_fields)
        yield "  initComponent : function() {"
        a = rpt.detail_action
        if a:
            yield "    this.ls_detail_handler = Lino.%s;" % a
        a = rpt.insert_action
        if a:
            yield "    this.ls_insert_handler = Lino.%s;" % a
            
        yield "    Lino.%sPanel.superclass.initComponent.call(this);" % action
        yield "  }"
        yield "});"
        yield ""
        
    def js_render_GridPanel_class(self,rh,user):
        
        yield ""
        #~ yield "// js_render_GridPanel_class"
        yield "Lino.%s.GridPanel = Ext.extend(Lino.GridPanel,{" % rh.actor
        
        kw = dict()
        #~ kw.update(empty_title=%s,rh.actor.get_button_label()
        kw.update(ls_url=ext_elems.rpt2url(rh.actor))
        kw.update(ls_store_fields=[js_code(f.as_js()) for f in rh.store.list_fields])
        if rh.store.pk is not None:
            kw.update(ls_id_property=rh.store.pk.name)
            kw.update(pk_index=rh.store.pk_index)
            #~ if settings.LINO.use_contenttypes:
            if settings.LINO.is_installed('contenttypes'):
                kw.update(content_type=ContentType.objects.get_for_model(rh.actor.model).pk)
        kw.update(ls_quick_edit=rh.actor.cell_edit)
        kw.update(ls_bbar_actions=[
            rh.ui.a2btn(a) 
              for a in rh.actor.get_actions(rh.actor.default_action) 
                  if a.show_in_bbar and a.get_action_permission(jsgen._for_user,None,None)])
        kw.update(ls_grid_configs=[gc.data for gc in rh.actor.grid_configs])
        kw.update(gc_name=ext_elems.DEFAULT_GC_NAME)
        #~ if action != rh.actor.default_action:
            #~ kw.update(action_name=action.name)
        #~ kw.update(content_type=rh.report.content_type)
        
        vc = dict(emptyText=_("No data to display."))
        if rh.actor.editable:
            vc.update(getRowClass=js_code('Lino.getRowClass'))
        kw.update(viewConfig=vc)
        
        
        
        kw.update(page_length=rh.actor.page_length)
        kw.update(stripeRows=True)

        #~ if rh.actor.master:
        kw.update(title=rh.actor.label)
        kw.update(disabled_actions_index=rh.store.column_index('disabled_actions'))
        
        for k,v in kw.items():
            yield "  %s : %s," % (k,py2js(v))
        
        yield "  initComponent : function() {"
        
        #~ a = rh.actor.get_action('detail')
        a = rh.actor.detail_action
        if a:
            yield "    this.ls_detail_handler = Lino.%s;" % a
        #~ a = rh.actor.get_action('insert')
        a = rh.actor.insert_action
        if a:
            yield "    this.ls_insert_handler = Lino.%s;" % a
        
        
        yield "    var ww = this.containing_window;"
        for ln in jsgen.declare_vars(rh.list_layout.main.columns):
            yield "    " + ln
            
            
        yield "    this.before_row_edit = function(record) {"
        for ln in ext_elems.before_row_edit(rh.list_layout.main):
            yield "      " + ln
        yield "    };"
        
        #~ if rh.on_render:
        on_render = self.build_on_render(rh.list_layout.main)        
        if on_render:
            yield "    this.onRender = function(ct, position) {"
            for ln in on_render:
                yield "      " + ln
            yield "      Lino.%s.GridPanel.superclass.onRender.call(this, ct, position);" % rh.actor
            yield "    }"
            
            
        yield "    this.ls_columns = %s;" % py2js([ 
            ext_elems.GridColumn(i,e) for i,e 
                in enumerate(rh.list_layout.main.columns)])
            
        #~ yield "    this.columns = this.apply_grid_config(this.gc_name,this.ls_grid_configs,this.ls_columns);"
        #~ yield "    this.colModel = Lino.ColumnModel({columns:this.apply_grid_config(this.gc_name,this.ls_grid_configs,this.ls_columns)});"

        #~ yield "    this.items = %s;" % rh.list_layout._main.as_ext()
        #~ 20111125 see ext_elems.py too
        #~ if self.main.listeners:
            #~ yield "  config.listeners = %s;" % py2js(self.main.listeners)
        yield "    Lino.%s.GridPanel.superclass.initComponent.call(this);" % rh.actor
        yield "  }"
        yield "});"
        yield ""
      
            
    def js_render_workflow_action(self,rh,action,user):
        """
        Defines the non-window action used by :meth:`row_action_button`
        """
        yield "Lino.%s = function(rp,pk,action) { " % action
        #~ panel = "Lino.%s.GridPanel.ls_url" % action 
        url = ext_elems.rpt2url(rh.actor)
        yield "  Lino.run_row_action(rp,action,%s,pk,%s);" % (
            py2js(url),py2js(action.url_action_name))
        yield "};"


    def js_render_window_action(self,rh,action,user):
      
        rpt = rh.actor
        
        if isinstance(action,actions.ShowDetailAction):
            mainPanelClass = "Lino.%sPanel" % action
        elif isinstance(action,actions.InsertRow): 
            mainPanelClass = "Lino.%sPanel" % action
        elif isinstance(action,actions.GridEdit):
            mainPanelClass = "Lino.%s.GridPanel" % rpt
        elif isinstance(action,actions.Calendar):
            mainPanelClass = "Lino.CalendarPanel"
            #~ mainPanelClass = "Lino.CalendarAppPanel"
            #~ mainPanelClass = "Ext.ensible.cal.CalendarPanel"
        else:
            return 
        if action.actor is None:
            raise Exception("20120524 %s %s actor is None" % (rh.actor,action))
        if rpt.parameters:
            params = rh.params_layout.main
            #~ assert params.__class__.__name__ == 'ParameterPanel'
        else:
            params = None
            
        windowConfig = dict()
        #~ ws = action.actor.window_size
        wl = action.get_window_layout()
        if wl is not None:
            ws = wl.window_size
            if ws:
                windowConfig.update(
                    #~ width=ws[0],
                    width=js_code('Lino.chars2width(%d)' % ws[0]),
                    maximized=False,
                    draggable=True, 
                    maximizable=True, 
                    modal=True)
                if ws[1] == 'auto':
                    windowConfig.update(autoHeight=True)
                elif isinstance(ws[1],int):
                    #~ windowConfig.update(height=ws[1])
                    windowConfig.update(height=js_code('Lino.rows2height(%d)' % ws[1]))
                else:
                    raise ValueError("height")
                #~ print 20120629, action, windowConfig
                
        #~ yield "var fn = function() {" 
        #~ yield "};" 
        yield "Lino.%s = new Lino.WindowAction(%s,function(){" % (action,py2js(windowConfig))
        #~ yield "  console.log('20120625 fn');" 
        if isinstance(action,actions.Calendar):
            yield "  return Lino.calendar_app.get_main_panel();"
        else:
            p = dict()
            if action is settings.LINO.modules.lino.Home.default_action:
                p.update(is_home_page=True)
            #~ yield "  var p = {};" 
            if action.hide_top_toolbar:
                p.update(hide_top_toolbar=True)
                #~ yield "  p.hide_top_toolbar = true;" 
            if action.actor.hide_window_title:
                #~ yield "  p.hide_window_title = true;" 
                p.update(hide_window_title=True)
            #~ yield "  p.is_main_window = true;" # workaround for problem 20111206
            p.update(is_main_window=True) # workaround for problem 20111206
            yield "  var p = %s;"  % py2js(p)
            #~ if isinstance(action,actions.Calendar):
                #~ yield "  p.items = Lino.CalendarAppPanel_items;" 
            if params:
                for ln in jsgen.declare_vars(params):
                    yield '  '  + ln
                yield "  p.params_panel = %s;" % params
                yield "  p.params_panel.fields = %s;" % py2js(
                  [e for e in params.walk() if isinstance(e,ext_elems.FieldElement)])
            
            yield "  return new %s(p);" % mainPanelClass
        #~ yield "  console.log('20120625 rv is',rv);" 
        #~ yield "  return rv;"
        yield "});" 
        
    
    def table2xhtml(self,ar,max_row_count=300):
        doc = xghtml.Document(force_unicode(ar.get_title()))
        t = doc.add_table()
        self.ar2html(ar,t)
        return xghtml.E.tostring(t.as_element())
        
    def ar2html(self,ar,tble):
        """
        Using lino.utils.xmlgen.html
        """
        tble.attrib.update(cellspacing="3px",bgcolor="#ffffff", width="100%")
        
        fields = ar.ah.store.list_fields
        headers = [force_unicode(col.label or col.name) for col in ar.ah.list_layout.main.columns]
        cellwidths = None
        columns = ar.ah.list_layout.main.columns
        
        if ar.request is not None:
            widths = [x for x in ar.request.REQUEST.getlist(ext_requests.URL_PARAM_WIDTHS)]
            col_names = [str(x) for x in ar.request.REQUEST.getlist(ext_requests.URL_PARAM_COLUMNS)]
            hiddens = [(x == 'true') for x in ar.request.REQUEST.getlist(ext_requests.URL_PARAM_HIDDENS)]
        
            if col_names:
                fields = []
                headers = []
                cellwidths = []
                columns = []
                for i,cn in enumerate(col_names):
                    col = None
                    for e in ar.ah.list_layout.main.columns:
                        if e.name == cn:
                            col = e
                            break
                    #~ col = ar.ah.list_layout._main.find_by_name(cn)
                    #~ col = ar.ah.list_layout._main.columns[ci]
                    if col is None:
                        #~ names = [e.name for e in ar.ah.list_layout._main.walk()]
                        raise Exception("No column named %r in %s" % (cn,ar.ah.list_layout.main.columns))
                    if not hiddens[i]:
                        columns.append(col)
                        fields.append(col.field._lino_atomizer)
                        headers.append(force_unicode(col.label or col.name))
                        cellwidths.append(widths[i])
          
        
        #~ for k,v in ar.actor.override_column_headers(ar):
            
        oh = ar.actor.override_column_headers(ar)
        if oh:
            for i,e in enumerate(columns):
                header = oh.get(e.name,None)
                if header is not None:
                    headers[i] = unicode(header)
            #~ print 20120507, oh, headers
          
        
        sums  = [fld.zero for fld in fields]
        #~ cellattrs = dict(align="center",valign="middle",bgcolor="#eeeeee")
        cellattrs = dict(align="left",valign="top",bgcolor="#eeeeee")
        hr = tble.add_header_row(*headers,**cellattrs)
        if cellwidths:
            for i,td in enumerate(hr): 
                td.attrib.update(width=cellwidths[i])
        #~ print 20120623, ar.actor
        recno = 0
        for row in ar.data_iterator:
            recno += 1
            cells = [x for x in ar.ah.store.row2html(ar,fields,row,sums)]
            #~ print 20120623, cells
            tble.add_body_row(*cells,**cellattrs)
                
        has_sum = False
        for i in sums:
            if i:
                has_sum = True
                break
        if has_sum:
            tble.add_body_row(*ar.ah.store.sums2html(ar,fields,sums),**cellattrs)
            
            
            
    
    def create_layout_panel(self,lh,name,vertical,elems,**kw):
        pkw = dict()
        pkw.update(labelAlign=kw.pop('label_align','top'))
        pkw.update(hideCheckBoxLabels=kw.pop('hideCheckBoxLabels',True))
        pkw.update(label=kw.pop('label',None))
        pkw.update(width=kw.pop('width',None))
        pkw.update(height=kw.pop('height',None))
        if kw:
            raise Exception("Unknown panel attributes %r" % kw)
        if name == 'main':
            if isinstance(lh.layout,layouts.ListLayout):
                #~ return ext_elems.GridMainPanel(lh,name,vertical,*elems,**pkw)
                #~ return ext_elems.GridMainPanel(lh,name,lh.layout._table,*elems,**pkw)
                return ext_elems.GridElement(lh,name,lh.layout._table,*elems,**pkw)
            if isinstance(lh.layout,layouts.ParamsLayout) : 
                return ext_elems.ParamsPanel(lh,name,vertical,*elems,**pkw)
                #~ fkw = dict(layout='fit', autoHeight= True, frame= True, items=pp)
                #~ if lh.layout._table.params_panel_hidden:
                    #~ fkw.update(hidden=True)
                #~ return ext_elems.FormPanel(**fkw)
            if isinstance(lh.layout,layouts.FormLayout): 
                if len(elems) == 1 or vertical:
                    return ext_elems.DetailMainPanel(lh,name,vertical,*elems,**pkw)
                else:
                    return ext_elems.TabPanel(lh,name,*elems,**pkw)
            raise Exception("No element class for layout %r" % lh.layout)
        return ext_elems.Panel(lh,name,vertical,*elems,**pkw)


