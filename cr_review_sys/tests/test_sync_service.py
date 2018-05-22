'''
Created on Sep 26, 2017

@author: mtk06979
'''
import datetime
import logging

from django.test import TestCase

from cr_review_sys.const import HwPrjFieldMap, Const, WitsClan, CrMeta,\
    SyncControlTag, DeptsFieldMap, UsersFieldMap
from cr_review_sys.models import ActivityCr, SyncControl, Cr, CrmHwProject,\
    CrmHwProjectMilestone, SyncJob, Activity, Depts, Users, ActivityCategory
from cr_review_sys.services.sync_service import SyncService
from md_analysis.const import MdMeta
from my_to_do.util.date_helper import DateHelper
from my_to_do.util.db_table_helper import DbTableHelper


class SyncServiceTest(TestCase):

    def setUp(self):
        self.logger = logging.getLogger('aplogger')
        self.sync_service = SyncService()
        self.clan = "Staging_Area"
        self.db = "tstdb"
        self.last_sync_time = "2017-12-22 17:00:00"

        ActivityCr.objects.create(
            id="1_tstdb03618301_tstdb20171220000001", activity_id="1", cr_id="tstdb03618301", sync_job_id="tstdb20171220000001")
        ActivityCr.objects.create(
            id="2_tstdb03618302_tstdb20171220000001", activity_id="2", cr_id="tstdb03618302", sync_job_id="tstdb20171220000001")
        ActivityCr.objects.create(
            id="1_tstdb03618301_tstdb20171220000002", activity_id="1", cr_id="tstdb03618301", sync_job_id="tstdb20171220000002")
        ActivityCr.objects.create(
            id="2_tstdb03618302_tstdb20171220000002", activity_id="2", cr_id="tstdb03618302", sync_job_id="tstdb20171220000002")

    def test_getWitsId(self):
        test_result = self.sync_service.getWitsId("aaa", "bbb")
        self.assertEqual(test_result, "aaa_bbb")

    def test_getWitsObject(self):  # haven't fully test
        test_result = self.sync_service.getWitsObject(self.clan, self.db)
        self.assertIsNotNone(test_result)

    def test_getSyncControlId(self):
        clan = "Staging_Area"
        db = "tstdb"
        sync_type = "SyncCR"
        expected_result = "{}_{}_{}".format(clan, db, sync_type)
        test_result = self.sync_service.getSyncControlId(
            clan, db, sync_type)
        self.assertEqual(test_result, expected_result)

#     def test_sync_act_cr(self):  # haven't fully test
#         test_result = self.sync_service.sync_act_cr(self.clan, self.db)
#         self.assertNotEqual(test_result, [])

    def test_insert_act_cr(self):  # haven't test exception
        new_sync_job_id = "new_sync_job_id"
        db = 'ALPS'
        test_result = self.sync_service.insert_act_cr(
            "1", new_sync_job_id, ["cr1", "cr2", "cr3"], db)
        self.assertEqual(test_result, new_sync_job_id)

    def test_get_distinct_cr(self):
        valid_result = ["tstdb03618301", "tstdb03618302"]
        sync_job_id_list = ["tstdb20171220000001", "tstdb20171220000002"]
        test_result = self.sync_service.get_distinct_cr(sync_job_id_list)
        self.assertEqual(test_result, valid_result)

    def test_get_mytodo_crs(self):

        Cr.objects.create(cr_id="tstdb03618301")
        Cr.objects.create(cr_id="tstdb03618302")
        Cr.objects.create(cr_id="tstdb03618303")

        test_result = self.sync_service.get_mytodo_crs()
        self.assertEqual(
            test_result, ["tstdb03618301", "tstdb03618302", "tstdb03618303"])

    def test_check_hw_project_exist(self):
        hw_prj_id_non_exist = "a"
        hw_prj_id_exist = "b"
        hw_prj_list = ["b", "c", "d"]

        test_result = self.sync_service.check_hw_project_exist(
            hw_prj_id_non_exist, hw_prj_list)
        self.assertEqual(test_result, ["b", "c", "d", "a"])

        test_result = self.sync_service.check_hw_project_exist(
            hw_prj_id_exist, hw_prj_list)
        self.assertEqual(test_result, hw_prj_list)

    def test_get_last_sync_time(self):

        sync_id = self.clan + "_" + self.db + "_" + SyncControlTag.CR_INFO

        SyncControl.objects.create(id=sync_id, sync_value=self.last_sync_time)

        test_result = self.sync_service.get_last_sync_time(sync_id)
        self.assertEqual(test_result, self.last_sync_time)

    def test_get_last_sync_time_with_db_return_null(self):

        sync_id = self.clan + "_" + self.db + "_" + SyncControlTag.CR_INFO

        SyncControl.objects.create(id=sync_id, sync_value="")

        test_result = self.sync_service.get_last_sync_time(sync_id)
        self.assertIsNotNone(
            test_result, "with auto cal now - 1 day for last_sync_time")

    def test_get_distinct_hw_prj_id_by_cr(self):

        Cr.objects.create(cr_id="tstdb03618301", hw_project_id="001")
        Cr.objects.create(cr_id="tstdb03618302", hw_project_id="001")
        Cr.objects.create(cr_id="tstdb03618303", hw_project_id="003")
        Cr.objects.create(cr_id="tstdb03618304", hw_project_id="003")

        test_result = self.sync_service.get_distinct_hw_prj_id_by_cr(
            ["tstdb03618301", "tstdb03618302", "tstdb03618303", "tstdb03618304"])

        self.assertEqual(test_result, ["001", "003"])

    def test_cal_distinct_hw_prj_list(self):
        final_hw_list = ["a", "b", "c"]
        cal_hw_list = ["b", "c", "d", "e"]
        expected_result = ["a", "b", "c", "d", "e"]

        test_result = self.sync_service.cal_distinct_hw_prj_list(
            final_hw_list, cal_hw_list)

        self.assertEqual(test_result, expected_result)

    def test_create_hw_prj(self):
        create_list = [
            {'id': 'a0E9000001BhbMMEAZ_Operator', 'hw_project_id': 'a0E9000001BhbMMEAZ', 'hw_type': 'Operator',
                'completed': 1, 'start_date': '2016-05-16 00:00:00', 'end_date': None, 'operator': 'CMCC'},
            {'id': 'a0E9000001BhXmaEAF_Operator', 'hw_project_id': 'a0E9000001BhXmaEAF', 'hw_type': 'Operator',
                'completed': 0, 'start_date': '2016-04-11 00:00:00', 'operator': 'Vodafone'},
            {'id': 'a0E90000017XycZEAS_Operator', 'hw_project_id': 'a0E90000017XycZEAS', 'hw_type': 'Operator',
                'completed': 1, 'start_date': '2016-04-05 00:00:00', 'end_date': '2016-05-06 00:00:00', 'operator': 'Vodafone'}
        ]

        test_result = self.sync_service.create_hw_prj(create_list)
        self.assertEqual(test_result, True)

    def test_true_check_hw_prj_exist_in_mytodo(self):
        '''
        return True when hw_prj_id/hw_type exist
        '''
        hw_prj_id = "a0E9000001BhbMMEAZ"
        hw_type = "Operator"
        operator = "CMCC"
        t_id = DbTableHelper.get_crm_hw_prj_id(hw_prj_id, hw_type, operator)
        expected_result = True

        CrmHwProject.objects.create(id=t_id)
        test_result = self.sync_service.check_hw_prj_exist_in_mytodo(t_id)

        self.assertEqual(test_result, expected_result)

    def test_false_check_hw_prj_exist_in_mytodo(self):
        '''
        return False when hw_prj_id/hw_type not-exist
        '''
        hw_prj_id = "a0E9000001BhbMMEAZ"
        hw_type = "Operator"
        operator = "TelCel"
        t_id = DbTableHelper.get_crm_hw_prj_id(hw_prj_id, hw_type, operator)
        expected_result = False

        test_result = self.sync_service.check_hw_prj_exist_in_mytodo(t_id)

        self.assertEqual(test_result, expected_result)

    def test_true_check_hw_milestone_exist_in_mytodo(self):
        '''
        return True when hw_prj_id/hw_type/milestone exist
        '''
        hw_prj_id = "a0E9000001BhbMMEAZ"
        hw_type = "Operator"
        milestone_id = "123456"
        operator = "CMCC"
        t_id = DbTableHelper.get_crm_hw_prj_milestone_id(
            hw_prj_id, hw_type, milestone_id, operator)
        expected_result = True

        CrmHwProjectMilestone.objects.create(
            id=t_id, hw_project_id=hw_prj_id, type=hw_type, milestone_id=milestone_id, operator=operator)
        test_result = self.sync_service.check_hw_milestone_exist_in_mytodo(
            t_id)

        self.assertEqual(test_result, expected_result)

    def test_false_check_hw_milestone_exist_in_mytodo(self):
        '''
        return False when hw_prj_id/hw_type/milestone exist
        '''
        hw_prj_id = "a0E9000001BhbMMEAZ"
        hw_type = "Operator"
        milestone_id = "123456"
        operator = "CMCC"
        t_id = DbTableHelper.get_crm_hw_prj_milestone_id(
            hw_prj_id, hw_type, milestone_id, operator)

        expected_result = False

        test_result = self.sync_service.check_hw_milestone_exist_in_mytodo(
            t_id)

        self.assertEqual(test_result, expected_result)

    def test_check_cr_bu_type(self):
        cr_id = "tstdb03618301"
        sync_job_id = "tstdb20171220000001"
        expected_result = True

        SyncJob.objects.create(activity_id=MdMeta.ActivityId,
                               sync_job_id=sync_job_id, is_active=Const.IS_ACTIVE)

        t_id = DbTableHelper.get_act_cr_id(MdMeta.ActivityId, cr_id)
        ActivityCr.objects.create(activity_id=MdMeta.ActivityId, id=t_id,
                                  sync_job_id=sync_job_id, cr_id=cr_id)

        test_result = self.sync_service.check_cr_bu_type(cr_id)
        self.assertEqual(test_result, expected_result)

    def test_update_hw_prj(self):
        hw_prj_id = "a0E9000001BhbMMEAZ"
        hw_type = "Operator"
        operator = "CMCC"
        t_id = DbTableHelper.get_crm_hw_prj_id(hw_prj_id, hw_type, operator)
        data = {
            "id": t_id,
            "hw_project_id": hw_prj_id,
            "hw_type": hw_type,
            "operator": operator,
            "fta": "",
            "start_date": datetime.datetime(2017, 12, 30),
            "end_date": datetime.datetime(2018, 12, 30),
            "completed": 0,
            "is_active": 1
        }

        CrmHwProject.objects.create(
            id=t_id, hw_project_id=hw_prj_id, hw_type=hw_type)

        expected_result = True
        test_result = self.sync_service.update_hw_prj(t_id, **data)
        self.assertEqual(test_result, expected_result)

    def test_get_create_info_for_hw_prj(self):
        hw_prj_id = "a0E9000001BhbMMEAA"
        hw_type = "Operator"
        is_completed = 1
        operator = "CMCC"
        ori_data = {"PROJECT_ID": hw_prj_id, "TYPE": "fta", "START_DATE": datetime.datetime(
            2017, 12, 30), "END_DATE": datetime.datetime(2018, 1, 1), "IS_COMPLETED": is_completed, "OPERATOR": operator}

        hw_info_from_wits = {
            HwPrjFieldMap.HW_Project_Status: "Mass production",
            HwPrjFieldMap.Name: "Prj NAME",
            HwPrjFieldMap.Company: "VIVO",
            HwPrjFieldMap.SWPM_fullname: "Claire Hsieh",
            HwPrjFieldMap.Platform: "MT9999"
        }
        expected_result = {
            "id": DbTableHelper.get_crm_hw_prj_id(hw_prj_id, hw_type, operator),
            "hw_project_id": hw_prj_id,
            "hw_type": hw_type,
            "completed": is_completed,
            "is_active": 1,
            "operator": operator,
            'end_date': '2018-01-01',
            'start_date': '2017-12-30'
        }
        expected_result.update(hw_info_from_wits)
        test_result = self.sync_service.get_create_info_for_hw_prj(
            hw_type, ori_data, hw_info_from_wits)
        self.assertDictEqual(test_result, expected_result)

    def test_update_hw_prj_milestone(self):
        hw_prj_id = "51008"
        hw_type = "Operator"
        milestone_name = "test_milestone"
        operator = "TelCel"
        t_id = DbTableHelper.get_crm_hw_prj_milestone_id(
            hw_prj_id, hw_type, milestone_name, operator)
        data = {"start_date": datetime.datetime(2017, 12, 30), "end_date": datetime.datetime(
            2018, 12, 30), "is_active": "0", "with_vote": 1, "with_wfc": 0, "with_vilte": 1}

        CrmHwProjectMilestone.objects.create(
            id=t_id, hw_project_id=hw_prj_id, type=hw_type, milestone_name=milestone_name, operator=operator)

        expected_result = True
        test_result = self.sync_service.update_hw_prj_milestone(t_id, **data)
        self.assertEqual(expected_result, test_result)

    def test_check_json_format(self):
        test_str = ""
        test_result = self.sync_service.check_json_format(test_str)
        expected_result = False
        self.assertEqual(expected_result, test_result)

        test_str = '{"1":{"ALPS":"XXX/XXXX/XXX"}}'
        test_result = self.sync_service.check_json_format(test_str)
        expected_result = True
        self.assertEqual(expected_result, test_result)

    def test_get_acts_by_cat_type(self):
        act_cat_type = CrMeta.ACT_CAT_TYPE
        activity_cat_id = 1

        ActivityCategory.objects.create(
            activity_cat_id=activity_cat_id, act_cat_type=act_cat_type, active=1)
        Activity.objects.create(
            activity_id=1, activity_cat_id=1, db_scope='{"1":{"ALPS":"XXX/XXXX/XXX"}}', active=1)
        Activity.objects.create(
            activity_id=2, activity_cat_id=1, db_scope='{"2":{"ALPS":XXX/XXXX/XXX"}}', active=0)

        expected_result = {1: '{"1":{"ALPS":"XXX/XXXX/XXX"}}'}
        test_result = self.sync_service.get_acts_by_cat_type(act_cat_type)
        self.assertEqual(expected_result, test_result)

    def test_get_clan(self):
        wits_db = "ALPS"
        expected_result = WitsClan.ALPS
        test_result = self.sync_service.get_clan(wits_db)
        self.assertEqual(expected_result, test_result)

        wits_db = ""
        expected_result = None
        test_result = self.sync_service.get_clan(wits_db)
        self.assertEqual(expected_result, test_result)

    def test_insert_one_cr(self):  # haven't test exception
        cr_id = "ALPS00000001"
        cr_info = {"cr_id": cr_id}
        test_result = self.sync_service.insert_one_cr(cr_info)
        expected_result = True
        self.assertEqual(test_result, expected_result)

    def test_get_crs_while_list_by_act(self):
        activity_id = 1
        activity_cat_id = 1
        witsdb = "ALPS"
        expected_active_crs = ["ALPS00000001", "ALPS00000002", "ALPS00000003"]
        expected_disable_crs = ["ALPS00000004", "ALPS00000005", "ALPS00000006"]

        Activity.objects.create(
            activity_id=activity_id, activity_cat_id=activity_cat_id, db_scope='{"1":{"ALPS":"XXX/XXXX/XXX"}}')

        for cr in expected_active_crs:
            self.sync_service.insert_one_cr({"cr_id": cr})
            tmp_id = DbTableHelper.get_act_cr_id(activity_id, cr)
            ActivityCr.objects.create(
                id=tmp_id, activity_id=activity_id, cr_id=cr, active=1, cr_db=witsdb)

        for cr in expected_disable_crs:
            self.sync_service.insert_one_cr({"cr_id": cr})
            tmp_id = DbTableHelper.get_act_cr_id(activity_id, cr)
            ActivityCr.objects.create(
                id=tmp_id, activity_id=activity_id, cr_id=cr, active=0, cr_db=witsdb)

        (test_active_crs, test_disable_crs) = self.sync_service.get_crs_while_list_by_act(
            activity_id, witsdb)
        self.assertEqual(test_active_crs, expected_active_crs)
        self.assertEqual(test_disable_crs, expected_disable_crs)

    def test_check_cr_exist_in_mytodo(self):
        cr_id = "ALPS00000001"
        self.sync_service.insert_one_cr({"cr_id": cr_id})
        test_result = self.sync_service.check_cr_exist_in_mytodo(cr_id)
        expected_result = True
        self.assertEqual(test_result, expected_result)

        cr_id = "ALPS00000002"
        test_result = self.sync_service.check_cr_exist_in_mytodo(cr_id)
        expected_result = False
        self.assertEqual(test_result, expected_result)

    def test_handle_act_crs(self):
        act_id = 1
        sync_type = CrMeta.PREFIX_SYNC_JOB_ID
        witsdb = "ALPS"
        clan = self.sync_service.get_clan(witsdb)
        wits_session = self.sync_service.getWitsObject(clan, witsdb)
        new_sync_job_id = DateHelper.get_new_sync_job_id(sync_type)
        disable_crs = ["ALPS03669364", "ALPS03667459"]
        new_act_crs = ["ALPS02723602", "ALPS02851662"]
        new_crs = ["ALPS03667454", "ALPS02738609"]

        for cr in new_crs:
            self.sync_service.insert_one_cr({"cr_id": cr})
            tmp_id = DbTableHelper.get_act_cr_id(act_id, cr)
            ActivityCr.objects.create(
                id=tmp_id, activity_id=act_id, cr_id=cr, active=1, cr_db=witsdb)

        for cr in disable_crs:
            self.sync_service.insert_one_cr({"cr_id": cr})
            tmp_id = DbTableHelper.get_act_cr_id(act_id, cr)
            ActivityCr.objects.create(
                id=tmp_id, activity_id=act_id, cr_id=cr, active=0, cr_db=witsdb)

        act_crs = disable_crs + new_crs + new_act_crs

        expected_result = True
        test_result = self.sync_service.handle_act_crs(
            wits_session, act_id, witsdb, act_crs, new_sync_job_id)
        self.assertEqual(test_result, expected_result)

    def test_handle_update_act_cr(self):
        act_id = 1
        witsdb = "ALPS"
        expected_disable_crs = ["ALPS03669364", "ALPS03667459"]
        expected_enable_crs = ["ALPS02723602", "ALPS02851662"]

        for cr in expected_enable_crs:
            self.sync_service.insert_one_cr({"cr_id": cr})
            tmp_id = DbTableHelper.get_act_cr_id(act_id, cr)
            ActivityCr.objects.create(
                id=tmp_id, activity_id=act_id, cr_id=cr, active=0, cr_db=witsdb)

        for cr in expected_disable_crs:
            self.sync_service.insert_one_cr({"cr_id": cr})
            tmp_id = DbTableHelper.get_act_cr_id(act_id, cr)
            ActivityCr.objects.create(
                id=tmp_id, activity_id=act_id, cr_id=cr, active=1, cr_db=witsdb)

        self.sync_service.handle_update_act_cr(
            act_id, expected_disable_crs, expected_enable_crs)

        (test_enable_crs, test_disable_crs) = self.sync_service.get_crs_while_list_by_act(
            act_id, witsdb)
        self.assertEqual(test_enable_crs, expected_enable_crs)
        self.assertEqual(test_disable_crs, expected_disable_crs)

    def test_handle_create_act_cr_fail(self):
        act_id = 1
        sync_type = CrMeta.PREFIX_SYNC_JOB_ID
        witsdb = "ALPS"
        clan = self.sync_service.get_clan(witsdb)
        wits_session = self.sync_service.getWitsObject(clan, witsdb)
        new_sync_job_id = DateHelper.get_new_sync_job_id(sync_type)
        whole_new_cr_list = ["ALPS03669364", "ALPS03667459"]
        new_act_cr_list = ["ALPS02723602", "ALPS02851662"]

        for cr in new_act_cr_list:
            self.sync_service.insert_one_cr({"cr_id": cr})
            tmp_id = DbTableHelper.get_act_cr_id(act_id, cr)
            ActivityCr.objects.create(
                id=tmp_id, activity_id=act_id, cr_id=cr, active=1, cr_db=witsdb)
        expected_result = False
        test_result = self.sync_service.handle_create_act_cr(
            wits_session, act_id, witsdb, new_sync_job_id, whole_new_cr_list, new_act_cr_list)
        self.assertEqual(test_result, expected_result)

    def test_handle_create_act_cr_success(self):
        act_id = 1
        sync_type = CrMeta.PREFIX_SYNC_JOB_ID
        witsdb = "ALPS"
        clan = self.sync_service.get_clan(witsdb)
        wits_session = self.sync_service.getWitsObject(clan, witsdb)
        new_sync_job_id = DateHelper.get_new_sync_job_id(sync_type)
        whole_new_cr_list = ["ALPS03669364", "ALPS03667459"]
        new_act_cr_list = ["ALPS02723602", "ALPS02851662"]

        for cr in new_act_cr_list:
            self.sync_service.insert_one_cr({"cr_id": cr})

        expected_result = True
        test_result = self.sync_service.handle_create_act_cr(
            wits_session, act_id, witsdb, new_sync_job_id, whole_new_cr_list, new_act_cr_list)
        self.assertEqual(test_result, expected_result)

    def test_create_act_cr_while_list_fail(self):
        act_id = 1
        sync_type = CrMeta.PREFIX_SYNC_JOB_ID
        witsdb = "ALPS"
        new_sync_job_id = DateHelper.get_new_sync_job_id(sync_type)
        whole_new_cr_list = ["ALPS03669364", "ALPS03667459"]

        for cr in whole_new_cr_list:
            tmp_id = DbTableHelper.get_act_cr_id(act_id, cr)
            ActivityCr.objects.create(
                id=tmp_id, activity_id=act_id, cr_id=cr, active=1, cr_db=witsdb)

        expected_result = False
        test_result = self.sync_service.create_act_cr_while_list(
            act_id, witsdb, whole_new_cr_list, new_sync_job_id)
        self.assertEqual(test_result, expected_result)

    def test_create_act_cr_while_list_success(self):
        act_id = 1
        sync_type = CrMeta.PREFIX_SYNC_JOB_ID
        witsdb = "ALPS"
        new_sync_job_id = DateHelper.get_new_sync_job_id(sync_type)
        whole_new_cr_list = ["ALPS03669364", "ALPS03667459"]

        expected_result = True
        test_result = self.sync_service.create_act_cr_while_list(
            act_id, witsdb, whole_new_cr_list, new_sync_job_id)
        self.assertEqual(test_result, expected_result)

    def test_format_odr_depts(self):
        depts = [{'DEPARTMENT_ID': '50159310', 'DEPARTMENT_NAME': 'EO/CEG', 'DEPARTMENT_SITE': 'MUS', 'DEPARTMENT_MANAGER': 'MTK30015', 'PARENT_DEPARTMENT': '50064810'},
                 {'DEPARTMENT_ID': '50159711', 'DEPARTMENT_NAME': 'EO/TBGMO', 'DEPARTMENT_SITE': 'MTB', 'DEPARTMENT_MANAGER': 'MTK10824', 'PARENT_DEPARTMENT': '50159710'}]
        expected_result = {'50159310': {DeptsFieldMap.DEPT_ID: '50159310', DeptsFieldMap.DEPT_MANGR: 'mtk30015', DeptsFieldMap.DEPT_NAME: 'EO/CEG', DeptsFieldMap.PARENT_DEPT: '50064810', DeptsFieldMap.SITE: 'MUS'},
                           '50159711': {DeptsFieldMap.DEPT_ID: '50159711', DeptsFieldMap.DEPT_MANGR: 'mtk10824', DeptsFieldMap.DEPT_NAME: 'EO/TBGMO', DeptsFieldMap.PARENT_DEPT: '50159710', DeptsFieldMap.SITE: 'MTB'}}
        test_result = self.sync_service.format_odr_depts(depts)
        self.assertDictEqual(test_result, expected_result)

    def test_get_mytodo_depts(self):
        dept_id = '50159310'
        dept_mangr = 'mtk30015'
        dept_name = 'EO/CEG'
        parent_dept = '50064810'
        site = 'MUS'
        Depts.objects.create(dept_id=dept_id, dept_mangr=dept_mangr,
                             dept_name=dept_name, parent_dept=parent_dept, site=site, is_active=1)
        expected_result = {dept_id: {DeptsFieldMap.DEPT_MANGR: dept_mangr, DeptsFieldMap.DEPT_NAME: dept_name,
                                     DeptsFieldMap.PARENT_DEPT: parent_dept, DeptsFieldMap.SITE: site, DeptsFieldMap.IS_ACTIVE: True}
                           }
        test_result = self.sync_service.get_mytodo_depts()
        self.assertDictEqual(test_result, expected_result)

    def test_format_odr_users(self):
        users = [{'EMPLOYEE_ID': 'MTK03384', 'ENGLISH_NAME': 'Ardigo Huang', 'EMAIL': 'ARDIGO.HUANG@MEDIATEK.COM', 'SITE': 'MTK', 'DEPARTMENT_ID': '50018958', 'STATUS': 'Active', 'DEPARTMENT_MANAGER': 'MTK03239', 'DEPARTMENT_NAME': 'CAI3/DP2/DM5'},
                 {'EMPLOYEE_ID': 'MTK03390', 'ENGLISH_NAME': 'Showmark Huang', 'EMAIL': 'SHOWMARK.HUANG@MEDIATEK.COM', 'SITE': 'MTK', 'DEPARTMENT_ID': '50231000', 'STATUS': 'Active', 'DEPARTMENT_MANAGER': 'MTK03937', 'DEPARTMENT_NAME': 'WCS/EPM/SM6'}]
        expected_result = {'mtk03384': {UsersFieldMap.LOGIN_NAME: 'mtk03384', UsersFieldMap.DEPT_ID: 50018958, UsersFieldMap.FULL_NAME: 'Ardigo Huang', UsersFieldMap.E_MAIL: 'ardigo.huang@mediatek.com', UsersFieldMap.IS_ACTIVE: True, UsersFieldMap.DEPT_NAME: 'CAI3/DP2/DM5', UsersFieldMap.SITE: 'MTK', UsersFieldMap.REPORTING_MANAGER: 'mtk03239'},
                           'mtk03390': {UsersFieldMap.LOGIN_NAME: 'mtk03390', UsersFieldMap.DEPT_ID: 50231000, UsersFieldMap.FULL_NAME: 'Showmark Huang', UsersFieldMap.E_MAIL: 'showmark.huang@mediatek.com', UsersFieldMap.IS_ACTIVE: True, UsersFieldMap.DEPT_NAME: 'WCS/EPM/SM6', UsersFieldMap.SITE: 'MTK', UsersFieldMap.REPORTING_MANAGER: 'mtk03937'}}
        test_result = self.sync_service.format_odr_users(users)
        self.assertDictEqual(test_result, expected_result)

    def test_success_create_users(self):
        new_users = ['mtk03384', 'mtk03390']
        wits_users = {'mtk03384': {UsersFieldMap.LOGIN_NAME: 'mtk03384', UsersFieldMap.DEPT_ID: 50018958, UsersFieldMap.FULL_NAME: 'Ardigo Huang', UsersFieldMap.E_MAIL: 'ardigo.huang@mediatek.com', UsersFieldMap.IS_ACTIVE: True, UsersFieldMap.DEPT_NAME: 'CAI3/DP2/DM5', UsersFieldMap.SITE: 'MTK', UsersFieldMap.REPORTING_MANAGER: 'mtk03239'},
                      'mtk03390': {UsersFieldMap.LOGIN_NAME: 'mtk03390', UsersFieldMap.DEPT_ID: 50231000, UsersFieldMap.FULL_NAME: 'Showmark Huang', UsersFieldMap.E_MAIL: 'showmark.huang@mediatek.com', UsersFieldMap.IS_ACTIVE: True, UsersFieldMap.DEPT_NAME: 'WCS/EPM/SM6', UsersFieldMap.SITE: 'MTK', UsersFieldMap.REPORTING_MANAGER: 'mtk03937'}}
        try:
            self.sync_service.create_users(new_users, **wits_users)
            assert True
        except Exception:
            assert False

    def test_fail_create_users(self):
        new_users = ['mtk03384', 'mtk03390']
        wits_users = {'mtk03384': {'UsersFieldMap.LOGIN_NAME': 'mtk03384', UsersFieldMap.DEPT_ID: 50018958, UsersFieldMap.FULL_NAME: 'Ardigo Huang', UsersFieldMap.E_MAIL: 'ardigo.huang@mediatek.com', UsersFieldMap.IS_ACTIVE: True, UsersFieldMap.DEPT_NAME: 'CAI3/DP2/DM5', UsersFieldMap.SITE: 'MTK', UsersFieldMap.REPORTING_MANAGER: 'mtk03239'},
                      'mtk03390': {UsersFieldMap.LOGIN_NAME: 'mtk03390', UsersFieldMap.DEPT_ID: 50231000, UsersFieldMap.FULL_NAME: 'Showmark Huang', UsersFieldMap.E_MAIL: 'showmark.huang@mediatek.com', UsersFieldMap.IS_ACTIVE: True, UsersFieldMap.DEPT_NAME: 'WCS/EPM/SM6', UsersFieldMap.SITE: 'MTK', UsersFieldMap.REPORTING_MANAGER: 'mtk03937'}}
        try:
            self.sync_service.create_users(new_users, **wits_users)
        except Exception:
            assert True

    def test_success_disable_users(self):
        disable_list = ['mtk10809']
        mytodo_users = {'mtk10809': {UsersFieldMap.DEPT_ID: None,
                                     UsersFieldMap.DEPT_NAME: 'WCS/EPM/SST3',
                                     UsersFieldMap.E_MAIL: 'claire.hsieh@mediatek.com',
                                     UsersFieldMap.FULL_NAME: 'Claire Hsieh',
                                     UsersFieldMap.IS_ACTIVE: True,
                                     UsersFieldMap.REPORTING_MANAGER: 'mtk04694',
                                     UsersFieldMap.SITE: None}}
        test_result = self.sync_service.disable_users(
            disable_list, **mytodo_users)
        expected_result = True
        self.assertEqual(test_result, expected_result)

    def test_get_mytodo_users(self):
        v_login_name = 'vend_test'
        v_full_name = "Vendor Hsieh"
        v_email = 'xxxxxx@xxxxx.xxxxx'
        v_is_active = True
        v_dept_name = 'vend_dept'

        m_login_name = 'mtk10809'
        m_full_name = "Claire Hsieh"
        m_email = 'claire.hsieh@mediatek.com'
        m_is_active = True
        m_dept_name = 'WCS/EPM/SST3'
        m_report_mangr = 'mtk04694'
        m_dept_id = 50199460

        Users.objects.create(login_name=m_login_name, full_name=m_full_name,
                             e_mail=m_email, is_active=m_is_active, dept_name=m_dept_name,
                             reporting_manager=m_report_mangr, dept_id=m_dept_id)
        Users.objects.create(login_name=v_login_name, full_name=v_full_name,
                             e_mail=v_email, is_active=v_is_active, dept_name=v_dept_name)

        # get mtk%
        expected_result = {m_login_name: {UsersFieldMap.DEPT_ID: m_dept_id,
                                          UsersFieldMap.DEPT_NAME: m_dept_name,
                                          UsersFieldMap.E_MAIL: m_email,
                                          UsersFieldMap.FULL_NAME: m_full_name,
                                          UsersFieldMap.IS_ACTIVE: True,
                                          UsersFieldMap.REPORTING_MANAGER: m_report_mangr,
                                          UsersFieldMap.SITE: None}}
        test_result = self.sync_service.get_mytodo_users(Const.MTK_PREFIX)
        self.assertDictEqual(test_result, expected_result)

        # get <>mtk%
        expected_result = {v_login_name: {UsersFieldMap.DEPT_ID: None,
                                          UsersFieldMap.DEPT_NAME: v_dept_name,
                                          UsersFieldMap.E_MAIL: v_email,
                                          UsersFieldMap.FULL_NAME: v_full_name,
                                          UsersFieldMap.IS_ACTIVE: True,
                                          UsersFieldMap.REPORTING_MANAGER: None,
                                          UsersFieldMap.SITE: None}}
        test_result = self.sync_service.get_mytodo_users(Const.NOT_MTK)
        self.assertDictEqual(test_result, expected_result)

    def test_insert_users(self):
        all_users = [{UsersFieldMap.LOGIN_NAME: 'vend_claire',
                      UsersFieldMap.DEPT_ID: 50199460,
                      UsersFieldMap.DEPT_NAME: 'vend_dept',
                      UsersFieldMap.E_MAIL: 'xxxxxx@xxxxx.xxxxx',
                      UsersFieldMap.FULL_NAME: 'Vendor Hsieh',
                      UsersFieldMap.IS_ACTIVE: True,
                      UsersFieldMap.REPORTING_MANAGER: None,
                      UsersFieldMap.SITE: None},
                     {UsersFieldMap.LOGIN_NAME: 'mtk10809',
                      UsersFieldMap.DEPT_ID: None,
                      UsersFieldMap.DEPT_NAME: 'WCS/EPM/SST3',
                      UsersFieldMap.E_MAIL: 'claire.hsieh@mediatek.com',
                      UsersFieldMap.FULL_NAME: 'Claire Hsieh',
                      UsersFieldMap.IS_ACTIVE: True,
                      UsersFieldMap.REPORTING_MANAGER: 'mtk04694',
                      UsersFieldMap.SITE: None}
                     ]
        try:
            self.sync_service.insert_users(all_users)
            assert True
        except Exception:
            assert False

    def test_update_users(self):
        m_login_name = 'mtk10809'
        m_full_name = "Claire Hsieh"
        m_email = 'claire.hsieh@mediatek.com'
        m_is_active = True
        m_dept_name = 'WCS/EPM/SST3'
        m_report_mangr = 'mtk04694'
        m_dept_id = '50199460'

        Users.objects.create(login_name=m_login_name, full_name=m_full_name,
                             e_mail=m_email, is_active=m_is_active, dept_name=m_dept_name,
                             reporting_manager=m_report_mangr, dept_id=m_dept_id)

        login_name = 'mtk10809'
        update_info = {UsersFieldMap.IS_ACTIVE: False}
        try:
            self.sync_service.update_users(login_name, **update_info)
            assert True
        except Exception:
            assert False

    def test_success_create_depts(self):
        new_depts = ['50159310', '50159711']
        odr_depts = {'50159310': {DeptsFieldMap.DEPT_ID: '50159310', DeptsFieldMap.DEPT_MANGR: 'mtk30015', DeptsFieldMap.DEPT_NAME: 'EO/CEG', DeptsFieldMap.PARENT_DEPT: '50064810', DeptsFieldMap.SITE: 'MUS'},
                     '50159711': {DeptsFieldMap.DEPT_ID: '50159711', DeptsFieldMap.DEPT_MANGR: 'mtk10824', DeptsFieldMap.DEPT_NAME: 'EO/TBGMO', DeptsFieldMap.PARENT_DEPT: '50159710', DeptsFieldMap.SITE: 'MTB'}}
        try:
            self.sync_service.create_depts(new_depts, **odr_depts)
            assert True
        except Exception:
            assert False

    def test_fail_create_depts(self):
        new_depts = ['50159310', '50159711']
        odr_depts = {'50159310': {'DeptsFieldMap.DEPT_ID': '50159310', DeptsFieldMap.DEPT_MANGR: 'mtk30015', DeptsFieldMap.DEPT_NAME: 'EO/CEG', DeptsFieldMap.PARENT_DEPT: '50064810', DeptsFieldMap.SITE: 'MUS'},
                     '50159711': {DeptsFieldMap.DEPT_ID: '50159711', DeptsFieldMap.DEPT_MANGR: 'mtk10824', DeptsFieldMap.DEPT_NAME: 'EO/TBGMO', DeptsFieldMap.PARENT_DEPT: '50159710', DeptsFieldMap.SITE: 'MTB'}}
        expected_result = False
        test_result = self.sync_service.create_depts(new_depts, **odr_depts)
        self.assertEqual(test_result, expected_result)

    def test_disable_depts(self):
        dept_id = '50159310'
        dept_mangr = 'mtk30015'
        dept_name = 'EO/CEG'
        parent_dept = '50064810'
        site = 'MUS'
        disable_list = [dept_id]
        Depts.objects.create(dept_id=dept_id, dept_mangr=dept_mangr,
                             dept_name=dept_name, parent_dept=parent_dept, site=site, is_active=True)

        mytodo_depts = {dept_id: {DeptsFieldMap.DEPT_MANGR: dept_mangr, DeptsFieldMap.DEPT_NAME: dept_name,
                                  DeptsFieldMap.PARENT_DEPT: parent_dept, DeptsFieldMap.SITE: site, DeptsFieldMap.IS_ACTIVE: True}
                        }

        try:
            self.sync_service.disable_depts(
                disable_list, **mytodo_depts)
            assert True
        except Exception:
            assert False

    def test_update_depts(self):
        dept_id = '50159310'
        dept_mangr = 'mtk30015'
        dept_name = 'EO/CEG'
        parent_dept = '50064810'
        site = 'MUS'
        Depts.objects.create(dept_id=dept_id, dept_mangr=dept_mangr,
                             dept_name=dept_name, parent_dept=parent_dept, site=site, is_active=True)

        update_info = {DeptsFieldMap.DEPT_MANGR: 'mtk10809'}
        try:
            self.sync_service.update_depts(dept_id, **update_info)
            assert True
        except Exception:
            assert False

    def test_insert_depts(self):
        all_depts = [{DeptsFieldMap.DEPT_ID: '50159310', DeptsFieldMap.DEPT_MANGR: 'mtk30015', DeptsFieldMap.DEPT_NAME: 'EO/CEG', DeptsFieldMap.PARENT_DEPT: '50064810', DeptsFieldMap.SITE: 'MUS'},
                     {DeptsFieldMap.DEPT_ID: '50159711', DeptsFieldMap.DEPT_MANGR: 'mtk10824', DeptsFieldMap.DEPT_NAME: 'EO/TBGMO', DeptsFieldMap.PARENT_DEPT: '50159710', DeptsFieldMap.SITE: 'MTB'}]
        try:
            self.sync_service.insert_depts(all_depts)
            assert True
        except Exception:
            assert False
