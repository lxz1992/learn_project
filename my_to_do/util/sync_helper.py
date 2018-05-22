import logging
import re

from cr_review_sys.const import Const, CrFieldMap
from cr_review_sys.models import SyncJob, ActivityCr, Users, OpArea, MdMccMnc
from md_analysis.const import MdState
from my_to_do.util import Singleton
from my_to_do.util.date_helper import DateHelper


class SyncHelper(object, metaclass=Singleton):

    def __init__(self):
        self.logger = logging.getLogger('aplogger')
        self.__act_crs_keeper = {}

    def get_lastest_sync_job_id(self, act_id):
        updating_sync = {}

        try:
            queryset = SyncJob.objects.filter(
                activity_id=act_id, is_active=Const.IS_ACTIVE).order_by('-created_time')[:1]

            for each in queryset:
                updating_sync[Const.SYNC_JOB_ID] = each.sync_job_id
                local_created_time = DateHelper.get_local_time(
                    each.created_time)
                updating_sync[Const.UPDATE_TIME] = local_created_time.strftime(
                    '%Y-%m-%d %H:%M:%S')
            self.logger.debug(
                "get_lastest_sync_job_id[%s][%s]: %s", act_id, updating_sync[Const.SYNC_JOB_ID], updating_sync[Const.UPDATE_TIME])

        except Exception as e:
            self.logger.exception('get_lastest_sync_job_id:%s', e)
        return updating_sync

    def get_act_cr_list(self, act_id, sync_job_id):
        act_cr_obj = self.__act_crs_keeper.get(act_id, {})
        # sync job id changed means data updated by frontend
        # cache empty list means data altered manually from db client or data
        # was outdated
        if act_cr_obj.get(Const.SYNC_JOB_ID, None) != sync_job_id or not act_cr_obj.get(Const.CR_LIST, []):
            self.logger.info("no cache existed! creating...")
            act_cr_obj[Const.CR_LIST] = []
            act_cr_obj[Const.SYNC_JOB_ID] = sync_job_id

            queryset = ActivityCr.objects.filter(
                activity_id=act_id, sync_job_id=sync_job_id)

            for eachrow in queryset:
                t_crid = eachrow.cr_id
                act_cr_obj[Const.CR_LIST].append(t_crid)

            self.__act_crs_keeper[act_id] = act_cr_obj
            self.logger.info("create cached act cr list: %s",
                             len(act_cr_obj[Const.CR_LIST]))
        else:
            self.logger.info("get cached act cr list: %s",
                             len(act_cr_obj[Const.CR_LIST]))

        return act_cr_obj[Const.CR_LIST]

    def get_latest_act_cr_list(self, act_id, sync_job_id, only_active=None):
        self.logger.info("[Current sync job id] %s", sync_job_id)

        data = {'sync_job_id': sync_job_id, 'activity_id': act_id}

        if only_active:
            data.update({'active': 1})

        queryset = ActivityCr.objects.order_by('cr_id').filter(
            **data).values_list('cr_id', flat=True).distinct()
        cr_id_list = list(queryset)
        return cr_id_list

    def get_user_site_map(self):
        result = {}
        queryset = Users.objects.values('login_name', 'site')
        for eachrow in queryset:
            result.update({eachrow['login_name']: {
                          'site': eachrow['site']}})
        return result

    def get_md_class(self, cr_class, resolution):
        md_class = None
        if cr_class == "New feature":
            md_class = "New feature"
        elif cr_class == "Change feature":
            md_class = "Change feature"
        elif cr_class == "Bug":
            if resolution == "Completed":
                md_class = "New bug"
            else:
                md_class = "Known bug"
        elif cr_class == "Question":
            md_class = "Non-bug"
        return md_class

    def get_patch_cr_type(self, cr_class, resolution):
        cr_type = None
        if cr_class == "Bug" and resolution == "Completed":
            return "New bug"
        elif resolution == "Duplicated":
            return "Known issue"
        elif cr_class == "Change feature" and resolution == "Completed":
            return "Change feature"
        elif cr_class == "New feature" and resolution == "Completed":
            return "New feature"
        return cr_type

    def get_op_area(self):
        result = {}
        queryset = OpArea.objects.all()
        for eachrow in queryset:
            result.update({eachrow.operator.upper(): eachrow.area})
        return result

    def get_md_open_state_list(self):
        state_condition = [e.value for e in getattr(
            MdState, MdState.Open.__name__)]
        return state_condition

    def get_country_operator_by_plmn(self, plmn):

        if not plmn:
            return (None, None)

        self.logger.info("check plmn %s", plmn)

        # special handling for plmn code
        # 1. ignore white spaces and split with . (to take care of xxxxxx.0
        tmp_result = plmn.strip().split(".")
        # 2. ignore English char
        real_plmn = re.sub("[A-Za-z]", "", tmp_result[0])
        # 3. ignore special char, ex. *^%$()-, etc.
        real_plmn = ''.join(e for e in real_plmn if e.isalnum())

        plmn1 = real_plmn[:3]
        plmn2 = real_plmn[3:]

        queryset = MdMccMnc.objects.filter(id="{}_{}".format(plmn1, plmn2))
        if not queryset:
            self.logger.error("no mapping for plmn code %s", real_plmn)

        final_country = None
        final_operator = None

        for eachrow in queryset:
            final_country = eachrow.country
            final_operator = eachrow.operator

        return (final_country, final_operator)

    def get_full_cr_info_with_plmn(self, **cr_info):

        # md cr needs extra mapping by plmn:
        # country/operator
        plmn = cr_info[CrFieldMap.Wits.MD_Info_PLMN1]
        (country, operator) = self.get_country_operator_by_plmn(plmn)

        cr_info.update({CrFieldMap.Custom.Country: country,
                        CrFieldMap.Custom.Operator: operator})
        return cr_info
