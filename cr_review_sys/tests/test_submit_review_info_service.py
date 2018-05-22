import logging

from django.test import TestCase

from cr_review_sys.const import ReviewInfoFieldMap
from cr_review_sys.models import CrReviewinfo
from cr_review_sys.services.submit_review_info_service import SubmitReviewInfoService
from my_to_do.util.db_table_helper import DbTableHelper


class SubmitReviewInfoTest(TestCase):

    def setUp(self):
        self.logger = logging.getLogger('aplogger')
        self.submit_review_info_service = SubmitReviewInfoService()

    def test_true_check_review_info_updated_time(self):
        cr_id = "ALPS02738610"
        activity_id = "1"
        updated_time = "2018-03-18 00:00:05"
        cr_updated_time_utf_plus_8 = "2018-03-18 08:00:05"
        expected_reuslt = True
        t_id = DbTableHelper.get_cr_review_info_id(cr_id, activity_id)

        CrReviewinfo.objects.create(
            id=t_id, activity_id=activity_id, cr_id=cr_id)
        CrReviewinfo.objects.filter(id=t_id).update(
            updated_time=cr_updated_time_utf_plus_8)

        test_result = self.submit_review_info_service.check_review_info_updated_time(
            cr_id, activity_id, updated_time)
        self.assertEqual(expected_reuslt, test_result)

    def test_false_check_review_info_updated_time(self):
        cr_id = "ALPS02738610"
        activity_id = "1"
        updated_time = "2018-03-18 00:00:05"
        db_updated_time = "2018-03-18 00:00:07"
        expected_reuslt = False
        t_id = DbTableHelper.get_cr_review_info_id(cr_id, activity_id)

        CrReviewinfo.objects.create(
            id=t_id, activity_id=activity_id, cr_id=cr_id)
        CrReviewinfo.objects.filter(id=t_id).update(
            updated_time=db_updated_time)

        test_result = self.submit_review_info_service.check_review_info_updated_time(
            cr_id, activity_id, updated_time)
        self.assertEqual(expected_reuslt, test_result)
