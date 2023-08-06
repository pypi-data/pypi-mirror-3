# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from asv_utils.common import *
from django.conf import settings
from django.core.exceptions import *
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.functional import lazy
from django.core.urlresolvers import reverse, resolve
from django.core.files.storage import FileSystemStorage
FSS = FileSystemStorage(location=settings.MEDIA_ROOT)
#---------------------------------------------------------------
#---------------------------------------------------------------
def Return404(request,addParams={},U='',tmpl='root/404.html',**kwargs):
    P = {
         'URI': request.get_full_path(),
         'BODYCLASS': 'all',
    }
    if addParams:
      P.update(addParams)
    R = render_to_response(tmpl,P,context_instance=RequestContext(request))
    return R
#---------------------------------------------------------------
#---------------------------------------------------------------
def Return50x(request,addParams={},U='',tmpl='root/404.html',**kwargs):
    P = {
         'URI': request.get_full_path(),
         'BODYCLASS': 'all',
    }
    if addParams:
      P.update(addParams)
    R = render_to_response(tmpl,P,context_instance=RequestContext(request))
    return R
#---------------------------------------------------------------
#---------------------------------------------------------------
reverse_lazy = lambda *args, **kwargs : lazy(reverse, str)(*args, **kwargs)
#---------------------------------------------------------------
#---------------------------------------------------------------

