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

import lino
from urllib import urlencode
from django.conf import settings
from django.conf.urls.defaults import patterns, include, url

class Handle:
  
    def __init__(self,ui):
        self.ui = ui
        
    def setup(self):
        if self.ui is not None:
            self.ui.setup_handle(self)
        
        
class Handled(object):
  
    "Inherited by Table, Layout, and maybe others"
    
    _handle_class = None
    
    @classmethod
    def do_setup(self):
        pass
        
    @classmethod
    def class_init(self):
        pass
        #~ self._handles = {}
      
    #~ @classmethod
    #~ def before_ui_handle(self,ui):
        #~ pass
        
    @classmethod
    def get_handle(self,ui):
        assert ui is None or isinstance(ui,UI), \
            "%s.get_handle() : %r is not a BaseUI" % (self,ui)
        if ui is None:
            hname = '_lino_console_handler'
        else:
            hname = ui._handler_attr_name
        h = self.__dict__.get(hname,None)
        if h is None:
            h = self._handle_class(ui,self)
            setattr(self,hname,h)
            h.setup()
        return h
        
        #~ h = self._handles.get(ui,None)
        #~ if h is None:
            #~ # self.before_ui_handle(ui)
            #~ h = self._handle_class(ui,self)
            #~ # be careful to not store it in the base class's `_handles`:
            #~ self._handles = dict(self._handles)
            #~ self._handles[ui] = h
            #~ h.setup()
        #~ return h
        
        
class UI:
    """
    """
    name = None
    #~ prefix = None
    verbose_name = None
    
    def __init__(self,prefix='',**options):
        settings.LINO.setup(**options)
        assert isinstance(prefix,basestring)
        self.prefix = prefix
        self.root_url = settings.LINO.root_url
        if prefix:
            assert not prefix.startswith('/')
            assert not prefix.endswith('/')
            self.root_url += '/' + prefix
        #~ print 'settings.LINO.root_url:', settings.LINO.root_url
        #~ print 'ui.root_url:', self.root_url
        
    def build_url(self,*args,**kw):
        #~ url = self.site.root_url
        url = self.root_url
        if args:
            url += '/' + ("/".join(args))
        #~ if self.prefix:
            #~ url = "/" + self.prefix + url
        if len(kw):
            url += "?" + urlencode(kw)
        return url
        
    def media_url(self,*args,**kw):
        return self.build_url('media',*args,**kw)
        #~ settings.MEDIA_URL
        
    def get_patterns(self):
        #~ return patterns('',(self.prefix, include(self.get_urls())))
        urlpatterns = patterns('',
            (r'^favicon\.ico$', 'django.views.generic.simple.redirect_to', 
                {'url': settings.MEDIA_URL + 'lino/favicon.ico'})
        )
        
        if self.prefix:
            urlpatterns += patterns('',
              ('^'+self.prefix+"/", include(self.get_urls()))
            )
        else:
            urlpatterns += self.get_urls()
        return urlpatterns
        
    def get_urls():
        raise NotImplementedError()
        

    def field2elem(self,lui,field,**kw):
        pass
        
    def setup_handle(self,h):
        pass
        
