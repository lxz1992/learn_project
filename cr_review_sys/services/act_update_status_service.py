'''
Created on Jan 5, 2018

@author: MTK06979
'''
import logging

from cr_review_sys.models import ActivityUpdateStatus
from my_to_do.util import Singleton


class ActivityUpdateStatusService(object, metaclass=Singleton):

    def __init__(self):
        self.logger = logging.getLogger("aplogger")

    def getActivityStatus(self, aid):
        return ActivityUpdateStatus.objects.get(id=aid)

    def updateActivityStatus(self, aid, **kwds):
        return ActivityUpdateStatus.objects.filter(id=aid).update(**kwds)
