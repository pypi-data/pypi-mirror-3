# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls.defaults import *
from django.views.static import serve
from asv_utils.dj.media import settings as AME

urlpatterns = patterns('',
    url(r'^media/?$', serve, {'document_root':AME.ASV_MEDIA__MEDIA_ROOT}, name='asv_media__media_url'),
    url(r'^media/(?P<path>.*)$', serve, {'document_root':AME.ASV_MEDIA__MEDIA_ROOT}, name='asv_media__media'),
)
