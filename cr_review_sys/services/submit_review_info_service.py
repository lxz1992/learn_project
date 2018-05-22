'''
@author: mtk10809
'''
import datetime
import logging

from django.db import transaction
from django.utils import timezone

from cr_review_sys.const import ReviewInfoFieldMap, Const
from cr_review_sys.errors import RecordUpdateInvalid
from cr_review_sys.models import CrReviewinfo, CrReviewcomments
from md_analysis.const import BULK_BATCH_SIZE
from my_to_do.util import Singleton
from my_to_do.util.db_table_helper import DbTableHelper


class SubmitReviewInfoService(object, metaclass=Singleton):

    def __init__(self):
        self.logger = logging.getLogger("aplogger")

    def submit_review_info_entry(self, activity_id, cr_id, **kwds):

        # check review info exist or not
        check_exist = self.check_review_info(cr_id, activity_id)
        if check_exist:
            updated_time = kwds[Const.UPDATED_TIME]
            check_consistency = self.check_review_info_updated_time(
                cr_id, activity_id, updated_time)

            # exist and check update time. return fail if updated_time didn't
            # match with db time
            if check_consistency:
                self.update_review_info(cr_id, activity_id, **kwds)
            else:
                raise RecordUpdateInvalid()
        else:
            self.insert_review_info(cr_id, activity_id, **kwds)

    def get_review_info_updated_time(self, cr_id, activity_id):
        result = None
        t_id = DbTableHelper.get_cr_review_info_id(cr_id, activity_id)
        queryset = CrReviewinfo.objects.filter(id=t_id)
        for eachrow in queryset:
            result = eachrow.updated_time
        return result

    def check_review_info(self, cr_id, activity_id):
        t_id = DbTableHelper.get_cr_review_info_id(cr_id, activity_id)
        queryset = CrReviewinfo.objects.filter(id=t_id)
        return any(x for x in queryset)

    @transaction.atomic
    def insert_review_info(self, cr_id, activity_id, **kwds):
        review_info = kwds[Const.REVIEW_INFO]
        review_comments = []

        t_id = DbTableHelper.get_cr_review_info_id(cr_id, activity_id)
        review_info.update({
            ReviewInfoFieldMap.ID: t_id,
            ReviewInfoFieldMap.CR_ID: cr_id,
            ReviewInfoFieldMap.ACTIVITY_ID: activity_id
        })
        CrReviewinfo.objects.create(**review_info)

        for eachrow in kwds[Const.REVIEW_COMMENTS]:
            review_comments.append(CrReviewcomments(**eachrow))
        CrReviewcomments.objects.bulk_create(
            review_comments, batch_size=BULK_BATCH_SIZE)

    def update_review_info(self, cr_id, activity_id, **kwds):
        review_info = kwds[Const.REVIEW_INFO]
        review_info.update({ReviewInfoFieldMap.UPDATED_TIME: timezone.now()})
        review_comments = []

        t_id = DbTableHelper.get_cr_review_info_id(cr_id, activity_id)
        CrReviewinfo.objects.filter(id=t_id).update(**review_info)

        for eachrow in kwds[Const.REVIEW_COMMENTS]:
            review_comments.append(CrReviewcomments(**eachrow))
        CrReviewcomments.objects.bulk_create(
            review_comments, batch_size=BULK_BATCH_SIZE)

    def check_review_info_updated_time(self, cr_id, activity_id, input_updated_time):
        time_diff = None
        # if the user can't modify the update time & and update time is also directly return by api
        # why we need to care the time zone ? 
        input_updated_time = datetime.datetime.strptime(
                input_updated_time, "%Y-%m-%d %H:%M:%S")
        db_updated_time = self.get_review_info_updated_time(cr_id, activity_id).replace(tzinfo=None)

        if input_updated_time:
            time_diff = db_updated_time - input_updated_time
                
        return time_diff != None and time_diff.seconds == 0 and time_diff.days == 0
