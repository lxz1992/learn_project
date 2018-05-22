import datetime
import logging

from cr_review_sys.models import CrmHwProject, CrmHwProjectMilestone
from md_analysis.const import MdPrjStatus, LOG_TRACE_LVL, MdHwPrjType
from md_analysis.errors import DbDataNotFound, ParseResultNotFound
from md_analysis.util.status_helper import StatusHelper
from my_to_do.util import Singleton
from my_to_do.util.date_helper import DateHelper


class PrjListService(object, metaclass=Singleton):
    '''
    Get Project List API
    '''

    def __init__(self):
        '''constructor
        '''
        self.logger = logging.getLogger('aplogger')

    def get_prj_list_all_data(self, operator):

        self.logger.info(
            "begin to get_prj_list_all_data for operator: %s", operator)
        final_data = []
        queryset = CrmHwProject.objects.filter(completed=0, operator__iexact=operator)

        self.logger.info(
            "begin to handle get_prj_list_all_data")

        for eachrow in queryset:
            t_hw_prj_id = eachrow.hw_project_id
            t_company = eachrow.company
            t_hw_prj_name = eachrow.hw_project_name
            t_platform = eachrow.platform
            t_swpm = eachrow.swpm_fullname
            t_type = eachrow.hw_type
            t_start_date = eachrow.start_date

            (start_year, start_week) = DateHelper.calculate_mtk_week(t_start_date)
            prj_status = StatusHelper.get_prj_status(start_year, start_week)

            if not prj_status:
                self.logger.log(
                    LOG_TRACE_LVL, "invalid prj status, skip", t_hw_prj_id, t_hw_prj_name)
                continue

            tmp_data = self.get_milestone_infor_by_prj(
                t_hw_prj_id, t_company, t_hw_prj_name, t_platform, t_swpm, t_type, operator)
            final_data += tmp_data
        self.logger.info(
            "end to handle get_prj_list_all_data")
        return final_data

    def get_milestone_infor_by_prj(self, hw_prj_id, company, prj_name, platform, swpm, prj_type, operator):

        prj_data = []
        type_value = MdHwPrjType.OperatorCategory.TYPE
        queryset = CrmHwProjectMilestone.objects.filter(
            hw_project_id=hw_prj_id, type__contains=type_value, operator__iexact=operator)

        for eachrow in queryset:
            milestone_name = eachrow.milestone_name
            with_volte = eachrow.with_vote
            with_wfc = eachrow.with_wfc
            with_vlte = eachrow.with_vilte
            start_date = eachrow.start_date
            end_date = eachrow.end_date
            is_completed = eachrow.completed

            prj_detail = [
                hw_prj_id,
                company,
                prj_name,
                platform,
                swpm,
                prj_type,
                milestone_name,
                start_date,
                end_date,
                with_volte,
                with_wfc,
                with_vlte,
                is_completed
            ]
            prj_data.append(prj_detail)
        return prj_data
