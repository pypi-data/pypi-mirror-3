# -*- coding: UTF-8 -*-
## Copyright 2010-2012 Luc Saffre
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

Overview
--------

Lino's authentification utilities

Notes
-----

The source code is at :srcref:`/lino/utils/auth.py`.
Notes about marked code locations:

[C1] Before logging the error we must create a `request.user` 
     attribute, otherwise Django might say 
     "AssertionError: The XView middleware requires authentication 
     middleware to be installed."
     
Documented classes and functions
--------------------------------

"""

import os
import logging
logger = logging.getLogger(__name__)


from django.utils import translation
from django.conf import settings
from django import http

from lino.utils import babel
from lino.core.modeltools import resolve_model
from lino.core import perms
from lino.ui import requests as ext_requests

class AnonymousUser(object):
  
    authenticated = False
    username = 'anonymous'
    modified = None
    
    def __init__(self):
        try:
            self.profile = perms.UserProfiles.get_by_value(settings.LINO.anonymous_user_profile)
        except KeyError:
            raise Exception(
                "Invalid value %r for `LINO.anonymous_user_profile`. Must be one of %s" % (
                    settings.LINO.anonymous_user_profile,
                    [i.value for i in perms.UserProfiles.items()]))
        


class NoUserMiddleware(object):
    """
    Middleware that will be used on sites with 
    empty :attr:`lino.Lino.user_model`.
    It just adds a `user` attribute whose value is None.
    """
    anonymous_user = None
    #~ class NoUser(object):
        #~ profile = UserProfiles.admin
        
    def process_request(self, request):
        # trigger site startup if necessary
        settings.LINO.startup()
        
        if self.anonymous_user is None:
            self.anonymous_user = AnonymousUser()
        request.user = self.anonymous_user
        request.subst_user = None
        
        

if settings.LINO.user_model:
  
    USER_MODEL = resolve_model(settings.LINO.user_model)
    
    class RemoteUserMiddleware(object):
        """
        This does the same as
        `django.contrib.auth.middleware.RemoteUserMiddleware`, 
        but in a simplified manner and without using Sessions.
        
        It also activates the User's language, if that field is not empty.
        Since it will run *after*
        `django.contrib.auth.middleware.RemoteUserMiddleware`
        (at least if you didn't change :meth:`lino.Lino.get_middleware_classes`),
        it will override any browser setting.
        
        """

        def process_request(self, request):
          
            username = request.META.get(
                settings.LINO.remote_user_header,settings.LINO.default_user)
            if not username:
                raise Exception("No %s in %s" 
                  % (settings.LINO.remote_user_header,request.META))
                  
            # trigger site startup if necessary
            settings.LINO.startup()
            
            """
            20120110 : alicia hatte es geschafft, beim Anmelden ein Leerzeichen vor ihren Namen zu setzen. 
            Apache ließ sie als " alicia" durch.
            Und Lino legte brav einen neuen User " alicia" an.
            """
            username = username.strip()
            
            try:
                request.user = USER_MODEL.objects.get(username=username)
                if len(babel.AVAILABLE_LANGUAGES) > 1:
                    if request.user.language:
                        translation.activate(request.user.language)
                        request.LANGUAGE_CODE = translation.get_language()
                        
                if request.method == 'GET':
                    su = request.GET.get(ext_requests.URL_PARAM_SUBST_USER,None)
                elif request.method == 'PUT':
                    PUT = http.QueryDict(request.raw_post_data)
                    su = PUT.get(ext_requests.URL_PARAM_SUBST_USER,None)
                elif request.method == 'POST':
                    su = request.POST.get(ext_requests.URL_PARAM_SUBST_USER,None)
                else:
                    su = None
                if su:
                    #~ logger.info("20120714 su is %r",su)
                    try:
                        request.subst_user = settings.LINO.user_model.objects.get(id=int(su))
                        #~ logger.info("20120714 su is %s",request.subst_user.username)
                    except settings.LINO.user_model.DoesNotExist, e:
                        request.subst_user = None
                else:
                    request.subst_user = None
                    
                        
            except USER_MODEL.DoesNotExist,e:
                # [C1]
                request.user = None  
                logger.exception("Unknown username %s from request %s",username, request)
                raise Exception(
                  "Unknown username %r. Please contact your system administrator." 
                  % username)
            
            
        
