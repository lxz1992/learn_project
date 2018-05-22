import logging

from cr_review_sys.const import CrPriority
from cr_review_sys.models import Cr, OpGroup, CrmHwProject
from md_analysis.const import MdState, Ces, LOG_TRACE_LVL, MdMeta
from md_analysis.errors import InvalidYearInterval
from md_analysis.util.query_helper import QueryHelper
from my_to_do.util import Singleton
from my_to_do.util.date_helper import DateHelper
from my_to_do.util.sync_helper import SyncHelper


class CrListService(object, metaclass=Singleton):
    '''
    Get Project List API
    '''

    def __init__(self):
        '''constructor
        '''
        self.logger = logging.getLogger('aplogger')
        self.sync_helper = SyncHelper()
        self.query_helper = QueryHelper()

    def get_country_list_by_group(self, group_list):
        queryset = OpGroup.objects.filter(
            type=Ces.GROUP, group_name__in=group_list)

        country_list = []

        for eachrow in queryset:
            t_country = eachrow.value
            country_list.append(t_country)

        self.logger.info("[%s] country list:%s", group_list, country_list)
        return country_list

    def get_all_country_list_by_group(self):
        queryset = OpGroup.objects.filter(type=Ces.GROUP)

        country_list = []

        for eachrow in queryset:
            t_country = eachrow.value
            country_list.append(t_country)

        self.logger.info("all country list:%s", country_list)
        return country_list

    def get_hw_prj_name(self, hw_prj_id):

        hw_prj_name = None
        queryset = CrmHwProject.objects.filter(hw_project_id=hw_prj_id)

        for eachrow in queryset:
            hw_prj_name = eachrow.hw_project_name

        self.logger.log(LOG_TRACE_LVL, "[%s] name:%s", hw_prj_id, hw_prj_name)
        return hw_prj_name

    def get_cr_list_all_data(self, p_state, p_from_year, p_to_year, p_country, p_group, p_operator, act_cr_list, p_ww_operator):

        self.logger.info(
            "begin to get_cr_list_all_data")

        queryset = {}

        if p_state is not None and p_from_year is not None and p_to_year is not None and p_country is not None:
            self.logger.info("query cr list for wwstatistic map, state: %s, to: %s, from: %s, country: %s",
                             p_state, p_from_year, p_to_year, p_country)

            if int(p_from_year) > int(p_to_year):
                raise InvalidYearInterval()

            (p_from_year, p_to_year) = DateHelper.get_year_datetime_for_query(
                p_from_year, p_to_year)

            state_condition = [e.value for e in getattr(MdState, p_state)]

            # only query urgent cr if contains p_ww_operator input
            if p_ww_operator:
                self.logger.info("query only urgent cr for %s", p_ww_operator)
                queryset = Cr.objects.filter(state__in=state_condition, country__iexact=p_country,
                                             operator__isnull=False, submit_date__range=(p_from_year, p_to_year), operator__iexact=p_ww_operator, priority=CrPriority.Urgent)
            else:
                queryset = Cr.objects.filter(state__in=state_condition, country__iexact=p_country,
                                             operator__isnull=False, submit_date__range=(p_from_year, p_to_year))
        elif p_operator is not None:
            # for urgent CR, only operator name couldn't directly map with CR
            # md_info_op_name, since it might be empty
            # thus, query hw prj id first and then query cr
            # by filtering hw prj id and cr proiorty
            self.logger.info("query cr list for urgent cr")
            state_condition = self.sync_helper.get_md_open_state_list()
            hw_prj_id_list = self.get_hw_prj_id_list_by_operator(p_operator)

            queryset = Cr.objects.filter(
                hw_project_id__in=hw_prj_id_list, priority=CrPriority.Urgent, state__in=state_condition, md_info_op_name__iexact=p_operator)
        elif p_country is not None:
            self.logger.info(
                "query cr list for CES cr by country, country: %s", p_country)

            state_condition = self.sync_helper.get_md_open_state_list()

            queryset = Cr.objects.filter(
                md_info_country__iexact=p_country, state__in=state_condition)
        elif p_group is not None:
            self.logger.info("query cr list for CES cr by group: %s", p_group)

            state_condition = self.sync_helper.get_md_open_state_list()

            if p_group.lower() == Ces.OTHERS:
                all_country_list = self.get_all_country_list_by_group()
                queryset = Cr.objects.filter(state__in=state_condition).exclude(
                    md_info_country__in=all_country_list)
            else:
                country_list = self.get_country_list_by_group([p_group])
                queryset = Cr.objects.filter(
                    md_info_op_name__in=country_list, state__in=state_condition)

        data = []

        for eachrow in queryset:
            t_crid = eachrow.cr_id

            check_activity = self.query_helper.check_cr_in_activity(
                t_crid, activity_id=MdMeta.ActivityId)

            if not check_activity:
                continue

            if t_crid in act_cr_list:
                t_title = eachrow.title
                t_priority = eachrow.priority
                t_customer = eachrow.customer_company
                t_assignee = eachrow.assignee
                t_class = eachrow.cr_class
                t_state = eachrow.state
                t_submit_date = eachrow.submit_date
                t_platform = eachrow.platform_group
                t_operator = eachrow.md_info_op_name
                t_rat = eachrow.rat1
                t_rat2 = eachrow.rat2
                t_country = eachrow.md_info_country
                t_plmn = eachrow.plmn1
                t_plmn2 = eachrow.plmn2
                t_tac_lac = eachrow.tac_lac
                t_cell_id = eachrow.cell_id
                t_sv_mce_effort = eachrow.sv_mce_effort
                t_resolution = eachrow.resolution
                t_patch_id = eachrow.patch_id
                t_solution = eachrow.solution
                t_hw_prj_name = self.get_hw_prj_name(eachrow.hw_project_id)
                t_assign_date = eachrow.assign_date
                t_module = eachrow.solution_category_level2
                t_dept = eachrow.assignee_dept

                cr_detail = [
                    t_crid,
                    t_title,
                    t_priority,
                    t_customer,
                    t_dept,
                    t_assignee,
                    t_class,
                    t_state,
                    t_submit_date,
                    t_platform,
                    t_operator,
                    t_rat,
                    t_module,
                    t_country,
                    t_plmn,
                    t_plmn2,
                    t_rat2,
                    t_tac_lac,
                    t_cell_id,
                    t_sv_mce_effort,
                    None,  # countrycode, didn't show in UI, keep None
                    t_resolution,
                    t_patch_id,
                    t_solution,
                    t_hw_prj_name,  # mapping to hw project name,
                    t_assign_date
                ]

                self.logger.log(LOG_TRACE_LVL, "append %s into result", t_crid)
                data.append(cr_detail)
            else:
                self.logger.log(LOG_TRACE_LVL,
                                "%s not in this activity", t_crid)
                pass

        self.logger.info("end to get_cr_list_all_data")

        if data == []:
            self.logger.warning("there's no cr list after parsing")
        return data

    def get_hw_prj_id_list_by_operator(self, operator):
        queryset = CrmHwProject.objects.filter(operator__iexact=operator).values_list(
            'hw_project_id', flat=True).distinct()

        hw_prj_id_list = list(queryset)
        return hw_prj_id_list
