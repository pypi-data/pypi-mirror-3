# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from asv_files.models import UploaderSess
from asv_files.settings import settings as AFS
import logging
logger = logging.getLogger(__name__)

def gen_uuid(req = None):
    if req:
        u = UploaderSess.create(req)
        uuid = u.uuid
    else:
        if AFS.ASV_FILES__DEBUG:
            logger.error('gen_uuid::only gen')
        u = UploaderSess.create()
        uuid = u.uuid
    return uuid
