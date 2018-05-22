import datetime
from threading import Thread
import threading
from time import sleep

from cr_review_sys.const import Const
from cr_review_sys.errors import WrongParamError
from cr_review_sys.views import CrReviewBaseView
from md_analysis.const import MdMeta
from my_to_do.util.date_helper import DateHelper


# we put some simple views together for alike functions to avoid
# over-separation
class SyncUsersDeptsView(CrReviewBaseView):

    def api_get(self, request):

        result = {}
        act_update_status_id = Const.USERS_DEPTS_ID
        sync_interval = request.GET.get(Const.SYNC_INTERVAL, None)        
        get_last_time = request.GET.get(Const.GET_LAST_TIME, "")

        if not get_last_time:
            t = None
            if sync_interval:
                t = threading.Thread(target=self._wits_service.schedule_sync_data, name="ScheduleUpdateUserThread", args=(
                    act_update_status_id, sync_interval), daemon=True)
            else:
                # this entry is for manual update
                t = Thread(target=self._wits_service.safe_sync_data, name="UpdateUserThread", args=(
                    act_update_status_id, ), daemon=True)
            t.start()
            sleep(1)

        act_update_status = self._act_update_status_service.getActivityStatus(
            act_update_status_id)
        result[Const.STATUS] = act_update_status.status
        result[Const.LAST_UPDATE_TIME] = DateHelper.get_current_time_str()

        # let every client knows the latest update error
        if act_update_status.error_code or act_update_status.error_msg:
            result[Const.ERROR_CODE] = act_update_status.error_code
            result[Const.ERROR_MSG] = act_update_status.error_msg
        return result


class SyncDataView(CrReviewBaseView):

    def api_get(self, request):

        result = {}
        clan = request.GET.get(Const.CLAN)
        db = request.GET.get(Const.DB)
        sync_interval = request.GET.get(Const.SYNC_INTERVAL, None)
        act_id = request.GET.get(Const.ACTIVITY_ID, MdMeta.ActivityId)
        latest_sync = self._sync_helper.get_lastest_sync_job_id(act_id)
        get_last_time = request.GET.get(Const.GET_LAST_TIME, "")

        act_update_status_id = Const.MD_ANALYS_ACT_STATUS_ID if act_id == MdMeta.ActivityId else "update id if any"

        # check param
        if not clan or not db:
            raise WrongParamError(msg='please input clan/db')
        else:
            if not get_last_time:
                kwargs = {Const.CLAN: clan, Const.DB: db}
                t = None
                if sync_interval:
                    t = threading.Thread(target=self._wits_service.schedule_sync_data, name="ScheduleUpdateThread", args=(
                        act_update_status_id, sync_interval), kwargs=kwargs, daemon=True)
                else:
                    # this entry is for manual update
                    t = Thread(target=self._wits_service.safe_sync_data,
                               name="UpdateThread", args=(act_update_status_id, ), kwargs=kwargs, daemon=True)
                t.start()
                sleep(1)

        act_update_status = self._act_update_status_service.getActivityStatus(
            act_update_status_id)
        result[Const.STATUS] = act_update_status.status
        result[Const.LAST_UPDATE_TIME] = latest_sync[Const.UPDATE_TIME]

        # let every client knows the latest update error
        if act_update_status.error_code or act_update_status.error_msg:
            result[Const.ERROR_CODE] = act_update_status.error_code
            result[Const.ERROR_MSG] = act_update_status.error_msg
#                 act_update_status_service.updateActivityStatus(act_update_status_id, error_code=None, error_msg="")
        return result


class SyncActWhileListView(CrReviewBaseView):

    def api_get(self, request):
        result = {}
        act_update_status_id = Const.CR_REVIEW_ACT_WL_STATUS_ID
        sync_interval = request.GET.get(Const.SYNC_INTERVAL, None)     
        get_last_time = request.GET.get(Const.GET_LAST_TIME, "")

        if not get_last_time:
            t = None
            if sync_interval:
                t = threading.Thread(target=self._wits_service.schedule_sync_data, name="ScheduleUpdateActThread", args=(
                    act_update_status_id, sync_interval), daemon=True)
            else:
                # this entry is for manual update
                t = Thread(target=self._wits_service.safe_sync_data, name="UpdateActThread", args=(
                    act_update_status_id, ), daemon=True)
            t.start()
            sleep(1)

        act_update_status = self._act_update_status_service.getActivityStatus(
            act_update_status_id)
        result[Const.STATUS] = act_update_status.status
        result[Const.LAST_UPDATE_TIME] = DateHelper.get_current_time_str()

        # let every client knows the latest update error
        if act_update_status.error_code or act_update_status.error_msg:
            result[Const.ERROR_CODE] = act_update_status.error_code
            result[Const.ERROR_MSG] = act_update_status.error_msg

        return result
