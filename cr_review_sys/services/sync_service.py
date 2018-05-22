'''
Created on Nov 23, 2017

@author: MTK06979
'''

from datetime import timedelta
import datetime
import json
import logging
import threading

import cx_Oracle
from django.conf import settings
from django.db import transaction
from django.db.models.query_utils import Q
from django.utils import timezone

from cr_review_sys.const import CrFieldMap, Const, CrMeta, WitsClan,\
    SyncControlTag, WitsDb, UsersFieldMap, DeptsFieldMap
from cr_review_sys.errors import QueryDefineNotFound, CrReviewErrorCode, CrNewListNotFound,\
    CrUpdateListNotFound, HwPrjUpdateInfoNotFound, HwPrjCreateInfoNotFound,\
    CrReviewError, SyncFunctionNotFound, DataSourceIncomplete
from cr_review_sys.models import Activity, ActivityCr, SyncJob, Cr, SyncControl,\
    CrmHwProject, CrmHwProjectMilestone, ActivityUpdateStatus, Users, Depts,\
    ActivityCategory
from md_analysis.const import MdHwPrjType, MdMeta, BULK_BATCH_SIZE
from md_analysis.errors import HwTypeNotFound, MdError
from md_analysis.services.gen_md_report_service import GenMdReportService
from my_to_do.util import Singleton
from my_to_do.util.date_helper import DateHelper
from my_to_do.util.db_table_helper import DbTableHelper
from my_to_do.util.sql_helper import SQLHelper
from my_to_do.util.sync_helper import SyncHelper
from my_to_do.util.wits_helper import Wits


class SyncService(object):
    '''
    DB and wits http data integration
    '''

    __metaclass__ = Singleton

    def __init__(self):
        '''
        Constructor
        '''
        self.wits_objs = {}
        self.logger = logging.getLogger('aplogger')
        self.sync_helper = SyncHelper()
        self.gen_report_service = None
        self.crm_sql_helper = None

    def getWitsId(self, clan, db):
        return "{}_{}".format(clan, db)

    def getWitsObject(self, clan, db):
        wits_id = self.getWitsId(clan, db)

        wits_obj = self.wits_objs.get(wits_id, None)
        if not wits_obj:
            wits_obj = Wits(clan, db)
            self.wits_objs[wits_id] = wits_obj
        else:
            check_result = wits_obj.checkSession()

            if not check_result:
                wits_obj = Wits(clan, db)
                self.wits_objs[wits_id] = wits_obj

        return wits_obj

    def getSyncControlId(self, clan, db, sync_type):
        '''
        helper to format id for sync_control table
        '''
        return "{}_{}_{}".format(clan, db, sync_type)

    def __create_sync_error_string(self, msg):
        return "latest failure happened at [{}]: {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg)

    def safe_sync_data(self, act_update_status_id, **kwds):
        """
        we don't really block the inter-master update, need to use file lock instead,
        and need to update the docker share mount path
        """
        isLocked = False
        lock = None
        sync_error_code = None
        sync_error_msg = ""

        try:
            self.logger.info("waiting for read lock...")
            lock = threading.Lock()
            lock.acquire()
            isLocked = True
            curStatus = ActivityUpdateStatus.objects.get(
                id=act_update_status_id)
            if curStatus.status == Const.ONGOING:
                self.logger.info("the sync is on the way.")
                return

            ActivityUpdateStatus.objects.filter(
                id=act_update_status_id).update(status=Const.ONGOING)

            lock.release()
            isLocked = False

            self.logger.info("running update...")
            try:
                sync_error_code = None
                sync_error_msg = ""
                ActivityUpdateStatus.objects.filter(id=act_update_status_id).update(
                    error_code=sync_error_code, error_msg=sync_error_msg)

                if act_update_status_id == Const.MD_ANALYS_ACT_STATUS_ID:
                    clan = kwds[Const.CLAN]
                    db = kwds[Const.DB]
                    self.__sync_partial(clan, db)
                elif act_update_status_id == Const.CR_REVIEW_ACT_WL_STATUS_ID:
                    self.__sync_activity_cr_while_list()
                elif act_update_status_id == Const.USERS_DEPTS_ID:
                    self.__sync_users_depts()
                else:
                    self.logger.error(
                        "[%s] no mapping for sync function", act_update_status_id)
                    raise SyncFunctionNotFound()
            finally:
                # even if the exception happened, the sync is called finish
                # (with failure)
                ActivityUpdateStatus.objects.filter(
                    id=act_update_status_id).update(status=Const.FINISH)

        except (MdError, CrReviewError) as e:
            self.logger.exception(e.msg)
            sync_error_code = e.code
            sync_error_msg = self.__create_sync_error_string(e.msg)

        except Exception as e:
            msg = "unknown exception: {}".format(e)
            self.logger.exception(msg)
            sync_error_code = CrReviewErrorCode.UnknownError
            sync_error_msg = self.__create_sync_error_string(msg)

        finally:
            # update the error status
            ActivityUpdateStatus.objects.filter(
                id=act_update_status_id).update(error_code=sync_error_code, error_msg=sync_error_msg)

            try:
                if lock and isLocked:
                    lock.release()
            except:
                self.logger.exception("fail to release lock")

    def __sync_partial(self, clan, db):
        self.logger.info("start sync partial")
        '''
        This is only partial sync for UI update button
        Scope: by each WITS db, address clan & db when using this function

        Steps:
        1. Get last sync activity CR list
        2. Get partial add list from WITS
        3. Sync new and update CR infor. from WITS
        4. Sync distinct HW project/milestone infor. from CRM
        5. Create new added crs for activity_cr with old sync job id (will update if gen report success)
        6. Gen report table
        7. Update new sync job id
        '''
        last_sync_info = {}
        new_sync_job_id = None

        try:
            self.logger.info("[Sync Partial] starting sync...")
            # 1. Get last sync activity CR list
            last_sync_info = self.sync_helper.get_lastest_sync_job_id(
                MdMeta.ActivityId)
            self.logger.info(
                "[step 1.] get last_sync_info: %s", last_sync_info)

            # 2. Get partial add list from WITS
            self.logger.info("[step 2.] get partial add list from WITS")
            wits = self.getWitsObject(clan, db)

            wits_cr_dict = wits.get_md_whilelist_change()

            # 3. Sync new and update CR infor. from WITS
            self.logger.info(
                "[step 3.] sync new and update CR infor. from WITS")
            new_cr_from_wits = []  # store cr list not in Activity_CR now
            new_cr_from_wits = self.sync_cr(
                clan, db, last_sync_info[Const.SYNC_JOB_ID], **wits_cr_dict)

            # 4. Sync distinct HW project/milestone infor. from CRM
            self.logger.info("[step 4.] sync hw project and mile stone")
            self.sync_hw_entry(clan, db)

            # 5. Create new added crs for activity_cr with old sync job id
            # (will update if gen report success)
            self.logger.info(
                "[step 5.] create new added crs for activity_cr with old sync job id")
            success_sync_job_id = self.insert_act_cr(
                MdMeta.ActivityId, last_sync_info[Const.SYNC_JOB_ID], new_cr_from_wits, db)

            if success_sync_job_id == last_sync_info[Const.SYNC_JOB_ID]:
                self.logger.info("success for new added activity cr list")
            else:
                self.logger.error(
                    "success for new added activity cr list, use ori activity cr list to gen report")

            # 6. Gen report table
            new_sync_job_id = DateHelper.get_new_sync_job_id(db)
            self.logger.info("[step 6.] gen report table start...")
            self.logger.info("[new_sync_job_id] %s", new_sync_job_id)
            self.gen_report_service = GenMdReportService()
            self.gen_report_service.gen_report_entry(
                new_sync_job_id, Const.PARTIALSYNC, last_sync_info[Const.SYNC_JOB_ID])

            # 7. Update new sync job id
            self.logger.info("[step 7.] update new sync job id...")
            result = self.update_sync_record_for_sync_partial(
                MdMeta.ActivityId, last_sync_info[Const.SYNC_JOB_ID], new_sync_job_id)
            self.logger.info("[Sync Partial] final result is %s", result)
        except Exception as e:
            self.logger.exception("[Sync Partial][Exception]: %s", e)

    def sync_hw_entry(self, clan, db):
        try:
            self.crm_sql_helper = SQLHelper(settings.CRM_CONNECTION_STRING)
            self.crm_sql_helper.connect()
            self.logger.info("start to sync_hw_prj")
            self.sync_hw_prj(clan, db)
            self.sync_hw_prj_milestone(clan, db)
            self.logger.info("end to sync_hw_prj")
        except Exception as e:
            self.logger.exception(
                "sync [5. Sync distinct HW project/milestone infor. from CRM] exception: %s", e)
        finally:
            del self.crm_sql_helper

    def schedule_sync_data(self, act_update_status_id, sync_interval, **kwds):
        self.safe_sync_data(act_update_status_id, **kwds)

        timer = threading.Timer(int(sync_interval) * 60, self.schedule_sync_data,
                                args=(act_update_status_id, sync_interval), kwargs=kwds)
        timer.setDaemon(True)
        timer.start()

    def sync_act_cr(self, clan, db):

        success_sync_job_id_list = []

        try:
            wits = self.getWitsObject(clan, db)

            activities = Activity.objects.filter(
                db_scope=wits.db, active=1)  # get all activity by cqdb

            try:
                for activity in activities:  # forloop all activity to sync
                    new_sync_job_id = DateHelper.get_new_sync_job_id(wits.db)

                    act_id = activity.activity_id
                    query_def = activity.query_def

                    if query_def == "":
                        self.logger.exception(
                            "null query_def, couldn't run sync for:" + str(act_id))
                        raise QueryDefineNotFound()
                    else:
                        all_act_cr = wits.get_activity_cr_by_act_def(query_def)
                        success_sync_job_id = self.insert_act_cr(
                            act_id, new_sync_job_id, all_act_cr, db)
                        success_sync_job_id_list.append(success_sync_job_id)
            except QueryDefineNotFound as e:
                self.logger.error(
                    "catch QueryDefineNotFound exception: [%s] %s", e.code, e.msg)
            except Exception as e:
                self.logger.error(
                    "catch exception in activity cr insert: [%s] %s", CrReviewErrorCode.UnknownError, format(e))
        except Exception as e:
            self.logger.error(
                "catch exception in sync_act_cr: [%s] %s", CrReviewErrorCode.UnknownError, format(e))
        return success_sync_job_id_list

    @transaction.atomic
    def insert_act_cr(self, act_id, new_sync_job_id, all_act_cr, witsdb):

        self.logger.info(
            "start sync [Activity_CR] act_id: %s, sync_job_id: %s, witsdb: %s", act_id, new_sync_job_id, witsdb)

        cr_insert_list = list()
        self.logger.info("start forloop all_act_cr")
        for cr_id in all_act_cr:  # for loop each CR list by activity
            tmp_id = DbTableHelper.get_act_cr_id(act_id, cr_id)

            cr_insert_list.append(
                ActivityCr(id=tmp_id, activity_id=act_id, cr_id=cr_id, sync_job_id=new_sync_job_id, cr_db=witsdb, active=Const.IS_ACTIVE))
        self.logger.info("end forloop all_act_cr")

        # note: check for real data to decide whether to adopt page
        # insert, ex. 1000/per commit
        self.logger.info("start bulk create all_act_cr")
        ActivityCr.objects.bulk_create(
            cr_insert_list, batch_size=BULK_BATCH_SIZE)
        self.logger.info("end bulk create all_act_cr")

        self.logger.info(
            "commit db ok for [Activity_CR] act_id: %s, sync_job_id: %s", act_id, new_sync_job_id)
        return new_sync_job_id

    def get_distinct_cr(self, sync_job_id_list):

        self.logger.info(
            "get_distinct_cr for sync_job_id_list: %s", sync_job_id_list)

        queryset = ActivityCr.objects.filter(
            sync_job_id__in=sync_job_id_list).values_list('cr_id', flat=True).distinct()

        self.logger.debug("queryset: %s", queryset)

        cr_list = list(queryset)
        self.logger.info(
            "distinct cr qty: %s", len(cr_list))
        return cr_list

    def sync_md_info(self, clan, db):
        wits_session = self.getWitsObject(clan, db)
        sync_id = self.getSyncControlId(clan, db, SyncControlTag.MD_INFO)
        last_sync_time = self.get_last_sync_time(sync_id)
        self.logger.info("last sync time: %s", last_sync_time)

        updated_md_info = wits_session.get_updated_md_info(last_sync_time)
        final_result = True
        for eachrow in updated_md_info:
            eachrow[Const.DATA] = self.sync_helper.get_full_cr_info_with_plmn(
                **eachrow[Const.DATA])
            updated_result = self.update_cr(eachrow)

            if not updated_result:
                final_result = False

        return final_result

    def sync_cr(self, clan, db, last_sync_job_id, **wits_cr_dict):
        '''
        1. Check wits_cr_dict, separate with 2 groups: a. new_cr_whitelist, b. new_cr_list
        2. Create new_cr_list first
        3. Update and disable Activity_CR white list
        4. For existing CR, check changelog after last sync time; then update in mytodo
        5. Updated MD_Info sync
        '''
        new_cr_whitelist = []
        new_cr_list = []
        enable_cr_list = []
        disable_cr_list = []
        # sync function do not use cache but query db directly, only UI
        # query leverage cache
        last_act_cr_list = self.sync_helper.get_latest_act_cr_list(
            MdMeta.ActivityId, last_sync_job_id)
        mytodo_crs = self.get_mytodo_crs()
        wits = self.getWitsObject(clan, db)

        for cr in wits_cr_dict[Const.NEW_CR]:
            if cr in last_act_cr_list:
                enable_cr_list.append(cr)
                # sync CR again to avoid info gap when disable
                tmp_cr_info = wits.get_cr_info(cr)
                tmp_cr_info = self.sync_helper.get_full_cr_info_with_plmn(
                    **tmp_cr_info)
                del tmp_cr_info[CrFieldMap.Wits.id]
                cr_info = {Const.CR_ID: cr, Const.DATA: tmp_cr_info}
                self.update_cr(cr_info)

            else:
                new_cr_whitelist.append(cr)  # not in whielist, and check CR
                if cr in mytodo_crs:
                    pass  # already exist, just add into whitelist
                else:
                    new_cr_list.append(cr)  # whole new cr

        for cr in wits_cr_dict[Const.DISABLE_CR]:
            if cr in last_act_cr_list:
                disable_cr_list.append(cr)
            else:
                self.logger.info("%s didn't exist in whitelist, skip", cr)

        try:
            self.create_cr(clan, db, new_cr_list)
        except CrNewListNotFound as e:
            self.logger.error("[%s] %s", e.code, e.msg)
        except Exception as e:
            self.logger.exception("create CR exception: %s", e)

        self.handle_update_act_cr(
            MdMeta.ActivityId, disable_cr_list, enable_cr_list)

        try:
            self.update_md_cr_by_changelog(clan, db)
        except CrUpdateListNotFound as e:
            self.logger.error("[%s] %s", e.code, e.msg)
        except Exception as e:
            self.logger.exception("updae CR exception: %s", e)

        md_info_sync_result = True
        new_sync_time = datetime.datetime.now().replace(microsecond=0)
        try:
            self.logger.info("sync CR MD_Info update from WITS")
            md_info_sync_result = self.sync_md_info(clan, db)
            self.logger.info("sync CR MD_Info result %s", md_info_sync_result)
        except Exception as e:
            self.logger.exception("updae MD_Info exception: %s", e)
        finally:
            self.logger.info("update last_update_time")

            if md_info_sync_result is True:
                sync_id = self.getSyncControlId(
                    clan, db, SyncControlTag.MD_INFO)
                self.update_last_sync_time(sync_id, new_sync_time)
            else:
                self.logger.warning(
                    "keep last_sync_time because part of update fail")
            self.logger.info("end to sync CR MD_Info update from WITS")

        return new_cr_whitelist

    def get_mytodo_crs(self):
        mytodo_cr_list = []

        queryset = Cr.objects.all()

        for eachrow in queryset:
            mytodo_cr_list.append(eachrow.cr_id)
        return mytodo_cr_list

    def create_cr(self, clan, db, cr_list):

        if cr_list == []:
            raise CrNewListNotFound()

        result = False
        hw_prj_list = []
        cr_detail_list = []
        wits = self.getWitsObject(clan, db)

        self.logger.info("start to get cr detail from WITS")
        for eachcr in cr_list:
            cr_info = wits.get_cr_info(eachcr)
            hw_prj_list = self.check_hw_project_exist(
                cr_info.get(CrFieldMap.Wits.HW_Project_HW_Project_ID, ""), hw_prj_list)

            # md cr needs extra certian fields:
            # country/operator
            # remove bu_type becuase MD CR could be checked by activity_cr
            # while list
            cr_info = self.sync_helper.get_full_cr_info_with_plmn(**cr_info)

            cr_detail_list.append(cr_info)
        self.logger.info("end to get cr detail from WITS")

        self.logger.info("start to insert cr")
        try:
            result = self.insert_cr(cr_detail_list)
        except Exception as e:
            self.logger.exception("insert cr exception: %s", e)

        if result is True:
            self.logger.info("insert cr ok")
        else:
            self.logger.info("insert cr fail & rollback")
        self.logger.info("end to insert cr")

        return hw_prj_list

    @transaction.atomic
    def insert_cr(self, all_cr):

        self.logger.info("start insert_cr")
        self.logger.info("all_cr list: %s", all_cr)

        cr_insert_list = list()
        self.logger.info("start forloop all_cr")
        for eachcr in all_cr:
            cr_insert_list.append(Cr(**eachcr))
        self.logger.info("end forloop all_cr")

        # note: check for real data to decide whether to adopt page
        # insert, ex. 1000/per commit
        self.logger.info("start bulk create all_cr")
        Cr.objects.bulk_create(cr_insert_list, batch_size=BULK_BATCH_SIZE)
        self.logger.info("end bulk create all_cr, commit db ok")
        return True

    @transaction.atomic
    def insert_one_cr(self, cr):
        Cr.objects.create(**cr)
        return True

    def update_cr(self, cr_info):

        try:
            self.logger.info("start update_cr")
            self.logger.info(u"cr_info changelog: %s", cr_info)

            cr_id = cr_info.get(CrFieldMap.Wits.id)
            update_data = cr_info.get(Const.DATA)

            # Add extra rule because of Oracle v10 bug-10102731,
            # Solution: need to update lob column use different bind. In here, separated update by ORM
            # Notice: need to add if new lob column created
            if update_data.get("solution", None) and update_data.get("inner_solution", None):
                tmp_update_data = {"solution": update_data["solution"]}
                Cr.objects.filter(cr_id=cr_id).update(**tmp_update_data)
                self.logger.info(
                    "successfully update solution first for %s", cr_id)
                del update_data["solution"]

            update_data.update(updated_time=timezone.now())
            Cr.objects.filter(cr_id=cr_id).update(**update_data)
            return True
        except Exception as e:
            self.logger.exception(
                "update cr fail, cr_info: %s, error: %s", cr_info, e)
            return False

    def check_hw_project_exist(self, hw_prj_id, hw_prj_list):
        if hw_prj_id not in hw_prj_list:
            hw_prj_list.append(hw_prj_id)
            self.logger.info("hw prj id [%s] non-exists, create", hw_prj_id)
        else:
            self.logger.info("hw prj id [%s] exists", hw_prj_id)
        return hw_prj_list

    def get_last_sync_time(self, sync_id):
        last_sync_time = ""
        try:
            queryset = SyncControl.objects.filter(
                id=sync_id)

            for eachrow in queryset:
                last_sync_time = eachrow.sync_value

            if last_sync_time == "":
                now = datetime.datetime.now()
                aDay = timedelta(days=-1)
                now_to_last_day = now + aDay
                last_sync_time = now_to_last_day.strftime("%Y-%m-%d %H:%M:%S")
                self.logger.info("last sync time [%s]", last_sync_time)
        except Exception as e:
            self.logger.exception("%s", e)
        return last_sync_time

    def get_distinct_hw_prj_id_by_cr(self, cr_list):

        queryset = Cr.objects.filter(
            cr_id__in=cr_list).values_list('hw_project_id', flat=True).distinct()

        hw_prj_list = list(queryset)
        return hw_prj_list

    def update_last_sync_time(self, sync_id, new_sync_time):
        try:
            SyncControl.objects.filter(id=sync_id).update(
                sync_value=new_sync_time, sync_lastdate=timezone.now())
        except Exception as e:
            self.logger.exception("update_last_sync_time exception: %s", e)

    def update_cr_by_changelog(self, clan, db, cr_list):

        if cr_list == []:
            raise CrUpdateListNotFound()

        result = False
        sync_result = True
        hw_prj_list = []
        wits = self.getWitsObject(clan, db)
        sync_id = self.getSyncControlId(clan, db, SyncControlTag.CR_INFO)
        last_sync_time = self.get_last_sync_time(sync_id)

        # new_sync_time is a string, and store last sync changelog time from WITS(CQ)
        # special use for datetime.datetime.now() instead of timezone.now() to
        # log GMT+8 time
        new_sync_time = datetime.datetime.now().replace(microsecond=0)

        try:
            self.logger.info(
                "start to update_cr_by_changelog from WITS, qty: %s", len(cr_list))
            for eachcr in cr_list:
                cr_info = wits.get_updated_cr_info(last_sync_time, eachcr)
                cr_info[Const.DATA] = self.sync_helper.get_full_cr_info_with_plmn(
                    **cr_info[Const.DATA])

                self.logger.info("start to update cr")
                result = self.update_cr(cr_info)

                if result is True:
                    self.logger.info("update cr ok")
                else:
                    sync_result = False
                    self.logger.info(
                        "update cr fail and don't need to update last sync time")
            self.logger.info("start get hw_prj_id")
            hw_prj_list = self.get_distinct_hw_prj_id_by_cr(cr_list)
            self.logger.info("end get hw_prj_id")
        except Exception as e:
            self.logger.exception("update cr exception: %s", e)
        finally:
            self.logger.info("update last_update_time")

            if sync_result is True:
                sync_id = self.getSyncControlId(
                    clan, db, SyncControlTag.CR_INFO)
                self.update_last_sync_time(sync_id, new_sync_time)
            else:
                self.logger.warning(
                    "keep last_sync_time because part of update fail")
            self.logger.info("end to update_cr_by_changelog from WITS")
        return hw_prj_list

    def update_md_cr_by_changelog(self, clan, db):
        result = False
        sync_result = True
        wits = self.getWitsObject(clan, db)
        sync_id = self.getSyncControlId(clan, db, SyncControlTag.CR_INFO)
        last_sync_time = self.get_last_sync_time(sync_id)

        # new_sync_time is a string, and store last sync changelog time from WITS(CQ)
        # special use for datetime.datetime.now() instead of timezone.now() to
        # log GMT+8 time
        new_sync_time = datetime.datetime.now().replace(microsecond=0)

        try:
            self.logger.info(
                "start to update_md_cr_by_changelog from WITS")
            update_info = wits.get_md_changelog(last_sync_time)
            for eachcr in update_info:
                self.logger.info("start to update cr")
                result = self.update_cr(eachcr)

                if result is True:
                    self.logger.info("update cr ok")
                else:
                    sync_result = False
                    self.logger.info(
                        "update cr fail and don't need to update last sync time")
        except Exception as e:
            self.logger.exception("update cr exception: %s", e)
        finally:
            self.logger.info("update last_update_time")

            if sync_result is True:
                sync_id = self.getSyncControlId(
                    clan, db, SyncControlTag.CR_INFO)
                self.update_last_sync_time(sync_id, new_sync_time)
            else:
                self.logger.warning(
                    "keep last_sync_time because part of update fail")
            self.logger.info("end to update_md_cr_by_changelog from WITS")

    def cal_distinct_hw_prj_list(self, final_hw_list, cal_hw_list):

        for hw_prj in cal_hw_list:
            if hw_prj not in final_hw_list:
                final_hw_list.append(hw_prj)
                self.logger.debug("[%s] add into final_hw_prj_list", hw_prj)
            else:
                self.logger.debug("[%s] exist in final_hw_prj_list", hw_prj)
        return final_hw_list

    def sync_hw_prj(self, clan, db):

        self.logger.info("start to sync_hw_prj from CRM")
        wits = self.getWitsObject(clan, db)
        sync_id = self.getSyncControlId(clan, db, SyncControlTag.HW_PRJ)
        last_sync_time = self.get_last_sync_time(sync_id)
        self.logger.info("last sync time: %s", last_sync_time)

        new_sync_time = datetime.datetime.now().replace(microsecond=0)
        op_update_result = self.sync_hw_prj_by_type(
            wits, last_sync_time, MdHwPrjType.Operator)
        fta_update_result = self.sync_hw_prj_by_type(
            wits, last_sync_time, MdHwPrjType.FTA)

        if op_update_result is True and fta_update_result is True:
            self.update_last_sync_time(sync_id, new_sync_time)
        else:
            self.logger.warning(
                "keep last_sync_time because part of sync_hw_prj fail")
        self.logger.info("end to sync_hw_prj from CRM")

    def get_hw_prj_info_by_last_update_time(self, last_sync_time, hw_type, wits):
        _hw_prj_info = {}

        try:
            '''
            Since operator info is based on hw_project_milestone,
            query milestone first and format into hw project
            '''
            _raw_hw_milestone_info = self.get_crm_hw_prj_milestone(
                hw_type, last_sync_time=last_sync_time)
            _hw_prj_info = self.format_hw_prj_info(
                hw_type, _raw_hw_milestone_info, wits)
        except Exception as e:
            self.logger.exception("Exception: %s", e)
        return _hw_prj_info

    def format_hw_prj_info(self, hw_type, raw_hw_milestone_info, wits):
        '''
        Since one hw prj will have more than one operator,
        format all hw project milestone info into hw project with operator separated.
        Recheck start_date/end_date also
        '''
        _result = []
        for eachrow in raw_hw_milestone_info:
            hw_prj_id = eachrow["PROJECT_ID"]
            operator = eachrow["OPERATOR"] if eachrow["OPERATOR"] else ""
            t_id = DbTableHelper.get_crm_hw_prj_id(
                hw_prj_id, hw_type, operator)
            fta = ""
            start_date = DateHelper.datetime_set_tz(eachrow["START_DATE"])
            end_date = DateHelper.datetime_set_tz(eachrow["END_DATE"])
            is_active = 1 if not eachrow["IS_DELETED"] else 0
            is_completed = eachrow["IS_COMPLETED"]

            # skip disable project's start_date/end_date/is_completed
            # calculation
            if not is_active:
                start_date = None
                end_date = None
                is_completed = 1

            if not any(d.get('id', None) == t_id for d in _result):
                _hw_info_from_wits = wits.get_hw_prj_info(hw_prj_id)
                # new hw prj info
                if hw_type == MdHwPrjType.FTA:
                    fta = eachrow["TYPE"]

                if hw_type == MdHwPrjType.Operator and not operator:
                    self.logger.info(
                        "skip, op project with null operator, %s", t_id)
                    continue

                _tmp = {
                    "id": t_id,
                    "data": {
                        "id": t_id,
                        "hw_project_id": hw_prj_id,
                        "hw_type": hw_type,
                        "operator": operator,
                        "fta": fta,
                        "start_date": start_date,
                        "end_date": end_date,
                        "completed": is_completed,
                        "is_active": is_active
                    }
                }
                _tmp["data"].update(_hw_info_from_wits)
                _result.append(_tmp)
            else:
                ori_data = next(
                    element for element in _result if element['id'] == t_id)
                list_index = _result.index(ori_data)

                is_completed &= ori_data["data"]["completed"]

                if start_date and ori_data["data"]["start_date"]:
                    start_time_diff = start_date - \
                        ori_data["data"]["start_date"]
                    if start_time_diff.days < 0:
                        start_date = ori_data["data"]["start_date"]

                if not start_date:
                    start_date = ori_data["data"]["start_date"]

                if end_date and ori_data["data"]["end_date"]:
                    end_time_diff = end_date - ori_data["data"]["end_date"]
                    if end_time_diff.days > 0:
                        end_date = ori_data["data"]["end_date"]

                if not end_date:
                    end_date = ori_data["data"]["end_date"]

                _data = {
                    "start_date": start_date,
                    "end_date": end_date,
                    "completed": is_completed
                }

                _result[list_index]["data"].update(_data)
        return _result

    def check_hw_prj_exist_in_mytodo(self, t_id):
        queryset = CrmHwProject.objects.filter(id=t_id)
        return any(x for x in queryset)

    def sync_hw_prj_by_type(self, wits, last_sync_time, hw_type):
        total_result = True
        try:
            self.logger.info(
                "start to get hw update info for %s", hw_type)

            hw_update_info = self.get_hw_prj_info_by_last_update_time(
                last_sync_time, hw_type, wits)
            self.logger.info(
                "end to get hw update info for %s", hw_type)

            create_hw_prj_list = []
            for eachrow in hw_update_info:
                t_id = eachrow["id"]
                data = eachrow["data"]

                check_result = self.check_hw_prj_exist_in_mytodo(t_id)

                try:
                    if check_result is True:
                        self.logger.info("[%s] need to update", t_id)
                        # need check is_completed/start_date/end_date
                        data = self.format_specific_hw_prj_info(hw_type, data)
                        update_result = self.update_hw_prj(t_id, **data)
                        self.logger.info("update result: %s", update_result)
                        total_result &= update_result
                    else:
                        self.logger.info("[%s] need to create", t_id)
                        create_hw_prj_list.append(data)
                except HwPrjUpdateInfoNotFound as e:
                    self.logger.warning("Operator [%s] %s", e.code, e.msg)

            if create_hw_prj_list:
                create_result = self.create_hw_prj(create_hw_prj_list)
                self.logger.info("create result: %s", create_result)
                total_result &= create_result
        except HwTypeNotFound as e:
            self.logger.error("[%s] please address hw type: %s", e.code, e.msg)
            total_result &= False
        except HwPrjCreateInfoNotFound as e:
            total_result &= False
            self.logger.error("[%s] no create data: %s", e.code, e.msg)
        except Exception as e:
            self.logger.exception("Exception in creating hw prj: %s", e)
            total_result &= False
        return total_result

    def update_hw_prj(self, t_id, **data):
        update_result = False
        if data == {}:
            raise HwPrjUpdateInfoNotFound

        try:
            CrmHwProject.objects.filter(id=t_id).update(**data)
            update_result = True
            self.logger.info("update hw prj [%s] ok", t_id)
        except Exception as e:
            self.logger.exception("update hw prj [%s] exception: %s", t_id, e)
        return update_result

    @transaction.atomic
    def create_hw_prj(self, create_list):

        if create_list == []:
            raise HwPrjCreateInfoNotFound()

        self.logger.info("create hw prj")
        create_hw_prj_list = list()
        for eachrow in create_list:
            create_hw_prj_list.append(CrmHwProject(**eachrow))

        # note: check for real data to decide whether to adopt page
        # insert, ex. 1000/per commit
        self.logger.info("start bulk create hw_prj_list")
        CrmHwProject.objects.bulk_create(
            create_hw_prj_list, batch_size=BULK_BATCH_SIZE)
        self.logger.info("end bulk create hw_prj_list")
        return True

    def get_create_info_for_hw_prj(self, hw_type, ori_data, hw_info_from_wits):

        hw_prj_id = ori_data["PROJECT_ID"]
        fta = ori_data["TYPE"]
        start_date = ori_data["START_DATE"]
        end_date = ori_data["END_DATE"]
        is_completed = ori_data["IS_COMPLETED"]
        operator = "" if not ori_data["OPERATOR"] else ori_data["OPERATOR"]

        create_info = {
            "id": DbTableHelper.get_crm_hw_prj_id(hw_prj_id, hw_type, operator),
            "hw_project_id": hw_prj_id,
            "hw_type": hw_type,
            "completed": is_completed,
            "is_active": 1
        }

        if start_date is not None:
            tmp_str = start_date.strftime("%Y-%m-%d")
            self.logger.debug("start_date: %s", tmp_str)
            create_info.update({"start_date": tmp_str})

        if end_date is not None:
            tmp_str = end_date.strftime("%Y-%m-%d")
            self.logger.debug("end_date: %s", tmp_str)
            create_info.update({"end_date": tmp_str})

        if hw_type == MdHwPrjType.Operator and operator is not None:
            create_info.update({"operator": operator})

        if hw_type == MdHwPrjType.FTA and fta is not None:
            create_info.update({"fta": fta})
        create_info.update(hw_info_from_wits)
        self.logger.info("create_info: %s", create_info)
        return create_info

    def sync_hw_prj_milestone(self, clan, db):

        self.logger.info("start to sync_hw_prj_milestone from CRM")
        sync_id = self.getSyncControlId(clan, db, SyncControlTag.HW_MILESTONE)
        last_sync_time = self.get_last_sync_time(sync_id)
        self.logger.info("last sync time: %s", last_sync_time)
        new_sync_time = datetime.datetime.now().replace(microsecond=0)

        op_sync_result = self.sync_hw_prj_milestone_by_type(
            last_sync_time, MdHwPrjType.Operator)
        fta_sync_result = self.sync_hw_prj_milestone_by_type(
            last_sync_time, MdHwPrjType.FTA)

        if op_sync_result is True and fta_sync_result is True:
            self.update_last_sync_time(sync_id, new_sync_time)
        else:
            self.logger.warning(
                "keep last_sync_time because part of sync_hw_prj fail")

        self.logger.info("end to sync_hw_prj_milestone from CRM")

    def sync_hw_prj_milestone_by_type(self, last_sync_time, hw_type):
        total_result = True
        try:
            self.logger.info(
                "[%s milestone sync] start, time: %s", hw_type, last_sync_time)
            raw_hw_milestone_info = self.get_crm_hw_prj_milestone(
                hw_type, last_sync_time=last_sync_time)

            hw_milestone_info = self.format_hw_prj_milestone(
                hw_type, raw_hw_milestone_info)

            create_hw_prj_milestone_list = []
            tmp_valid_milestone_id_list = []
            for eachrow in hw_milestone_info:
                t_id = eachrow["id"]
                data = eachrow["data"]
                check_result = self.check_hw_milestone_exist_in_mytodo(t_id)

                try:
                    if check_result is True:
                        update_result = self.update_hw_prj_milestone(
                            t_id, **data)
                        total_result &= update_result
                    else:
                        check_id_unique = self.check_id_unique_for_hw_prj_milestone(
                            tmp_valid_milestone_id_list, t_id)

                        if check_id_unique:
                            tmp_valid_milestone_id_list.append(t_id)
                        else:
                            self.logger.info(
                                "duplicated [%s], skip create", t_id)
                            continue

                        create_hw_prj_milestone_list.append(data)
                except (HwPrjUpdateInfoNotFound, HwPrjCreateInfoNotFound) as e:
                    total_result &= False
                    self.logger.warning(
                        "milestone sync no data: [%s] %s", e.code, e.msg)

            if not (create_hw_prj_milestone_list == []):
                create_result = self.create_hw_prj_milestone(
                    create_hw_prj_milestone_list)
                self.logger.info("create result: %s", create_result)
                total_result &= create_result
        except Exception as e:
            total_result &= False
            self.logger.error(
                "exception in sync_hw_prj_milestone_by_type: %s", e)
        self.logger.info("[%s milestone sync] end", hw_type)
        return total_result

    def format_hw_prj_milestone(self, hw_type, raw_hw_milestone_info):
        _result = []
        for eachrow in raw_hw_milestone_info:
            # get key first
            hw_prj_id = eachrow["PROJECT_ID"]
            hw_type = eachrow["TYPE"]
            milestone_id = eachrow["MILESTONE_ID"]
            operator = eachrow["OPERATOR"] if eachrow["OPERATOR"] else ""
            t_id = DbTableHelper.get_crm_hw_prj_milestone_id(
                hw_prj_id, hw_type, milestone_id, operator)

            if hw_type == MdHwPrjType.Operator and not operator:
                self.logger.info(
                    "operator project with null operator, skip, %s/%s/%s", hw_prj_id, milestone_id, hw_type)
                continue

            # other column and check
            milestone_name = eachrow["MILESTONE_NAME"]
            start_date = DateHelper.datetime_set_tz(eachrow["START_DATE"])
            end_date = DateHelper.datetime_set_tz(eachrow["END_DATE"])
            with_vote = eachrow["WITH_VOLTE"]
            with_wfc = eachrow["WITH_WFC"]
            with_vilte = eachrow["WITH_VILTE"]
            is_completed = eachrow["IS_COMPLETED"]
            is_active = 1 if not eachrow["IS_DELETED"] else 0

            _tmp = {
                "id": t_id,
                "data": {
                    "id": t_id,
                    "hw_project_id": hw_prj_id,
                    "type": hw_type,
                    "milestone_name": milestone_name,
                    "start_date": start_date,
                    "end_date": end_date,
                    "with_vote": with_vote,
                    "with_wfc": with_wfc,
                    "with_vilte": with_vilte,
                    "completed": is_completed,
                    "operator": operator,
                    "milestone_id": milestone_id,
                    "is_active": is_active
                }
            }
            _result.append(_tmp)
        return _result

    def check_id_unique_for_hw_prj_milestone(self, tmp_valid_milestone_id_list, tmp_id):
        if tmp_id in tmp_valid_milestone_id_list:
            return False
        else:
            return True

    def get_crm_hw_prj_milestone(self, hw_type, last_sync_time=None, exclude_delete=False, hw_id=None, operator=None):
        update_info = []

        try:
            sql_condition = []
            bindvars = {}
            table = "eservice.cq_crm_milestone_v"
            column = ['project_id', 'type', 'milestone_id', 'milestone_name',
                      'start_date', 'end_date', 'with_volte', 'with_wfc',
                      'with_vilte', 'is_completed', 'operator', 'is_deleted']

            if hw_type == MdHwPrjType.Operator:
                sql_condition.append("category = :category")
                bindvars.update(
                    {"category": MdHwPrjType.OperatorCategory.OPTR})
            elif hw_type == MdHwPrjType.FTA:
                sql_condition.append("type IN (:h1, :h2)")
                bindvars.update(
                    {"h1": MdHwPrjType.FTAType.GCF, "h2": MdHwPrjType.FTAType.PTCRB})
            else:
                raise HwTypeNotFound()

            if exclude_delete:
                sql_condition.append("is_deleted = 0")

            if last_sync_time:
                sql_condition.append(
                    "last_updated_date > TO_DATE(:last_updated_time, 'yyyy-mm-dd hh24:mi:ss')")
                bindvars.update({"last_updated_time": last_sync_time})

            if hw_id:
                sql_condition.append("project_id = '{}'".format(hw_id))

            if operator:
                sql_condition.append("operator = '{}'".format(operator))

            sql = "SELECT {} FROM {} WHERE {}".format(
                ", ".join(column), table, " AND ".join(sql_condition))
            self.crm_sql_helper.execute(sql, bindvars)
            update_info = self.crm_sql_helper.getResult()
        except cx_Oracle.DatabaseError as e:
            self.logger.exception(
                "db exception in get_crm_hw_prj_milestone: %s", e)
        return update_info

    def check_hw_milestone_exist_in_mytodo(self, t_id):
        queryset = CrmHwProjectMilestone.objects.filter(id=t_id)
        return any(x for x in queryset)

    def update_hw_prj_milestone(self, t_id, **data):
        self.logger.info("start update_hw_prj_milestone")
        update_result = False
        if data == {}:
            raise HwPrjUpdateInfoNotFound
        try:
            CrmHwProjectMilestone.objects.filter(id=t_id).update(**data)
            update_result = True
        except cx_Oracle.DatabaseError as e:
            self.logger.exception(
                "db exception in update_hw_prj_milestone: %s", e)
        self.logger.info(
            "end update_hw_prj_milestone, result: %s", update_result)
        return update_result

    @transaction.atomic
    def create_hw_prj_milestone(self, create_list):
        if create_list == []:
            raise HwPrjCreateInfoNotFound()

        self.logger.info("create hw prj milestone")
        create_hw_prj_milestone_list = list()
        for eachrow in create_list:
            create_hw_prj_milestone_list.append(
                CrmHwProjectMilestone(**eachrow))

        # note: check for real data to decide whether to adopt page
        # insert, ex. 1000/per commit
        self.logger.info("start bulk create_hw_prj_milestone")
        CrmHwProjectMilestone.objects.bulk_create(
            create_hw_prj_milestone_list, batch_size=BULK_BATCH_SIZE)
        self.logger.info("end bulk create_hw_prj_milestone")
        return True

    def check_cr_bu_type(self, cr_id):
        last_sync = self.sync_helper.get_lastest_sync_job_id(MdMeta.ActivityId)

        queryset = ActivityCr.objects.filter(
            cr_id=cr_id, activity_id=MdMeta.ActivityId, sync_job_id=last_sync['sync_job_id'])

        return any(x for x in queryset)

    @transaction.atomic
    def update_sync_record_for_sync_partial(self, act_id, last_sync_job_id, new_sync_job_id):
        '''
        Two steps for update sync record:
        1. create new record for sync job
        2. update activity cr while list with new sync job id
        '''

        SyncJob.objects.create(
            activity_id=act_id, sync_job_id=new_sync_job_id, is_active=Const.IS_ACTIVE)
        self.logger.info("create sync record in SyncJob")

        update_data = {
            "updated_time": timezone.now(),
            "sync_job_id": new_sync_job_id
        }

        ActivityCr.objects.filter(
            sync_job_id=last_sync_job_id).update(**update_data)
        return True

    def check_hw_prj_is_compelted(self, hw_type, hw_prj_id):

        try:
            sql_condition = "WHERE is_deleted = 0 AND project_id = :hw_prj_id "
            bindvars = {"hw_prj_id": hw_prj_id}

            if hw_type == MdHwPrjType.Operator:
                sql_condition += "AND category = :category "
                bindvars.update(
                    {"category": MdHwPrjType.OperatorCategory.OPTR})
            elif hw_type == MdHwPrjType.FTA:
                sql_condition += "AND type IN (:h1, :h2) "
                bindvars.update(
                    {"h1": MdHwPrjType.FTAType.GCF, "h2": MdHwPrjType.FTAType.PTCRB})
            else:
                raise HwTypeNotFound()

            sql_start = "SELECT project_id, is_completed FROM eservice.cq_crm_milestone_v "

            sql = sql_start + sql_condition
            self.crm_sql_helper.execute(sql, bindvars)
            check_info = self.crm_sql_helper.getResult()

            total_milestone = len(check_info)
            is_completed_milestone = 0

            for eachdict in check_info:
                if eachdict['IS_COMPLETED'] == 1:
                    is_completed_milestone += 1

            return 1 if total_milestone == is_completed_milestone else 0
        except Exception as e:
            self.logger.exception("Exception: %s", e)
        return 0

    def __sync_activity_cr_while_list(self):
        '''
        Sync activity cr while list for CR review sys,
        Full query cr list, compare then create or update
        Loop handling for each activity, handle separately if more than one wits db
        1. get last sync info
        '''

        acts = self.get_acts_by_cat_type(CrMeta.ACT_CAT_TYPE)

        for act_id in acts.keys():
            db_scope = json.loads(acts[act_id])

            self.logger.info(
                "[Sync Activity CR While List] activity id: %s", act_id)
            self.logger.info("[step 1.] get last_sync_info")

            last_sync_info = self.sync_helper.get_lastest_sync_job_id(act_id)
            if last_sync_info:
                self.logger.info("%s", last_sync_info)
            else:
                last_sync_info[Const.SYNC_JOB_ID] = ""
                self.logger.info(
                    "null last_sync_info, take as first initial sync")

            # forloop if multiple WTIS data source
            for eachdb in db_scope.keys():
                prefix = "{}{}".format(CrMeta.PREFIX_SYNC_JOB_ID, eachdb)
                new_sync_job_id = DateHelper.get_new_sync_job_id(prefix)
                self.logger.info("new_sync_job_id: %s", new_sync_job_id)

                sync_result = False
                clan = self.get_clan(eachdb)
                if clan:
                    query_define = db_scope[eachdb]
                    wits_session = self.getWitsObject(clan, eachdb)
                    act_crs = wits_session.get_activity_cr_by_act_def(
                        query_define)

                    if act_crs:
                        sync_result = self.handle_act_crs(
                            wits_session, act_id, eachdb, act_crs, new_sync_job_id)
                    else:
                        self.logger.error(
                            "act_id '%s' %s no while list from wits", act_id, eachdb)
                else:
                    self.logger.error(
                        "%s no clan mapping, please add in CrMeta", eachdb)

                # if the first time, no last sync info
                if sync_result:
                    result = self.update_sync_record_for_sync_partial(
                        act_id, last_sync_info[Const.SYNC_JOB_ID], new_sync_job_id)
                    self.logger.info(
                        "[Sync Activity CR While List] activity id: %s, result %s", act_id, result)
                else:
                    self.logger.info(
                        "[Sync Activity CR While List] activity id: %s, sync fail", act_id)

    def get_act_cat_ids_by_cat_type(self, cat_type):
        queryset = ActivityCategory.objects.filter(
            active=1, act_cat_type=cat_type).values_list('activity_cat_id', flat=True).distinct()
        result = list(queryset)
        return result

    def get_acts_by_cat_type(self, cat_type):
        '''
        get activity detail for sync, contains check json format valid or not for db_scope
        '''
        act_cat_ids = self.get_act_cat_ids_by_cat_type(cat_type)
        acts_queryset = Activity.objects.filter(
            activity_cat_id__in=act_cat_ids, active=1)
        result = {}
        for eachrow in acts_queryset:
            tmp = {eachrow.activity_id: eachrow.db_scope}
            if eachrow.db_scope:
                check_result = self.check_json_format(eachrow.db_scope)
                if check_result:
                    result.update(tmp)
                else:
                    self.logger.error(
                        "act_id '%s' db_scope invalid json format or null", eachrow.activity_id)
                    self.logger.error("db_scope: %s", eachrow.db_scope)
        return result

    def check_json_format(self, string):
        try:
            json.loads(string)
        except ValueError:
            return False
        return True

    def get_clan(self, wits_db):
        clan = None
        try:
            clan = getattr(WitsClan, wits_db)
        except AttributeError:
            self.logger.error(
                "no mapping for wits_db %s, please add in WitsClan mapping", wits_db)
        except Exception as e:
            self.logger.exception("exception to get clan: %s", e)
        return clan

    def get_crs_while_list_by_act(self, activity_id, witsdb):
        queryset = ActivityCr.objects.filter(
            ~Q(active=0), activity_id=activity_id, cr_db=witsdb).values_list('cr_id', flat=True).distinct()
        cr_list = list(queryset)
        self.logger.info(
            "get act_id '%s' current act crs while list, qty %s", activity_id, len(cr_list))

        disable_queryset = ActivityCr.objects.filter(
            active=0, activity_id=activity_id, cr_db=witsdb).values_list('cr_id', flat=True).distinct()
        disable_cr_list = list(disable_queryset)

        return (cr_list, disable_cr_list)

    def check_cr_exist_in_mytodo(self, cr_id):
        queryset = Cr.objects.filter(cr_id=cr_id)
        return any(x for x in queryset)

    def handle_act_crs(self, wits_session, act_id, witsdb, act_crs, new_sync_job_id):
        (ori_while_list, ori_disable_list) = self.get_crs_while_list_by_act(
            act_id, witsdb)
        whole_new_cr_list = []
        tmp_act_cr_create_list = list(set(act_crs) - set(ori_while_list))
        re_enable_cr_list = []
        act_cr_create_list = []
        act_cr_disable_list = list(set(ori_while_list) - set(act_crs))

        for eachcr in tmp_act_cr_create_list:
            if eachcr in ori_disable_list:
                self.logger.info("re-enable %s in activity while list", eachcr)
                re_enable_cr_list.append(eachcr)
            else:
                act_cr_create_list.append(eachcr)
                tmp_result = self.check_cr_exist_in_mytodo(eachcr)

                if not tmp_result:  # new CR, need to create
                    whole_new_cr_list.append(eachcr)
                else:
                    self.logger.info(
                        "cr %s exists in mytodo but haven't in act_id '%s' while list", eachcr, act_id)

        update_result = self.handle_update_act_cr(
            act_id, act_cr_disable_list, re_enable_cr_list)
        create_result = self.handle_create_act_cr(
            wits_session, act_id, witsdb, new_sync_job_id, whole_new_cr_list, act_cr_create_list)

        if update_result and create_result:
            return True

    def handle_update_act_cr(self, act_id, act_cr_disable_list, re_enable_cr_list):
        if act_cr_disable_list:
            # soft delete
            ActivityCr.objects.filter(activity_id=act_id, cr_id__in=act_cr_disable_list).update(
                active=Const.NOT_ACTIVE, updated_time=timezone.now())
            self.logger.info("soft delete success for %s", act_cr_disable_list)

        if re_enable_cr_list:
            ActivityCr.objects.filter(activity_id=act_id, cr_id__in=re_enable_cr_list).update(
                active=Const.IS_ACTIVE, updated_time=timezone.now())
            self.logger.info("re-enable success for %s", re_enable_cr_list)
        self.logger.info("finish update activity cr whilelist")
        return True

    def handle_create_act_cr(self, wits, act_id, witsdb, new_sync_job_id, whole_new_cr_list, new_act_cr_list):
        self.logger.info(
            "start for act_id '%s' create cr and activity cr", act_id)
        # get cr info one by one
        cr_detail_list = []
        for new_cr in whole_new_cr_list:
            cr_info = wits.get_cr_info(new_cr)
            cr_detail_list.append(cr_info)

        # start to create
        # bulk create first, create one by one if bulk creat fail
        if cr_detail_list:
            insert_result = self.insert_cr(cr_detail_list)
            if insert_result:
                self.logger.info(
                    "act_id '%s' bulk create successfully", act_id)
            else:
                self.logger.info(
                    "act_id '%s' bulk create fail, create one by one", act_id)

                for each_cr_info in cr_detail_list:
                    result = self.insert_one_cr(each_cr_info)
                    if result:
                        self.logger.info(
                            "create cr %s successfully", each_cr_info[CrFieldMap.Wits.id])
                    else:
                        # fail create CR should remove, not to create act cr
                        # while list
                        self.logger.error("create cr %s fail",
                                          each_cr_info[CrFieldMap.Wits.id])
                        new_act_cr_list.remove(each_cr_info)
                self.logger.info("finish create cr one by one")
        # define create time
        create_result = self.create_act_cr_while_list(
            act_id, witsdb, new_act_cr_list, new_sync_job_id)
        return create_result

    def create_act_cr_while_list(self, act_id, witsdb, new_act_cr_list, new_sync_job_id):
        result = False
        try:
            if new_act_cr_list:
                result_sync_job_id = self.insert_act_cr(
                    act_id, new_sync_job_id, new_act_cr_list, witsdb)
                self.logger.info(
                    "create act_id '%s' activity cr while list successfully", act_id)
                result = True if result_sync_job_id == new_sync_job_id else False
            else:
                self.logger.info("no new activity cr while list")
                result = True
        except Exception as e:
            self.logger.error(
                "create act_id '%s' activity cr while list fail: %s", act_id, e)
        return result

    def __sync_users_depts(self):
        '''
        Sync users and depts, sources from ODR & WITS/ALPS
        For users, <>mtk% is from WITS/ALPS, mtk% is from ODR
        For depts, only from ODR

        1. Sync <>mtk% from WITS/ALPS
        2. Sync mtk% from ODR
        3. Sync depts from ODR

        General rule, get all and compare all. update if exists, disable if source disable or non-exist, create if source created
        No last update time flag in both source and destination db
        '''
        try:
            self.logger.info("[Start Sync Users Depts]")
            odr_session = SQLHelper(settings.ODR_CONNECTION_STRING)
            odr_session.connect()
            self.sync_mtk_users(odr_session)
            self.sync_depts(odr_session)
        except Exception as e:
            self.logger.exception("exception: %s", e)
        finally:
            del odr_session
            self.logger.info("[End Sync Users Depts]")

    def sync_depts(self, odr_session):
        disable_result = True
        update_result = True
        create_result = True
        new_depts = None
        try:
            self.logger.info("[3. Start Depts Sync from ODR]")
            odr_depts = self.get_odr_depts(odr_session)
            mytodo_depts = self.get_mytodo_depts()

            if not odr_depts or not mytodo_depts:
                self.logger.error(
                    "couldn't get any data from ODR or MYTODO, skip sync")
                raise DataSourceIncomplete()

            disable_depts = set(mytodo_depts) - set(odr_depts)
            disable_result = self.disable_depts(disable_depts, **mytodo_depts)

            new_depts = set(odr_depts) - set(mytodo_depts)
            create_result = self.create_depts(new_depts, **odr_depts)

            update_depts = list(odr_depts.keys() - new_depts - disable_depts)
            for eachdept in update_depts:
                # remove dept_id becasue key don't need to check update
                del odr_depts[eachdept][DeptsFieldMap.DEPT_ID]
                # check diff and update
                update_info = {}
                for data in odr_depts[eachdept]:
                    if odr_depts[eachdept][data] != mytodo_depts[eachdept][data]:
                        update_info.update({data: odr_depts[eachdept][data]})
                if update_info:
                    try:
                        self.logger.info(
                            "update %s, details %s, result: %s", eachdept, update_info, update_result)
                        self.update_depts(eachdept, **update_info)
                    except Exception as e:
                        update_result &= False
                        self.logger.error("update fail: %s", e)
        except DataSourceIncomplete as e:
            self.logger.error("Sync MTK Users exception: %s", e.msg)
        finally:
            self.logger.info("disable_result: %s", disable_result)
            self.logger.info("create_result: %s, list: %s",
                             create_result, new_depts)
            self.logger.info("update_result: %s", update_result)
            self.logger.info("[3. End Depts Sync from ODR]")

    def sync_mtk_users(self, odr_session):
        disable_result = True
        update_result = True
        create_result = True
        new_users = None
        try:
            self.logger.info("[2. Start MTK Users Sync from ODR]")
            odr_users = self.get_odr_users(odr_session)
            mytodo_users = self.get_mytodo_users(Const.MTK_PREFIX)

            if not odr_users or not mytodo_users:
                self.logger.error(
                    "couldn't get any data from ODR or MYTODO, skip sync")
                raise DataSourceIncomplete()

            disable_users = set(mytodo_users) - set(odr_users)
            disable_result = self.disable_users(disable_users, **mytodo_users)

            new_users = set(odr_users) - set(mytodo_users)
            create_result = self.create_users(new_users, **odr_users)

            update_users = list(odr_users.keys() - new_users - disable_users)
            for eachuser in update_users:
                # remove login_name becasue key don't need to check update
                del odr_users[eachuser][UsersFieldMap.LOGIN_NAME]
                # check diff and update
                update_info = {}
                for data in odr_users[eachuser]:
                    if odr_users[eachuser][data] != mytodo_users[eachuser][data]:
                        update_info.update({data: odr_users[eachuser][data]})
                if update_info:
                    try:
                        self.logger.info(
                            "update %s, details %s", eachuser, update_info)
                        self.update_users(eachuser, **update_info)
                    except Exception as e:
                        update_result &= False
                        self.logger.error("update fail: %s", e)
        except DataSourceIncomplete as e:
            self.logger.error("Sync MTK Users error: %s", e.msg)
        except Exception as e:
            self.logger.exception("Sync MTK Users exception: %s", e)
        finally:
            self.logger.info("disable_result: %s", disable_result)
            self.logger.info("create_result: %s, detail: %s",
                             create_result, new_users)
            self.logger.info("update_result: %s", update_result)
            self.logger.info("[2. End MTK Users Sync from ODR]")

    def get_odr_depts(self, session):
        format_depts = {}
        total_field_name = "total"
        count_field = "count(*) as {}".format(total_field_name)
        fields = "d.department_id, d.department_name, d.department_site, d.department_manager, d.parent_department"
        table = "V_SST_DEPARTMENT d"

        # check how many records for depts
        count_sql = "select {fields} from {table}".format(
            fields=count_field, table=table)
        count_result = session.getTotalCount(count_sql, total_field_name)

        if count_result:
            sql = "select {fields} from {table}".format(
                fields=fields, table=table)
            session.execute(sql, no_of_records=count_result)
            depts = session.getResult()
            format_depts = self.format_odr_depts(depts)
        return format_depts

    def format_odr_depts(self, depts):
        format_result = {}

        for eachrow in depts:
            key = str(eachrow["DEPARTMENT_ID"])
            values = {
                DeptsFieldMap.DEPT_ID: key,
                DeptsFieldMap.DEPT_NAME: eachrow["DEPARTMENT_NAME"] if eachrow["DEPARTMENT_NAME"] else "",
                DeptsFieldMap.SITE: eachrow["DEPARTMENT_SITE"] if eachrow["DEPARTMENT_SITE"] else "",
                DeptsFieldMap.DEPT_MANGR: eachrow["DEPARTMENT_MANAGER"].lower() if eachrow["DEPARTMENT_MANAGER"] else "",
                DeptsFieldMap.PARENT_DEPT: eachrow["PARENT_DEPARTMENT"] if eachrow["PARENT_DEPARTMENT"] else ""
            }
            format_result[key] = values
        return format_result

    def get_mytodo_depts(self):
        depts = {}
        depts_obj = Depts.objects.all()

        for eachrow in depts_obj:
            key = str(eachrow.dept_id)
            values = {
                DeptsFieldMap.DEPT_NAME: eachrow.dept_name,
                DeptsFieldMap.IS_ACTIVE: eachrow.is_active,
                DeptsFieldMap.SITE: eachrow.site,
                DeptsFieldMap.DEPT_MANGR: eachrow.dept_mangr,
                DeptsFieldMap.PARENT_DEPT: eachrow.parent_dept
            }
            depts[key] = values
        return depts

    def get_odr_users(self, session):
        format_users = {}
        total_field_name = "total"
        count_field = "count(*) as {}".format(total_field_name)
        fields = "e.employee_id, e.english_name, e.email, e.site, e.department_id, e.status, d.department_manager, d.department_name"
        table = "V_SST_EMPLOYEE e"
        join_table = "V_SST_DEPARTMENT d"
        relation = "e.department_id = d.department_id"

        # check how many records for users
        count_sql = "select {fields} from {table} left join {join_table} on {relation}".format(
            fields=count_field, table=table, join_table=join_table, relation=relation)
        count_result = session.getTotalCount(count_sql, total_field_name)

        if count_result:
            sql = "select {fields} from {table} left join {join_table} on {relation}".format(
                fields=fields, table=table, join_table=join_table, relation=relation)
            session.execute(sql, no_of_records=count_result)
            users = session.getResult()
            format_users = self.format_odr_users(users)
        return format_users

    def format_odr_users(self, users):
        format_result = {}

        for eachrow in users:
            key = eachrow["EMPLOYEE_ID"].lower()
            values = {
                UsersFieldMap.LOGIN_NAME: key,
                UsersFieldMap.DEPT_ID: int(eachrow["DEPARTMENT_ID"]) if eachrow["DEPARTMENT_ID"] else "",
                UsersFieldMap.FULL_NAME: eachrow["ENGLISH_NAME"] if eachrow["ENGLISH_NAME"] else "",
                UsersFieldMap.E_MAIL: eachrow["EMAIL"].lower() if eachrow["EMAIL"] else "",
                UsersFieldMap.IS_ACTIVE: True if eachrow["STATUS"].lower() == Const.ACTIVE.lower() else False,
                UsersFieldMap.DEPT_NAME: eachrow["DEPARTMENT_NAME"] if eachrow["DEPARTMENT_NAME"] else "",
                UsersFieldMap.SITE: eachrow["SITE"] if eachrow["SITE"] else "",
                UsersFieldMap.REPORTING_MANAGER: eachrow["DEPARTMENT_MANAGER"].lower(
                ) if eachrow["DEPARTMENT_MANAGER"] else ""
            }
            format_result[key] = values
        return format_result

    def sync_not_mtk_users(self):
        disable_result = True
        update_result = True
        create_result = True
        new_users = None

        try:
            self.logger.info("[1. Start Not MTK Users Sync]")
            wits_session = self.getWitsObject(WitsClan.ALPS, WitsDb.ALPS)
            wits_users = wits_session.get_not_mtk_users()
            mytodo_users = self.get_mytodo_users(Const.NOT_MTK)

            if not wits_users or not mytodo_users:
                self.logger.error(
                    "couldn't get any data from ODR or MYTODO, skip sync")
                raise DataSourceIncomplete()

            disable_users = set(mytodo_users) - set(wits_users)
            disable_result = self.disable_users(disable_users, **mytodo_users)

            new_users = set(wits_users) - set(mytodo_users)
            create_result = self.create_users(new_users, **wits_users)

            update_result = True
            update_users = list(wits_users.keys() - new_users - disable_users)
            for eachuser in update_users:
                # remove login_name becasue key don't need to check update
                del wits_users[eachuser][UsersFieldMap.LOGIN_NAME]
                # check diff and update
                update_info = {}
                for data in wits_users[eachuser]:
                    if wits_users[eachuser][data] != mytodo_users[eachuser][data]:
                        update_info.update({data: wits_users[eachuser][data]})
                if update_info:
                    try:
                        self.update_users(eachuser, **update_info)
                    except Exception as e:
                        update_result &= False
                        self.logger.error("update %s fail: %s", eachuser, e)
        except DataSourceIncomplete as e:
            self.logger.error("Sync Not MTK Users error: %s", e.msg)
        except Exception as e:
            self.logger.exception("Sync Not MTK Users exception: %s", e)
        finally:
            self.logger.info("disable_result: %s", disable_result)
            self.logger.info("create_result: %s, detail: %s",
                             create_result, new_users)
            self.logger.info("update_result: %s", update_result)
            self.logger.info("[1. End Not MTK Users Sync]")

    def create_users(self, new_users, **wits_users):
        result = True
        new_users_list = []
        for eachnew in new_users:
            new_users_list.append(wits_users[eachnew])
        try:
            self.insert_users(new_users_list)
        except Exception as e:
            self.logger.exception("create users fail exception: %s", e)
            result = False
        return result

    def disable_users(self, disable_list, **mytodo_users):
        result = True
        disable_info = {UsersFieldMap.IS_ACTIVE: False}
        for login_name in disable_list:
            check_result = mytodo_users[login_name][UsersFieldMap.IS_ACTIVE]
            # update if is_active ori is True, need to be disable
            if check_result:
                self.logger.info("disable %s", login_name)
                try:
                    self.update_users(login_name, **disable_info)
                except Exception:
                    result &= False
        return result

    def get_mytodo_users(self, user_type):
        users = {}
        users_obj = None

        if user_type == Const.MTK_PREFIX:
            users_obj = Users.objects.filter(
                login_name__startswith=Const.MTK_PREFIX)
        elif user_type == Const.NOT_MTK:
            users_obj = Users.objects.filter(
                ~Q(login_name__startswith=Const.MTK_PREFIX))
        else:
            self.logger.error("no user_type, return")
            return

        for eachrow in users_obj:
            key = eachrow.login_name
            values = {
                UsersFieldMap.DEPT_ID: eachrow.dept_id,
                UsersFieldMap.FULL_NAME: eachrow.full_name,
                UsersFieldMap.E_MAIL: eachrow.e_mail,
                UsersFieldMap.IS_ACTIVE: eachrow.is_active,
                UsersFieldMap.DEPT_NAME: eachrow.dept_name,
                UsersFieldMap.SITE: eachrow.site,
                UsersFieldMap.REPORTING_MANAGER: eachrow.reporting_manager
            }
            users[key] = values
        return users

    @transaction.atomic
    def insert_users(self, all_users):
        users_insert_list = list()
        for eachuser in all_users:
            users_insert_list.append(Users(**eachuser))
        Users.objects.bulk_create(
            users_insert_list, batch_size=BULK_BATCH_SIZE)

    def update_users(self, key, **update_info):
        update_info.update(updated_time=timezone.now())
        Users.objects.filter(login_name=key).update(**update_info)

    def create_depts(self, new_depts, **odr_depts):
        result = True
        new_depts_list = []
        for eachnew in new_depts:
            odr_depts[eachnew][DeptsFieldMap.IS_ACTIVE] = True
            new_depts_list.append(odr_depts[eachnew])
        try:
            result = self.insert_depts(new_depts_list)
        except Exception as e:
            self.logger.exception("fail: %s", e)
            result = False
        return result

    def disable_depts(self, disable_list, **mytodo_depts):
        result = True
        disable_info = {DeptsFieldMap.IS_ACTIVE: False}
        for dept_id in disable_list:
            check_result = mytodo_depts[dept_id][DeptsFieldMap.IS_ACTIVE]
            # update if is_active ori is True, need to be disable
            if check_result:
                self.logger.info("disable %s", dept_id)
                try:
                    self.update_depts(dept_id, **disable_info)
                except Exception:
                    result &= False
        return result

    def update_depts(self, key, **update_info):
        update_info.update(updated_time=timezone.now())
        Depts.objects.filter(dept_id=key).update(**update_info)

    @transaction.atomic
    def insert_depts(self, all_depts):
        depts_insert_list = list()
        for eachdept in all_depts:
            depts_insert_list.append(Depts(**eachdept))
        Depts.objects.bulk_create(
            depts_insert_list, batch_size=BULK_BATCH_SIZE)

    def format_specific_hw_prj_info(self, hw_type, data):
        '''
        For check is_completed/start_date/end_date
        '''
        _raw_hw_prj_milestone = self.get_crm_hw_prj_milestone(
            hw_type, exclude_delete=True, hw_id=data["hw_project_id"], operator=data["operator"])
        data["completed"], data["start_date"], data["end_date"], data["is_active"] = self.get_specific_hw_prj(
            _raw_hw_prj_milestone, data["completed"], data["start_date"], data["end_date"], data["is_active"])
        return data

    def get_specific_hw_prj(self, raw_hw_prj_milestone, ori_completed, ori_start, ori_end, ori_active):
        '''
        check and format hw prj info
        special column: completed/start_date/end_date
        '''

        final_start_date = ori_start
        final_end_date = ori_end
        final_completed = ori_completed
        final_disable = 1

        for eachrow in raw_hw_prj_milestone:
            start_date = DateHelper.datetime_set_tz(eachrow["START_DATE"])
            end_date = DateHelper.datetime_set_tz(eachrow["END_DATE"])
            is_completed = eachrow["IS_COMPLETED"]
            is_delete = eachrow["IS_DELETED"]

            final_completed &= is_completed
            final_disable &= is_delete

            if start_date and final_start_date:
                start_time_diff = start_date - final_start_date
                if start_time_diff.days < 0:
                    final_start_date = start_date

            if not final_start_date:
                final_start_date = start_date

            if end_date and final_end_date:
                end_time_diff = end_date - final_end_date
                if end_time_diff.days > 0:
                    final_end_date = end_date

            if not final_end_date:
                final_end_date = end_date

        final_active = 0 if final_disable else 1
        return final_completed, final_start_date, final_end_date, final_active
