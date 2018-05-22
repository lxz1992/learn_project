import logging

from django.test import TestCase

from cr_review_sys.const import Const, CrFieldMap
from cr_review_sys.models import Users, OpArea, SyncJob, MdMccMnc, ActivityCr
from md_analysis.const import MdMeta
from my_to_do.util.sync_helper import SyncHelper


class SyncHelperTest(TestCase):

    def setUp(self):
        self.logger = logging.getLogger('aplogger')
        self.sync_common = SyncHelper()

    def test_get_user_site_map(self):

        Users.objects.create(login_name="mtk10809", site="MTK")
        Users.objects.create(login_name="mtk08298", site="MTK")
        Users.objects.create(login_name="mtk04694", site="MTK")

        expected_result = {"mtk10809": {"site": "MTK"}, "mtk08298": {
            "site": "MTK"}, "mtk04694": {"site": "MTK"}}

        test_result = self.sync_common.get_user_site_map()
        self.assertEqual(test_result, expected_result)

    def test_get_md_class(self):
        cr_class = "New feature"
        test_result = self.sync_common.get_md_class(cr_class, "")
        self.assertEqual(test_result, cr_class)

        cr_class = "Change feature"
        test_result = self.sync_common.get_md_class(cr_class, "test")
        self.assertEqual(test_result, cr_class)

        cr_class = "Bug"
        resolution = "Completed"
        expected_result = "New bug"
        test_result = self.sync_common.get_md_class(cr_class, resolution)
        self.assertEqual(test_result, expected_result)

        cr_class = "Bug"
        resolution = "Duplicated"
        expected_result = "Known bug"
        test_result = self.sync_common.get_md_class(cr_class, resolution)
        self.assertEqual(test_result, expected_result)

        cr_class = "Question"
        resolution = "Completed"
        expected_result = "Non-bug"
        test_result = self.sync_common.get_md_class(cr_class, resolution)
        self.assertEqual(test_result, expected_result)

    def test_get_op_area(self):
        OpArea.objects.create(area="Asia", operator="True Move")
        OpArea.objects.create(area="EU", operator="TIM")
        OpArea.objects.create(area="Asia", operator="TWN")
        OpArea.objects.create(area="Asia", operator="Ufone")
        OpArea.objects.create(area="North A", operator="VideoTron")

        # all upper cases
        except_result = {"TRUE MOVE": "Asia", "TIM": "EU",
                         "TWN": "Asia", "UFONE": "Asia", "VIDEOTRON": "North A"}
        test_result = self.sync_common.get_op_area()
        self.assertDictEqual(test_result, except_result)

    def test_get_lastest_sync_job_id(self):

        sync_job_id = "tstdb20180101174302"
        SyncJob.objects.create(activity_id=MdMeta.ActivityId,
                               sync_job_id=sync_job_id, is_active=Const.IS_ACTIVE)

        SyncJob.objects.create(activity_id=MdMeta.ActivityId,
                               sync_job_id="tstdb20180101174303", is_active=Const.NOT_ACTIVE)

        expected_result = {Const.SYNC_JOB_ID: sync_job_id}
        test_result = self.sync_common.get_lastest_sync_job_id(
            MdMeta.ActivityId)
        self.assertDictContainsSubset(expected_result, test_result)

    def test_get_country_operator_by_plmn(self):
        # 41405.0 plmn with .0
        plmn1 = "414"
        plmn2 = "05"
        expected_country = "Myanmar"
        expected_operator = "Ooredoo"
        test_plmn = "41405.0"
        MdMccMnc.objects.create(id="{}_{}".format(
            plmn1, plmn2), country=expected_country, operator=expected_operator)
        (test_country, test_operator) = self.sync_common.get_country_operator_by_plmn(
            test_plmn)
        self.assertEqual(expected_country, test_country)
        self.assertEqual(expected_operator, test_operator)

        # 310410, usual plmn
        plmn1 = "310"
        plmn2 = "410"
        expected_country = "United States of America"
        expected_operator = "AT&T"
        test_plmn = "{}{}".format(plmn1, plmn2)
        MdMccMnc.objects.create(id="{}_{}".format(
            plmn1, plmn2), country=expected_country, operator=expected_operator)
        (test_country, test_operator) = self.sync_common.get_country_operator_by_plmn(
            test_plmn)
        self.assertEqual(expected_country, test_country)
        self.assertEqual(expected_operator, test_operator)

        # correct plmn but with other char
        test_plmn = "{}{}.0 US".format(plmn1, plmn2)
        (test_country, test_operator) = self.sync_common.get_country_operator_by_plmn(
            test_plmn)
        self.assertEqual(expected_country, test_country)
        self.assertEqual(expected_operator, test_operator)

        # null case
        plmn1 = ""
        plmn2 = ""
        expected_country = None
        expected_operator = None
        test_plmn = "{}{}".format(plmn1, plmn2)
        (test_country, test_operator) = self.sync_common.get_country_operator_by_plmn(
            test_plmn)
        self.assertEqual(expected_country, test_country)
        self.assertEqual(expected_operator, test_operator)

    def test_get_patch_cr_type(self):
        # Type: New feature
        cr_class = "New feature"
        resolution = "Completed"
        expected_result = "New feature"
        test_result = self.sync_common.get_patch_cr_type(cr_class, resolution)
        self.assertEqual(test_result, expected_result)

        # no resolution
        cr_class = "New feature"
        resolution = None
        expected_result = None
        test_result = self.sync_common.get_patch_cr_type(cr_class, resolution)
        self.assertEqual(test_result, expected_result)

        # Type: Change feature
        cr_class = "Change feature"
        resolution = "Completed"
        expected_result = "Change feature"
        test_result = self.sync_common.get_patch_cr_type(cr_class, resolution)
        self.assertEqual(test_result, expected_result)

        # Type: Change feature
        cr_class = "Change feature"
        resolution = "Duplicated"
        expected_result = "Known issue"
        test_result = self.sync_common.get_patch_cr_type(cr_class, resolution)
        self.assertEqual(test_result, expected_result)

        # Type: Change feature
        cr_class = "Bug"
        resolution = "Completed"
        expected_result = "New bug"
        test_result = self.sync_common.get_patch_cr_type(cr_class, resolution)
        self.assertEqual(test_result, expected_result)

    def test_get_latest_act_cr_list(self):
        sync_job_id = "tstdb20171220000001"

        ActivityCr.objects.create(
            id="1_tstdb03618301_tstdb20171220000001", activity_id=MdMeta.ActivityId, cr_id="tstdb03618301", sync_job_id=sync_job_id)
        ActivityCr.objects.create(
            id="1_tstdb03618301_tstdb20171220000002", activity_id=MdMeta.ActivityId, cr_id="tstdb03618302", sync_job_id=sync_job_id)
        ActivityCr.objects.create(
            id="1_tstdb03618301_tstdb20171220000003", activity_id=MdMeta.ActivityId, cr_id="tstdb03618303", sync_job_id=sync_job_id, active=1)

        expected_result = ["tstdb03618301", "tstdb03618302", "tstdb03618303"]
        test_result = self.sync_common.get_latest_act_cr_list(
            MdMeta.ActivityId, sync_job_id)
        self.assertEqual(test_result, expected_result)

        expected_result = ["tstdb03618303"]
        test_result = self.sync_common.get_latest_act_cr_list(
            MdMeta.ActivityId, sync_job_id, only_active=True)
        self.assertEqual(test_result, expected_result)

    def test_success_get_full_cr_info_with_plmn(self):
        # normal case
        plmn1 = "310"
        plmn2 = "410"
        expected_country = "United States of America"
        expected_operator = "AT&T"
        test_plmn = "{}{}".format(plmn1, plmn2)
        MdMccMnc.objects.create(id="{}_{}".format(
            plmn1, plmn2), country=expected_country, operator=expected_operator)

        ori_cr_info = {CrFieldMap.Wits.MD_Info_PLMN1: test_plmn}
        expected_result = {CrFieldMap.Custom.Country: expected_country,
                           CrFieldMap.Custom.Operator: expected_operator, CrFieldMap.Wits.MD_Info_PLMN1: test_plmn}
        test_result = self.sync_common.get_full_cr_info_with_plmn(
            **ori_cr_info)
        self.assertDictEqual(test_result, expected_result)

    def test_fail_get_full_cr_info_with_plmn(self):
        # normal case
        plmn1 = "110"
        plmn2 = "001"
        expected_country = None
        expected_operator = None
        test_plmn = "{}{}".format(plmn1, plmn2)

        ori_cr_info = {CrFieldMap.Wits.MD_Info_PLMN1: test_plmn}
        expected_result = {CrFieldMap.Custom.Country: expected_country,
                           CrFieldMap.Custom.Operator: expected_operator, CrFieldMap.Wits.MD_Info_PLMN1: test_plmn}
        test_result = self.sync_common.get_full_cr_info_with_plmn(
            **ori_cr_info)
        self.assertDictEqual(test_result, expected_result)
