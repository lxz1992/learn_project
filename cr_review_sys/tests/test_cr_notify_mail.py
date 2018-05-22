import datetime
import os

from django.test import TestCase

from cr_review_sys.const import MailInfo, Const
from cr_review_sys.models import Cr, ActivityCr, Users, Activity, CrReviewinfo,\
    CrReviewcomments
from cr_review_sys.services.cr_notify_mail_service import CrNotifyMailService


class CrNotifyMailTest(TestCase):

    def setUp(self):
        owner = "mtk10809"
        activity_id = 1
        Activity.objects.create(activity_id=activity_id, owner=owner)
        Users.objects.create(
            login_name="mtk10809", full_name="Claire Hsieh", e_mail="claire.hsieh@mediatek.com", reporting_manager="mtk06979")
        Users.objects.create(
            login_name="mtk06979", full_name="Cash Chang", e_mail="cash.chang@mediatek.com", reporting_manager="mtk03528")
        Users.objects.create(
            login_name="mtk02471", full_name="Ivy Liao", e_mail="ivy.liao@mediatek.com", reporting_manager="mtk03528")

        Cr.objects.create(cr_id="tstdb03618301",
                          title="title test for key tstdb03618301",
                          priority="2.Medium",
                          cr_class="Bug",
                          assignee_dept="wcs_se3_ps15",
                          assignee="mtk10809",
                          state=MailInfo.State.Submitted.value, assign_date=datetime.datetime(2017, 12, 31))
        ActivityCr.objects.create(
            id="1_tstdb03618301", activity_id=activity_id, cr_id="tstdb03618301", active=Const.IS_ACTIVE)
        CrReviewinfo.objects.create(
            id="tstdb03618301_1",
            activity_id=activity_id,
            cr_id="tstdb03618301",
            waived=0,
            remark="remark test",
            importance="importance",
            war_room="war_room",
            progress="progress",
            additional_fields='{"WITS_Field1":"value1", "WITS_Field2":"value2", "WITS_Field3":"value3"}')
        CrReviewcomments.objects.create(
            activity_id=activity_id, cr_id="tstdb03618301", login_name="mtk10809", review_comments="review comments test")
        CrReviewcomments.objects.create(
            activity_id=activity_id, cr_id="tstdb03618301", login_name="mtk10809", review_comments="review comments test 2")
        CrReviewcomments.objects.create(
            activity_id=activity_id, cr_id="tstdb03618301", login_name="mtk10809", review_comments="review comments test 3")

        Cr.objects.create(cr_id="tstdb03618302",
                          title="title test for key tstdb03618302",
                          priority="1.High",
                          cr_class="Question",
                          assignee_dept="wsd_acf_af1",
                          assignee="mtk10809",
                          state=MailInfo.State.Submitted.value, assign_date=datetime.datetime(2017, 12, 1))
        ActivityCr.objects.create(
            id="1_tstdb03618302", activity_id=activity_id, cr_id="tstdb03618302", active=Const.IS_ACTIVE)

        Cr.objects.create(cr_id="tstdb03618303",
                          title="title test for key tstdb03618303",
                          priority="1.High",
                          state=MailInfo.State.Assigned.value, assign_date=datetime.datetime(2017, 1, 31))
        ActivityCr.objects.create(
            id="1_tstdb03618303", activity_id=activity_id, cr_id="tstdb03618303", active=Const.IS_ACTIVE)
        CrReviewinfo.objects.create(
            id="tstdb03618303_1", activity_id=activity_id, cr_id="tstdb03618303", waived=1)

        Cr.objects.create(cr_id="tstdb03618304",
                          title="title test for key tstdb03618304",
                          priority="2.Medium",
                          cr_class="Bug",
                          assignee_dept="wcs_se3_ps15",
                          assignee="mtk10809",
                          state=MailInfo.State.Submitted.value, assign_date=datetime.datetime(2018, 3, 21))
        ActivityCr.objects.create(
            id="1_tstdb03618304", activity_id=activity_id, cr_id="tstdb03618304", active=Const.IS_ACTIVE)
        CrReviewinfo.objects.create(
            id="tstdb03618304_1", activity_id=activity_id, cr_id="tstdb03618304", waived=0, remark="remark test", importance="importance", war_room="war_room", progress="progress")
        self.mail_service = CrNotifyMailService()

    def test_activity_mail_notice(self):
        json_file = "test.json"
#         json_path = ""
        self.mail_service.activity_mail_notice(
            json_file, os.path.dirname(__file__))

    def test_get_activity_cr_list(self):
        activity_id = 1
        test_result = self.mail_service.get_activity_cr_list(activity_id)
        expected_result = ["tstdb03618301", "tstdb03618302",
                           "tstdb03618303", 'tstdb03618304']
        self.assertEqual(test_result, expected_result)

    def test_get_cr_url(self):
        cr_id = "tstdb03618301"
        expected_result = "tstdb"
        test_result = self.mail_service.get_cr_url(cr_id)
        self.assertEqual(expected_result, test_result)

    def test_get_activity_cr_info(self):
        activity_id = 1
        test_result = self.mail_service.get_activity_cr_info(activity_id)
        if test_result:
            assert True
        else:
            assert False
