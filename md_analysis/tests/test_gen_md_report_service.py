import datetime
import logging

from django.test import TestCase

from cr_review_sys.const import CrPriority
from cr_review_sys.models import ActivityCr, Cr, CrmHwProject, Activity
from md_analysis.const import MdMeta, MdCrFieldMap, WwStatisticTop10, WwStaMap,\
    ResolvedEs, MdState, Ces, CrmHwPrj, OpCert, MdHwPrjType, FTA
from md_analysis.services.gen_md_report_service import GenMdReportService
from my_to_do.util.db_table_helper import DbTableHelper


class NewDate(datetime.datetime):
    '''
    mock now is 2017,12,25 christmas
    '''
    @classmethod
    def now(cls, tz=None):
        return cls(2017, 12, 25)


class GenMdReportServiceTest(TestCase):

    def setUp(self):
        datetime.datetime = NewDate
        self.logger = logging.getLogger('aplogger')
        self.gen_report_service = GenMdReportService()

    def test_get_cr_info_by_current_sync_job_id(self):
        cr_id_list = ["tstdb03618301", "tstdb03618302"]
        Cr.objects.create(cr_id="tstdb03618301",
                          md_info_op_name="CMCC", customer_company="OPPO", md_info_country="China", assignee="mtk10809")
        Cr.objects.create(cr_id="tstdb03618302",
                          md_info_op_name="CMCC", md_info_country="China", assignee="mtk10809")

        expected_result = [
            {
                MdCrFieldMap.CR_ID: "tstdb03618301",
                MdCrFieldMap.SUBMIT_DATE: None,
                MdCrFieldMap.PRIORITY: None,
                MdCrFieldMap.CUSTOMER: "OPPO",
                MdCrFieldMap.COUNTRY: "China",
                MdCrFieldMap.OPERATOR: "CMCC",
                MdCrFieldMap.CR_CLASS: None,
                MdCrFieldMap.STATE: None,
                MdCrFieldMap.RESOLUTION: None,
                MdCrFieldMap.ASSIGNEE_DEPT: None,
                MdCrFieldMap.RESOLVE_TIME: None,
                MdCrFieldMap.ASSIGNEE: "mtk10809"
            }, {
                MdCrFieldMap.CR_ID: "tstdb03618302",
                MdCrFieldMap.SUBMIT_DATE: None,
                MdCrFieldMap.PRIORITY: None,
                MdCrFieldMap.CUSTOMER: None,
                MdCrFieldMap.COUNTRY: "China",
                MdCrFieldMap.OPERATOR: "CMCC",
                MdCrFieldMap.CR_CLASS: None,
                MdCrFieldMap.STATE: None,
                MdCrFieldMap.RESOLUTION: None,
                MdCrFieldMap.ASSIGNEE_DEPT: None,
                MdCrFieldMap.RESOLVE_TIME: None,
                MdCrFieldMap.ASSIGNEE: "mtk10809"
            }
        ]
        test_result = self.gen_report_service.get_cr_info_by_current_sync_job_id(
            cr_id_list)
        self.assertEqual(len(test_result), len(expected_result))
        self.assertEqual(
            test_result[0][MdCrFieldMap.CR_ID], expected_result[0][MdCrFieldMap.CR_ID])
        self.assertEqual(
            test_result[1][MdCrFieldMap.CR_ID], expected_result[1][MdCrFieldMap.CR_ID])

    def test_gen_wwstatistic_top10_raw(self):
        self.gen_report_service.cr_info = [
            {
                MdCrFieldMap.CR_ID: "tstdb03618301",
                MdCrFieldMap.SUBMIT_DATE: datetime.datetime(2015, 1, 12, 23, 9, 12, 946118),
                MdCrFieldMap.PRIORITY: "0.Urgent",
                MdCrFieldMap.CUSTOMER: "FOXCONN_FIH",
                MdCrFieldMap.COUNTRY: "China",
                MdCrFieldMap.OPERATOR: "CMCC"
            }, {
                MdCrFieldMap.CR_ID: "tstdb03618302",
                MdCrFieldMap.SUBMIT_DATE: datetime.datetime(2015, 1, 12, 23, 9, 12, 946118),
                MdCrFieldMap.PRIORITY: "0.Urgent",
                MdCrFieldMap.CUSTOMER: "VIVO",
                MdCrFieldMap.COUNTRY: "China",
                MdCrFieldMap.OPERATOR: "CMCC"
            }
        ]

        test_result = self.gen_report_service.gen_wwstatistic_top10_raw()
        expect_result_country = "{a}{delimit}{b}{delimit}{c}{delimit}{d}".format(
            delimit=MdMeta.Delimit, a="2015", b="Country", c="China", d="0.Urgent")
        expect_result_customer = "{a}{delimit}{b}{delimit}{c}{delimit}{d}".format(
            delimit=MdMeta.Delimit, a="2015", b="Customer", c="FOXCONN_FIH", d="0.Urgent")
        expect_result_operator = "{a}{delimit}{b}{delimit}{c}{delimit}{d}".format(
            delimit=MdMeta.Delimit, a="2015", b="Operator", c="CMCC", d="0.Urgent")
        self.assertDictContainsSubset({expect_result_country: 2}, test_result)
        self.assertDictContainsSubset({expect_result_customer: 1}, test_result)
        self.assertDictContainsSubset({expect_result_operator: 2}, test_result)

    def test_get_each_wwsta_top10_data(self):
        data = "{a}{delimit}{b}{delimit}{c}{delimit}{d}".format(
            delimit=MdMeta.Delimit, a="2015", b="Customer", c="OPPO", d="0.Urgent")
        cr_count = 2

        expected_resut = {
            WwStatisticTop10.DbFieldMap.CR_COUNT: 2,
            WwStatisticTop10.DbFieldMap.PERIOD: "2015",
            WwStatisticTop10.DbFieldMap.PRIORITY: "0.Urgent",
            WwStatisticTop10.DbFieldMap.TYPE: "Customer",
            WwStatisticTop10.DbFieldMap.TYPE_VALUE: "OPPO"
        }

        test_result = self.gen_report_service.get_each_wwsta_top10_data(
            data, cr_count)
        self.assertDictEqual(expected_resut, test_result)

    def test_gen_wwstatistic_map_raw(self):
        self.gen_report_service.cr_info = [
            {
                MdCrFieldMap.CR_ID: "tstdb03618301",
                MdCrFieldMap.SUBMIT_DATE: datetime.datetime(2015, 1, 12, 23, 9, 12, 946118),
                MdCrFieldMap.WW_COUNTRY: "China",
                MdCrFieldMap.WW_OPERATOR: "CMCC",
                MdCrFieldMap.CR_CLASS: "New feature",
                MdCrFieldMap.STATE: "Closed",
                MdCrFieldMap.RESOLUTION: "",
                MdCrFieldMap.PRIORITY: CrPriority.Urgent
            }, {
                MdCrFieldMap.CR_ID: "tstdb03618302",
                MdCrFieldMap.SUBMIT_DATE: datetime.datetime(2016, 1, 12, 23, 9, 12, 946118),
                MdCrFieldMap.WW_COUNTRY: "China",
                MdCrFieldMap.WW_OPERATOR: "CMCC",
                MdCrFieldMap.CR_CLASS: "Change feature",
                MdCrFieldMap.STATE: "Assigned",
                MdCrFieldMap.RESOLUTION: "",
                MdCrFieldMap.PRIORITY: CrPriority.Urgent
            }, {
                MdCrFieldMap.CR_ID: "tstdb03618303",
                MdCrFieldMap.SUBMIT_DATE: datetime.datetime(2016, 1, 12, 23, 9, 12, 946118),
                MdCrFieldMap.WW_COUNTRY: "China",
                MdCrFieldMap.WW_OPERATOR: "China Unicom",
                MdCrFieldMap.CR_CLASS: "Bug",
                MdCrFieldMap.STATE: "Assigned",
                MdCrFieldMap.RESOLUTION: "Completed",
                MdCrFieldMap.PRIORITY: CrPriority.Medium
            }, {
                MdCrFieldMap.CR_ID: "tstdb03618304",
                MdCrFieldMap.SUBMIT_DATE: datetime.datetime(2016, 1, 12, 23, 9, 12, 946118),
                MdCrFieldMap.WW_COUNTRY: "China",
                MdCrFieldMap.WW_OPERATOR: "CMCC",
                MdCrFieldMap.CR_CLASS: "Question",
                MdCrFieldMap.STATE: "Assigned",
                MdCrFieldMap.RESOLUTION: "",
                MdCrFieldMap.PRIORITY: CrPriority.Medium
            }, {
                MdCrFieldMap.CR_ID: "tstdb03618305",
                MdCrFieldMap.SUBMIT_DATE: datetime.datetime(2016, 1, 12, 23, 9, 12, 946118),
                MdCrFieldMap.WW_COUNTRY: "China",
                MdCrFieldMap.WW_OPERATOR: "CMCC",
                MdCrFieldMap.CR_CLASS: "Question",
                MdCrFieldMap.STATE: "Assigned",
                MdCrFieldMap.RESOLUTION: "",
                MdCrFieldMap.PRIORITY: CrPriority.Urgent
            }, {
                MdCrFieldMap.CR_ID: "tstdb03618306",
                MdCrFieldMap.SUBMIT_DATE: datetime.datetime(2016, 1, 12, 23, 9, 12, 946118),
                MdCrFieldMap.WW_COUNTRY: "China",
                MdCrFieldMap.WW_OPERATOR: "CMCC",
                MdCrFieldMap.CR_CLASS: "Question",
                MdCrFieldMap.STATE: "Assigned",
                MdCrFieldMap.RESOLUTION: "",
                MdCrFieldMap.PRIORITY: CrPriority.Urgent
            }

        ]

        test_result = self.gen_report_service.gen_wwstatistic_map_raw()
        expected_result = {'Resolved%%2015%%China%%CMCC%%New feature': {'cr_count': 1, 'urgent_cr_count': 1},
                           'Open%%2016%%China%%CMCC%%Change feature': {'cr_count': 1, 'urgent_cr_count': 1},
                           'Open%%2016%%China%%China Unicom%%New bug': {'cr_count': 1},
                           'Open%%2016%%China%%CMCC%%Non-bug': {'cr_count': 3, 'urgent_cr_count': 2}
                           }

        self.assertDictContainsSubset(expected_result, test_result)

    def test_get_each_wwsta_map_data(self):
        data = "{a}{delimit}{b}{delimit}{c}{delimit}{d}{delimit}{e}".format(
            delimit=MdMeta.Delimit, a="Resolved", b="2017", c="Indonesia", d="Others", e="Question")
        cr_count = 1
        urgent_cr_count = 1

        expected_resut = {
            WwStaMap.DbFieldMap.CR_COUNT: 1,
            WwStaMap.DbFieldMap.STATE: "Resolved",
            WwStaMap.DbFieldMap.PERIOD: "2017",
            WwStaMap.DbFieldMap.COUNTRY: "Indonesia",
            WwStaMap.DbFieldMap.OPERATOR: "Others",
            WwStaMap.DbFieldMap.MD_CLASS: "Question",
            WwStaMap.DbFieldMap.URGENT_COUNT: 1,
        }

        test_result = self.gen_report_service.get_each_wwsta_map_data(
            data, cr_count, urgent_cr_count)
        self.assertDictEqual(expected_resut, test_result)

    def test_gen_resolved_eservices_raw(self):
        self.gen_report_service.cr_info = [
            {
                MdCrFieldMap.CR_ID: "tstdb03618301",
                MdCrFieldMap.ASSIGNEE: "mtk10809",
                MdCrFieldMap.CUSTOMER: "OPPO",
                MdCrFieldMap.RESOLVE_DATE: datetime.datetime(2017, 1, 12, 23, 9, 12, 946118),
                MdCrFieldMap.PRIORITY: "0.Urgent",
                MdCrFieldMap.RESOLVE_TIME: 10,
                MdCrFieldMap.STATE: MdState.Resolved.Verified.value
            }, {
                MdCrFieldMap.CR_ID: "tstdb03618302",
                MdCrFieldMap.ASSIGNEE: "mtk08298",
                MdCrFieldMap.CUSTOMER: "OPPO",
                MdCrFieldMap.RESOLVE_DATE: datetime.datetime(2017, 10, 18, 23, 9, 12, 946118),
                MdCrFieldMap.PRIORITY: "1.High",
                MdCrFieldMap.RESOLVE_TIME: 5,
                MdCrFieldMap.STATE: MdState.Resolved.Closed.value
            }, {
                MdCrFieldMap.CR_ID: "tstdb03618303",
                MdCrFieldMap.ASSIGNEE: "mtk08298",
                MdCrFieldMap.CUSTOMER: "OPPO",
                MdCrFieldMap.RESOLVE_DATE: datetime.datetime(2017, 1, 17, 23, 9, 12, 946118),
                MdCrFieldMap.PRIORITY: "1.High",
                MdCrFieldMap.RESOLVE_TIME: 7,
                MdCrFieldMap.STATE: MdState.Resolved.Closed.value
            }, {
                MdCrFieldMap.CR_ID: "tstdb03618303",
                MdCrFieldMap.ASSIGNEE: "mtk08298",
                MdCrFieldMap.CUSTOMER: "OPPO",
                MdCrFieldMap.RESOLVE_DATE: datetime.datetime(2017, 1, 17, 23, 9, 12, 946118),
                MdCrFieldMap.PRIORITY: "1.High",
                MdCrFieldMap.RESOLVE_TIME: 7,
                MdCrFieldMap.STATE: MdState.Open.Reworking.value
            }
        ]

        self.gen_report_service.user_site = {"mtk10809": {"site": "MTK"}, "mtk08298": {
            "site": "MTK"}, "mtk04694": {"site": "MTK"}}

        test_result = self.gen_report_service.gen_resolved_eservices_raw()
        # only show 12 weekls for Week, 1 year for Month
        # state should only with MdState.Resolved
        expected_result = {
            "{a}{delimit}{b}{delimit}{c}{delimit}{d}{delimit}{e}".format(
                delimit=MdMeta.Delimit, a="Year", b="MTK", c="OPPO", d="2017", e="0.Urgent"): {"cr_count": 1, "time_count": 10},
            "{a}{delimit}{b}{delimit}{c}{delimit}{d}{delimit}{e}".format(
                delimit=MdMeta.Delimit, a="Year", b="MTK", c="OPPO", d="2017", e="1.High"): {"cr_count": 2, "time_count": 12},
            "{a}{delimit}{b}{delimit}{c}{delimit}{d}{delimit}{e}".format(
                delimit=MdMeta.Delimit, a="Month", b="MTK", c="OPPO", d="2017-01", e="1.High"): {"cr_count": 1, "time_count": 7},
            "{a}{delimit}{b}{delimit}{c}{delimit}{d}{delimit}{e}".format(
                delimit=MdMeta.Delimit, a="Month", b="MTK", c="OPPO", d="2017-01", e="0.Urgent"): {"cr_count": 1, "time_count": 10},
            "{a}{delimit}{b}{delimit}{c}{delimit}{d}{delimit}{e}".format(
                delimit=MdMeta.Delimit, a="Month", b="MTK", c="OPPO", d="2017-10", e="1.High"): {"cr_count": 1, "time_count": 5},
            "{a}{delimit}{b}{delimit}{c}{delimit}{d}{delimit}{e}".format(
                delimit=MdMeta.Delimit, a="Week", b="MTK", c="OPPO", d="2017.w42", e="1.High"): {"cr_count": 1, "time_count": 5}
        }
        self.assertDictEqual(test_result, expected_result)

    def test_get_each_resolved_eservices_data(self):
        data = "{a}{delimit}{b}{delimit}{c}{delimit}{d}{delimit}{e}".format(
            delimit=MdMeta.Delimit, a="Month", b="MTK", c="OPPO", d="2015-01", e="1.High")
        details = {"cr_count": 1,
                   "time_count": 14}

        expected_resut = {
            ResolvedEs.DbFieldMap.TYPE: "Month",
            ResolvedEs.DbFieldMap.SITE: "MTK",
            ResolvedEs.DbFieldMap.CUSTOMER: "OPPO",
            ResolvedEs.DbFieldMap.PERIOD: "2015-01",
            ResolvedEs.DbFieldMap.PRIORITY: "1.High",
            ResolvedEs.DbFieldMap.CR_COUNT: details.get("cr_count", 0),
            ResolvedEs.DbFieldMap.RESOLVE_TIME_COUNT: details.get(
                "time_count", 0)
        }

        test_result = self.gen_report_service.get_each_resolved_eservices_data(
            data, details)
        self.assertDictEqual(expected_resut, test_result)

    def test_get_stay_submitted_define(self):
        days = 0
        expected_result = "<1W"
        test_result = self.gen_report_service.get_stay_submitted_define(days)
        self.assertEqual(expected_result, test_result)

        days = 7
        expected_result = "1W-2W"
        test_result = self.gen_report_service.get_stay_submitted_define(days)
        self.assertEqual(expected_result, test_result)

        days = 14
        expected_result = "2W-4W"
        test_result = self.gen_report_service.get_stay_submitted_define(days)
        self.assertEqual(expected_result, test_result)

        days = 28
        expected_result = "1-2Month"
        test_result = self.gen_report_service.get_stay_submitted_define(days)
        self.assertEqual(expected_result, test_result)

        days = 60
        expected_result = "1-2Month"
        test_result = self.gen_report_service.get_stay_submitted_define(days)
        self.assertEqual(expected_result, test_result)

        days = 61
        expected_result = ">2Month"
        test_result = self.gen_report_service.get_stay_submitted_define(days)
        self.assertEqual(expected_result, test_result)

    def test_gen_open_eservices_raw_1(self):
        self.gen_report_service.cr_info = [
            {
                MdCrFieldMap.CR_ID: "tstdb03618301",
                MdCrFieldMap.ASSIGNEE: "mtk10809",
                MdCrFieldMap.CUSTOMER: "OPPO",
                MdCrFieldMap.SUBMIT_DATE: datetime.datetime(2017, 1, 12, 23, 9, 12, 946118),
                MdCrFieldMap.PRIORITY: "0.Urgent",
                MdCrFieldMap.RESOLVE_TIME: 10,
                MdCrFieldMap.STATE: MdState.Resolved.Verified.value
            }, {
                MdCrFieldMap.CR_ID: "tstdb03618302",
                MdCrFieldMap.ASSIGNEE: "mtk08298",
                MdCrFieldMap.CUSTOMER: "OPPO",
                MdCrFieldMap.SUBMIT_DATE: datetime.datetime(2017, 10, 18, 23, 9, 12, 946118),
                MdCrFieldMap.PRIORITY: "1.High",
                MdCrFieldMap.RESOLVE_TIME: 5,
                MdCrFieldMap.STATE: MdState.Resolved.Closed.value
            }, {
                MdCrFieldMap.CR_ID: "tstdb03618303",
                MdCrFieldMap.ASSIGNEE: "mtk10809",
                MdCrFieldMap.CUSTOMER: "OPPO",
                MdCrFieldMap.SUBMIT_DATE: datetime.datetime(2017, 1, 17, 23, 9, 12, 946118),
                MdCrFieldMap.PRIORITY: "1.High",
                MdCrFieldMap.RESOLVE_TIME: 7,
                MdCrFieldMap.STATE: MdState.Open.Assigned.value
            }, {
                MdCrFieldMap.CR_ID: "tstdb03618303",
                MdCrFieldMap.ASSIGNEE: "mtk08298",
                MdCrFieldMap.CUSTOMER: "OPPO",
                MdCrFieldMap.SUBMIT_DATE: datetime.datetime(2017, 1, 17, 23, 9, 12, 946118),
                MdCrFieldMap.PRIORITY: "1.High",
                MdCrFieldMap.RESOLVE_TIME: 8,
                MdCrFieldMap.STATE: MdState.Open.Reworking.value
            }
        ]
        self.gen_report_service.user_site = {"mtk10809": {"site": "MTK"}, "mtk08298": {
            "site": "MTI"}, "mtk04694": {"site": "MTK"}}

        expected_result = {
            "{site}{delimit}{cus}{delimit}{stay}{delimit}{priority}".format(
                delimit=MdMeta.Delimit, site="MTK", cus="OPPO", stay=">2Month", priority="1.High"): 1,
            "{site}{delimit}{cus}{delimit}{stay}{delimit}{priority}".format(
                delimit=MdMeta.Delimit, site="MTI", cus="OPPO", stay=">2Month", priority="1.High"): 1
        }

        test_result = self.gen_report_service.gen_open_eservices_raw()
        self.assertDictEqual(test_result, expected_result)

    def test_gen_ces_raw(self):
        self.gen_report_service.cr_info = [
            {
                MdCrFieldMap.CR_ID: "tstdb03618301",
                MdCrFieldMap.PRIORITY: "0.Urgent",
                MdCrFieldMap.OPERATOR: "Idea",
                MdCrFieldMap.COUNTRY: "India",
                MdCrFieldMap.STATE: MdState.Open.Assigned.value
            }, {
                MdCrFieldMap.CR_ID: "tstdb03618302",
                MdCrFieldMap.PRIORITY: "1.High",
                MdCrFieldMap.OPERATOR: "Airtel",
                MdCrFieldMap.COUNTRY: "India",
                MdCrFieldMap.STATE: MdState.Open.Assigned.value
            }, {
                MdCrFieldMap.CR_ID: "tstdb03618303",
                MdCrFieldMap.PRIORITY: "0.Urgent",
                MdCrFieldMap.OPERATOR: "Reliance Jio",
                MdCrFieldMap.COUNTRY: "India",
                MdCrFieldMap.STATE: MdState.Open.Reworking.value
            }, {
                MdCrFieldMap.CR_ID: "tstdb03618304",
                MdCrFieldMap.PRIORITY: "2.Medium",
                MdCrFieldMap.OPERATOR: "Airtel",
                MdCrFieldMap.COUNTRY: "India",
                MdCrFieldMap.STATE: MdState.Open.Reworking.value
            }, {
                MdCrFieldMap.CR_ID: "tstdb03618305",
                MdCrFieldMap.PRIORITY: "2.Medium",
                MdCrFieldMap.OPERATOR: "Airtel",
                MdCrFieldMap.COUNTRY: "India",
                MdCrFieldMap.STATE: MdState.Open.Submitted.value
            }
        ]

        expected_result = {
            "{country}{delimit}{operator}{delimit}{priority}".format(
                delimit=MdMeta.Delimit, country="India", operator="Idea", priority="0.Urgent"): 1,
            "{country}{delimit}{operator}{delimit}{priority}".format(
                delimit=MdMeta.Delimit, country="India", operator="Airtel", priority="1.High"): 1,
            "{country}{delimit}{operator}{delimit}{priority}".format(
                delimit=MdMeta.Delimit, country="India", operator="Reliance Jio", priority="0.Urgent"): 1,
            "{country}{delimit}{operator}{delimit}{priority}".format(
                delimit=MdMeta.Delimit, country="India", operator="Airtel", priority="2.Medium"): 2
        }

        test_result = self.gen_report_service.gen_ces_raw()
        self.assertDictEqual(test_result, expected_result)

    def test_get_each_ces_data(self):
        data = "{country}{delimit}{operator}{delimit}{priority}".format(
            delimit=MdMeta.Delimit, country="India", operator="Airtel", priority="1.High")
        cr_count = 2

        expected_resut = {
            Ces.DbFieldMap.CR_COUNT: 2,
            Ces.DbFieldMap.PRIORITY: "1.High",
            Ces.DbFieldMap.OPERATOR: "Airtel",
            Ces.DbFieldMap.COUNTRY: "India"
        }

        test_result = self.gen_report_service.get_each_ces_data(data, cr_count)
        self.assertDictEqual(expected_resut, test_result)

    def test_get_hw_prj_info_in_mytodo(self):
        hw_prj_id = "a0exxxxxxxx"
        hw_type = "Operator"
        operator = "CMCC"
        company = "VIVO"
        platform = "MT9999"
        is_completed = "0"
        t_id = DbTableHelper.get_crm_hw_prj_id(hw_prj_id, hw_type, operator)

        CrmHwProject.objects.create(
            id=t_id, hw_project_id=hw_prj_id, hw_type=hw_type, operator=operator,
            company=company, platform=platform, completed=is_completed, is_active=1)

        expected_result = [{
            CrmHwPrj.DbFieldMap.ID: t_id,
            CrmHwPrj.DbFieldMap.HW_PRJ_ID: hw_prj_id,
            CrmHwPrj.DbFieldMap.HW_TYPE: hw_type,
            CrmHwPrj.DbFieldMap.OPERATOR: operator,
            CrmHwPrj.DbFieldMap.IS_COMPLETED: is_completed,
            CrmHwPrj.DbFieldMap.PLATFORM: platform,
            CrmHwPrj.DbFieldMap.COMPANY: company,
            CrmHwPrj.DbFieldMap.START_DATE: None,
            CrmHwPrj.DbFieldMap.END_DATE: None
        }]
        test_result = self.gen_report_service.get_hw_prj_info_in_mytodo()
        self.assertEqual(test_result, expected_result)

    def test_get_period_week(self):
        is_completed_yes = "1"
        is_completed_no = "0"
        start_date = datetime.datetime(2017, 1, 10)
        end_date = datetime.datetime(2018, 12, 10)

        # for is_completed = 1, normal case
        expected_year = "2018"
        expected_week = "W18.50"
        (test_year, test_week) = self.gen_report_service.get_period_week(
            is_completed_yes, start_date, end_date)
        self.assertEqual(expected_year, test_year)
        self.assertEqual(expected_week, test_week)

        # for is_completed = 1, no end_date case
        expected_year = None
        expected_week = None
        (test_year, test_week) = self.gen_report_service.get_period_week(
            is_completed_yes, start_date, None)
        self.assertEqual(expected_year, test_year)
        self.assertEqual(expected_week, test_week)

        # for is_completed = 0, normal case
        expected_year = "2017"
        expected_week = "W17.02"
        (test_year, test_week) = self.gen_report_service.get_period_week(
            is_completed_no, start_date, end_date)
        self.assertEqual(expected_year, test_year)
        self.assertEqual(expected_week, test_week)

        # for is_completed = 0, no start_date case
        expected_year = None
        expected_week = None
        (test_year, test_week) = self.gen_report_service.get_period_week(
            is_completed_no, None, end_date)
        self.assertEqual(expected_year, test_year)
        self.assertEqual(expected_week, test_week)

    def test_get_urgent_cr_count_by_hw_prj(self):
        hw_prj_id = "a0E999999"
        operator = "CMCC"

        activity = Activity.objects.create(
            activity_id=MdMeta.ActivityId, active=1)

        # valid cr
        Cr.objects.create(cr_id="tstdb00000001", priority=CrPriority.Urgent,
                          hw_project_id=hw_prj_id, is_active=1, state=MdState.Open.Submitted.value, md_info_op_name=operator)
        Cr.objects.create(cr_id="tstdb00000005", priority=CrPriority.Urgent,
                          hw_project_id=hw_prj_id, is_active=1, state=MdState.Open.Working.value, md_info_op_name=operator)
        # invalid cr
        Cr.objects.create(cr_id="tstdb00000002", priority=CrPriority.Medium,
                          hw_project_id=hw_prj_id, is_active=1, state=MdState.Open.Submitted.value, md_info_op_name=operator)
        Cr.objects.create(cr_id="tstdb00000003", priority=CrPriority.Urgent,
                          hw_project_id=hw_prj_id, is_active=1, state=MdState.Resolved.Closed.value, md_info_op_name=operator)
        Cr.objects.create(cr_id="tstdb00000004", priority=CrPriority.Urgent,
                          hw_project_id=hw_prj_id, is_active=0, state=MdState.Open.Assigned)

        ActivityCr.objects.create(id="{}_{}".format(
            MdMeta.ActivityId, "tstdb00000001"), cr_id="tstdb00000001", active=1, activity=activity)
        ActivityCr.objects.create(id="{}_{}".format(
            MdMeta.ActivityId, "tstdb00000005"), cr_id="tstdb00000005", active=1, activity=activity)
        ActivityCr.objects.create(id="{}_{}".format(
            MdMeta.ActivityId, "tstdb00000002"), cr_id="tstdb00000002", active=0, activity=activity)
        ActivityCr.objects.create(id="{}_{}".format(
            MdMeta.ActivityId, "tstdb00000003"), cr_id="tstdb00000003", active=1, activity=activity)
        ActivityCr.objects.create(id="{}_{}".format(
            MdMeta.ActivityId, "tstdb00000004"), cr_id="tstdb00000004", active=1, activity=activity)
        expected_result = 2
        test_result = self.gen_report_service.get_urgent_cr_count_by_hw_prj(
            hw_prj_id, operator)
        self.assertEqual(expected_result, test_result)

    def test_gen_prj_status_raw(self):
        self.gen_report_service.hw_prj_info = [
            {
                CrmHwPrj.DbFieldMap.ID: "a0E00001_Operator",
                CrmHwPrj.DbFieldMap.HW_PRJ_ID: "a0E00001",
                CrmHwPrj.DbFieldMap.HW_TYPE: "Operator",
                CrmHwPrj.DbFieldMap.OPERATOR: "CMCC",
                CrmHwPrj.DbFieldMap.IS_COMPLETED: "1",
                CrmHwPrj.DbFieldMap.PLATFORM: "MT9999",
                CrmHwPrj.DbFieldMap.COMPANY: "VIVO",
                CrmHwPrj.DbFieldMap.START_DATE: datetime.datetime(2017, 1, 18, 23, 9, 12, 946118),
                CrmHwPrj.DbFieldMap.END_DATE: datetime.datetime(
                    2017, 12, 31, 23, 9, 12, 946118)
            },
            {
                CrmHwPrj.DbFieldMap.ID: "a0E00002_Operator",
                CrmHwPrj.DbFieldMap.HW_PRJ_ID: "a0E00002",
                CrmHwPrj.DbFieldMap.HW_TYPE: "Operator",
                CrmHwPrj.DbFieldMap.OPERATOR: "CMCC",
                CrmHwPrj.DbFieldMap.IS_COMPLETED: "1",
                CrmHwPrj.DbFieldMap.PLATFORM: "MT9999",
                CrmHwPrj.DbFieldMap.COMPANY: "VIVO",
                CrmHwPrj.DbFieldMap.START_DATE: datetime.datetime(2017, 5, 18, 23, 9, 12, 946118),
                CrmHwPrj.DbFieldMap.END_DATE: datetime.datetime(
                    2017, 12, 31, 23, 9, 12, 946118)
            },
            {
                CrmHwPrj.DbFieldMap.ID: "a0E00003_Operator",
                CrmHwPrj.DbFieldMap.HW_PRJ_ID: "a0E00003",
                CrmHwPrj.DbFieldMap.HW_TYPE: "Operator",
                CrmHwPrj.DbFieldMap.OPERATOR: "CMCC",
                CrmHwPrj.DbFieldMap.IS_COMPLETED: "0",
                CrmHwPrj.DbFieldMap.PLATFORM: "MT9999",
                CrmHwPrj.DbFieldMap.COMPANY: "SONY",
                CrmHwPrj.DbFieldMap.START_DATE: datetime.datetime(2017, 12, 31, 23, 9, 12, 946118),
                CrmHwPrj.DbFieldMap.END_DATE: datetime.datetime(
                    2018, 12, 18, 23, 9, 12, 946118)
            }
        ]

        activity = Activity.objects.create(
            activity_id=MdMeta.ActivityId, active=1)

        Cr.objects.create(cr_id="tstdb00000001", priority=CrPriority.Urgent,
                          hw_project_id="a0E00001", is_active=1, state=MdState.Open.Submitted.value, md_info_op_name="CMCC")
        Cr.objects.create(cr_id="tstdb00000002", priority=CrPriority.Urgent,
                          hw_project_id="a0E00001", is_active=1, state=MdState.Open.Submitted.value, md_info_op_name="CMCC")
        Cr.objects.create(cr_id="tstdb00000003", priority=CrPriority.Urgent,
                          hw_project_id="a0E00001", is_active=1, state=MdState.Open.Working.value, md_info_op_name="CMCC")

        ActivityCr.objects.create(id="{}_{}".format(
            MdMeta.ActivityId, "tstdb00000001"), cr_id="tstdb00000001", active=1, activity=activity)
        ActivityCr.objects.create(id="{}_{}".format(
            MdMeta.ActivityId, "tstdb00000002"), cr_id="tstdb00000002", active=1, activity=activity)
        ActivityCr.objects.create(id="{}_{}".format(
            MdMeta.ActivityId, "tstdb00000003"), cr_id="tstdb00000003", active=1, activity=activity)

        self.gen_report_service.op_area_info = {"CMCC": "Asia", "TIM": "EU",
                                                "TWN": "Asia", "Ufone": "Asia", "VideoTron": "North A"}

        combo_key1 = "{operator}{delimit}{completed}{delimit}{platform}{delimit}{company}{delimit}{period_week}{delimit}{period_year}{delimit}{area}".format(
            delimit=MdMeta.Delimit, operator="CMCC", completed=0, platform="MT9999", company="SONY", period_week="W17.53", period_year="2017", area="Asia")
        combo_key2 = "{operator}{delimit}{completed}{delimit}{platform}{delimit}{company}{delimit}{period_week}{delimit}{period_year}{delimit}{area}".format(
            delimit=MdMeta.Delimit, operator="CMCC", completed=1, platform="MT9999", company="VIVO", period_week="W17.53", period_year="2017", area="Asia")
        expected_result = {
            combo_key1: {'prj_count': 1, 'will_kickoff_count': 1},
            combo_key2: {'prj_count': 2, 'u_cr_count': 3}
        }

        test_result = self.gen_report_service.gen_prj_status_raw(
            MdHwPrjType.Operator)
        self.assertDictEqual(test_result, expected_result)

    def test_get_each_op_cert_data(self):
        data = "{operator}{delimit}{completed}{delimit}{platform}{delimit}{company}{delimit}{period_week}{delimit}{period_year}{delimit}{area}".format(
            delimit=MdMeta.Delimit, operator="CMCC", completed=0, platform="MT9999", company="SONY", period_week="W17.53", period_year="2017", area="Asia")

        details = {
            "prj_count": 1,
            "will_kickoff_count": 2,
            "u_cr_count": 3
        }

        expected_resut = {
            OpCert.DbFieldMap.OPERATOR: "CMCC",
            OpCert.DbFieldMap.AREA: "Asia",
            OpCert.DbFieldMap.IS_COMPLETED: "0",
            OpCert.DbFieldMap.PLATFORM: "MT9999",
            OpCert.DbFieldMap.COMPANY: "SONY",
            OpCert.DbFieldMap.PERIOD_WEEK: "W17.53",
            OpCert.DbFieldMap.PERIOD_YEAR: "2017",
            OpCert.DbFieldMap.PROJECT_COUNT: details.get("prj_count", 0),
            OpCert.DbFieldMap.WILL_KICKOFF_PROJECT_COUNT: details.get("will_kickoff_count", 0),
            OpCert.DbFieldMap.URGENT_CR_COUNT: details.get("u_cr_count", 0)
        }

        test_result = self.gen_report_service.get_each_op_cert_data(
            data, details)
        self.assertDictEqual(expected_resut, test_result)

    def test_get_user_site(self):
        self.gen_report_service.user_site = {"mtk10809": {"site": "MTK"}, "mtk08298": {
            "site": "MTK"}, "mtk04694": {"site": "MTK"}}

        user = "mtk10809"
        expected_result = "MTK"
        test_result_ = self.gen_report_service.get_user_site(user)
        self.assertEqual(expected_result, test_result_)

        user = "cpm_temp"
        expected_result = None
        test_result_ = self.gen_report_service.get_user_site(user)
        self.assertEqual(expected_result, test_result_)

    def test_get_combo_key_by_hw_type(self):
        hw_type = MdHwPrjType.FTA
        operator = "CMCC"
        is_completed = "1"
        platform = "MT1234"
        company = "SONY"
        period_week = "W18.01"
        period_year = "2018"
        area = "Asia"
        expected_result = "1%%MT1234%%SONY%%W18.01%%2018"
        test_result = self.gen_report_service.get_combo_key_by_hw_type(
            hw_type, operator, is_completed, platform, company, period_week, period_year, area)
        self.assertEqual(expected_result, test_result)

        hw_type = MdHwPrjType.Operator
        expected_result = "CMCC%%1%%MT1234%%SONY%%W18.01%%2018%%Asia"
        test_result = self.gen_report_service.get_combo_key_by_hw_type(
            hw_type, operator, is_completed, platform, company, period_week, period_year, area)
        self.assertEqual(expected_result, test_result)

    def test_get_each_fta_data(self):
        data = "{completed}{delimit}{platform}{delimit}{company}{delimit}{period_week}{delimit}{period_year}".format(
            delimit=MdMeta.Delimit, completed=0, platform="MT9999", company="SONY", period_week="W17.53", period_year="2017")

        details = {
            "prj_count": 1,
            "will_kickoff_count": 2,
            "u_cr_count": 3
        }

        expected_resut = {
            FTA.DbFieldMap.IS_COMPLETED: "0",
            FTA.DbFieldMap.PLATFORM: "MT9999",
            FTA.DbFieldMap.COMPANY: "SONY",
            FTA.DbFieldMap.PERIOD_WEEK: "W17.53",
            FTA.DbFieldMap.PERIOD_YEAR: "2017",
            FTA.DbFieldMap.PROJECT_COUNT: details.get("prj_count", 1),
            FTA.DbFieldMap.WILL_KICKOFF_PROJECT_COUNT: details.get("will_kickoff_count", 2),
            FTA.DbFieldMap.URGENT_CR_COUNT: details.get("u_cr_count", 3)
        }

        test_result = self.gen_report_service.get_each_fta_data(
            data, details)
        self.assertDictEqual(expected_resut, test_result)
