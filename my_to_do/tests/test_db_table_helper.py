import logging

from django.test import TestCase

from my_to_do.util.db_table_helper import DbTableHelper
from md_analysis.const import MdMeta


class DbTableHelperTest(TestCase):

    def setUp(self):
        self.logger = logging.getLogger('aplogger')

    def test_get_wwsta_top10_id(self):
        act_id = 1
        sync_job_id = "tstdb20171206031709"
        period = "2017"
        figure_type = "Customer"
        type_value = "OPPO"
        priority = "0.Urgent"

        expected_result = "{}_{}_{}_{}_{}_{}".format(
            act_id, sync_job_id, period, figure_type, type_value, priority)
        test_result = DbTableHelper.get_wwsta_top10_id(
            act_id, sync_job_id, period, figure_type, type_value, priority)
        self.assertEqual(test_result, expected_result)

    def test_get_wwstatistic_map_id(self):
        act_id = 1
        sync_job_id = "tstdb20171206031709"
        state = "Submit"
        period = "2017"
        country = "China"
        operator = "China Mobile"
        md_class = "Known bug"

        expected_result = "{}_{}_{}_{}_{}_{}_{}".format(
            act_id, sync_job_id, state, period, country, operator, md_class)
        test_result = DbTableHelper.get_wwsta_map_id(
            act_id, sync_job_id, state, period, country, operator, md_class)
        self.assertEqual(test_result, expected_result)

    def test_get_resolved_es_id(self):
        act_id = 1
        sync_job_id = "tstdb20171206031709"
        period_type = "Week"
        site = "Assignee_site"
        customer = "VIVO"
        period = "2017.w52"
        priority = "0.Urgent"

        expected_result = "{}_{}_{}_{}_{}_{}_{}".format(
            act_id, sync_job_id, period_type, site, customer, period, priority)
        test_result = DbTableHelper.get_resolved_es_id(
            act_id, sync_job_id, period_type, site, customer, period, priority)
        self.assertEqual(test_result, expected_result)

    def test_get_open_es_id(self):
        act_id = 1
        sync_job_id = "tstdb20171206031709"
        site = "Assignee_site"
        customer = "VIVO"
        stay_submitted = "<1W"
        priority = "0.Urgent"

        expected_result = "{}_{}_{}_{}_{}_{}".format(
            act_id, sync_job_id, site, customer, stay_submitted, priority)
        test_result = DbTableHelper.get_open_es_id(
            act_id, sync_job_id, site, customer, stay_submitted, priority)
        self.assertEqual(test_result, expected_result)

    def test_get_operator_cert_id(self):
        act_id = 1
        sync_job_id = "tstdb20171206031709"
        operator = "CMCC"
        is_completed = "0"
        platform = "MT6375P"
        company = "BIRD"
        period_week = "2017"

        expected_result = "{}_{}_{}_{}_{}_{}_{}".format(
            act_id, sync_job_id, operator, is_completed, platform, company, period_week)
        test_result = DbTableHelper.get_operator_cert_id(
            act_id, sync_job_id, operator, is_completed, platform, company, period_week)
        self.assertEqual(test_result, expected_result)

    def test_get_fta_id(self):
        act_id = 1
        sync_job_id = "tstdb20171206031709"
        is_completed = "0"
        platform = "MT6375P"
        company = "BIRD"
        period_week = "2017"

        expected_result = "{}_{}_{}_{}_{}_{}".format(
            act_id, sync_job_id, is_completed, platform, company, period_week)
        test_result = DbTableHelper.get_fta_id(
            act_id, sync_job_id, is_completed, platform, company, period_week)
        self.assertEqual(test_result, expected_result)

    def test_get_ces_specific_id(self):
        act_id = 1
        sync_job_id = "tstdb20171206031709"
        country = "China"
        operator = "CMCC"
        priority = "0.Urgent"

        expected_result = "{}_{}_{}_{}_{}".format(
            act_id, sync_job_id, country, operator, priority)
        test_result = DbTableHelper.get_ces_specific_id(
            act_id, sync_job_id, country, operator, priority)
        self.assertEqual(test_result, expected_result)

    def test_get_crm_hw_prj_id(self):
        hw_prj_id = "a0E6F00001HWZbUUAX"
        hw_type = "Operator"
        operator = "CMCC"
        expected_result = "{}_{}_{}".format(hw_prj_id, hw_type, operator)
        test_result = DbTableHelper.get_crm_hw_prj_id(hw_prj_id, hw_type, operator)
        self.assertEqual(test_result, expected_result)

    def test_get_crm_hw_prj_milestone_id(self):
        hw_prj_id = "a0E6F00001HWZbUUAX"
        hw_type = "Operator"
        milestone_name = "OPTR (CMCC VoLTE)"
        operator = "CMCC"
        expected_result = "{}_{}_{}_{}".format(hw_prj_id, hw_type, milestone_name, operator)
        test_result = DbTableHelper.get_crm_hw_prj_milestone_id(
            hw_prj_id, hw_type, milestone_name, operator)
        self.assertEqual(test_result, expected_result)

    def test_get_act_cr_id(self):
        act_id = MdMeta.ActivityId
        cr_id = "tstdb03618301"
        expected_result = "{}_{}".format(act_id, cr_id)
        test_result = DbTableHelper.get_act_cr_id(
            act_id, cr_id)
        self.assertEqual(test_result, expected_result)
