# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings as DJS
from asv_files import settings_default

class Settings(object):
    def __init__(self):
        for setting in dir(settings_default):
            if setting == setting.upper():
                setattr(self, setting, getattr(settings_default, setting))
        DJS_d = dir(DJS)
        for setting in dir(self):
            if setting == setting.upper():
                s = None
                try:
                    DJS_d.index(setting)
                    s = getattr(DJS, setting)
                except ValueError:
                    pass
                if s:
                    setattr(self, setting, s)
        self.SETTINGS_MODULE = settings_default
        self.ASV_FILES__FILE_STORAGE = self.ASV_FILES__FILE_STORAGE or DJS.DEFAULT_FILE_STORAGE
        self.ASV_FILES__TMP_FILE_STORAGE = self.ASV_FILES__TMP_FILE_STORAGE or DJS.DEFAULT_FILE_STORAGE
    #
settings = Settings()


