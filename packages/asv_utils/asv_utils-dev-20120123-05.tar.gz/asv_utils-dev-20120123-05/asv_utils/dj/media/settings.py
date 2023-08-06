# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings as dj_settings
from asv_utils.dj import reverse_lazy
from asv_utils.dj.media import settings_default
import os

class Settings(object):
    def __init__(self):
        for setting in dir(settings_default):
            if setting == setting.upper():
                setattr(self, setting, getattr(settings_default, setting))
        djs = dir(dj_settings)
        #print(djs)
        for setting in dir(self):
            #print('>>{}'.format(setting))
            if setting == setting.upper():
                s = None
                try:
                    djs.index(setting)
                    s = getattr(dj_settings, setting)
                except ValueError:
                    pass
                if s:
                    setattr(self, setting, s)
                    #print('S>{}'.format(setting))
        self.SETTINGS_MODULE = settings_default
        mp = self.SETTINGS_MODULE.__file__
        mn = self.SETTINGS_MODULE.__name__
        mn = mn.rsplit('.',1)[1]
        mp = mp.rsplit(mn,1)[0]+'media'+os.sep
        self.ASV_MEDIA__MEDIA_ROOT = mp
        mr = None
        try:
            mr = reverse_lazy('asv_media__media_url')
            if mr[-1] != '/':
                mr += '/'
        except Exception:
            pass
        self.ASV_MEDIA__MEDIA_URL = mr
#