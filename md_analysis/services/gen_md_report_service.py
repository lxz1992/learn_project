'''
Created on 2017.12.27

@author: MTK10809
'''
from collections import Counter
import logging

from django.db import transaction

from cr_review_sys.const import CrPriority, Const
from cr_review_sys.models import Cr, Wwstatistictop10,\
    Wwstatisticmap, ResolvedEserives, OpenEservices, CesSpecific, CrmHwProject,\
    OperatorCertification, Fta
from md_analysis.const import MdMeta, MdCrFieldMap, WwStatisticTop10Type,\
    WwStatisticTop10, MdState, WwStaMap, ResolvedEs, OpenEs, Ces, CrmHwPrj,\
    OpCert, MdHwPrjType, FTA, REPORT_BULK_BATCH_SIZE
from md_analysis.util.query_helper import QueryHelper
from md_analysis.util.status_helper import StatusHelper
from my_to_do.util import Singleton
from my_to_do.util.common_util import binary_search
from my_to_do.util.date_helper import DateHelper
from my_to_do.util.db_table_helper import DbTableHelper
from my_to_do.util.sync_helper import SyncHelper


class GenMdReportService(object, metaclass=Singleton):
    '''
    Generate MD used report for other backend API
    '''

    def __init__(self):
        '''constructor
        '''
        self.logger = logging.getLogger('aplogger')
        self.sync_job_id = None
        self.cr_info = []
        self.sync_helper = SyncHelper()
        self.user_site = self.sync_helper.get_user_site_map()
        self.hw_prj_info = []
        self.op_area_info = self.sync_helper.get_op_area()
        self.query_helper = QueryHelper()

    def gen_report_entry(self, sync_job_id, sync_type, last_sync_job_id):

        try:
            self.sync_job_id = sync_job_id

            # use last_sync_job_id for query activity cr because not only
            # existing but new added still use last_sync_job_id
            # for gen report, need to use new sync_job_id
            cr_id_list = self.sync_helper.get_latest_act_cr_list(
                MdMeta.ActivityId, last_sync_job_id, only_active=True)
            self.cr_info = self.get_cr_info_by_current_sync_job_id(cr_id_list)
            self.hw_prj_info = self.get_hw_prj_info_in_mytodo()

            # 1. Wwstatistic top 10
            wwsta_top10_raw = self.gen_wwstatistic_top10_raw()
            wwsta_top10 = self.transfer_data_for_wwsta_top10(wwsta_top10_raw)

            # 2. Wwstatistic map
            wwsta_map_raw = self.gen_wwstatistic_map_raw()
            wwsta_map = self.transfer_data_for_wwsta_map(wwsta_map_raw)

            # 3. Resolved eServices
            resolved_es_raw = self.gen_resolved_eservices_raw()
            resolved_es = self.transfer_data_for_resolved_eservices(
                resolved_es_raw)

            # 4. Open eServices
            open_es_raw = self.gen_open_eservices_raw()
            open_es = self.transfer_data_for_open_eservices(open_es_raw)

            # 5. Operator Certification
            op_cert_raw = self.gen_prj_status_raw(hw_type=MdHwPrjType.Operator)
            op_cert = self.transfer_op_data_for_prj_status(op_cert_raw)

            # 6. FTA
            fta_raw = self.gen_prj_status_raw(hw_type=MdHwPrjType.FTA)
            fta = self.transfer_fta_data_for_prj_status(fta_raw)

            # 7. CES Specific
            ces_raw = self.gen_ces_raw()
            ces = self.transfer_data_for_ces(ces_raw)

            self.create_all_report_in_db(
                wwsta_top10, wwsta_map, resolved_es, open_es, op_cert, fta, ces)

        except Exception as e:
            self.logger.exception(
                "[SyncJobId %s] Exception in get data for report table: %s", self.sync_job_id, e)

            if sync_type == Const.PARTIALSYNC:
                raise

        self.logger.info(
            "[SyncJobId %s] finish to generate report table", self.sync_job_id)

    def get_cr_info_by_current_sync_job_id(self, cr_id_list):
        queryset = Cr.objects.all()
        filteredCrs = filter(lambda x: binary_search(
            cr_id_list, x.cr_id) != -1, queryset)

        def mapToObj(eachrow):
            return {
                MdCrFieldMap.CR_ID: eachrow.cr_id,
                MdCrFieldMap.SUBMIT_DATE: eachrow.submit_date,
                MdCrFieldMap.PRIORITY: eachrow.priority if eachrow.priority else "",
                MdCrFieldMap.CUSTOMER: eachrow.customer_company if eachrow.customer_company else "",
                MdCrFieldMap.COUNTRY: eachrow.md_info_country if eachrow.md_info_country else "",
                MdCrFieldMap.OPERATOR: eachrow.md_info_op_name if eachrow.md_info_op_name else "",
                MdCrFieldMap.STATE: eachrow.state if eachrow.state else "",
                MdCrFieldMap.CR_CLASS: eachrow.cr_class if eachrow.cr_class else "",
                MdCrFieldMap.RESOLUTION: eachrow.resolution if eachrow.resolution else "",
                MdCrFieldMap.ASSIGNEE_DEPT: eachrow.assignee_dept if eachrow.assignee_dept else "",
                MdCrFieldMap.RESOLVE_TIME: eachrow.resolve_time if eachrow.resolve_time else 0,  # null or 0
                MdCrFieldMap.ASSIGNEE: eachrow.assignee if eachrow.assignee else "",
                MdCrFieldMap.WW_COUNTRY: eachrow.country if eachrow.country else "",
                MdCrFieldMap.WW_OPERATOR: eachrow.operator if eachrow.operator else "",
                MdCrFieldMap.RESOLVE_DATE: eachrow.resolve_date if eachrow.resolve_date else ""
            }

        # you can choose return a list either, but in iterator mode, it's more
        # efficient
        tempCrs = list(map(mapToObj, filteredCrs))
        self.logger.info("cr_id_list qty: %s, cr_info qty: %s",
                         len(cr_id_list), len(tempCrs))
        return tempCrs

    def gen_wwstatistic_top10_raw(self):
        result = {}
        for eachdict in self.cr_info:
            period = eachdict[MdCrFieldMap.SUBMIT_DATE].year
            customer = eachdict.get(MdCrFieldMap.CUSTOMER, None)
            operator = eachdict.get(MdCrFieldMap.OPERATOR, None)
            country = eachdict.get(MdCrFieldMap.COUNTRY, None)
            priority = eachdict.get(MdCrFieldMap.PRIORITY, None)

            customer_key = None
            operator_key = None
            country_key = None
            check_list = []

            if customer:
                customer_key = "{a}{delimit}{b}{delimit}{c}{delimit}{d}".format(
                    delimit=MdMeta.Delimit, a=period, b=WwStatisticTop10Type.Customer, c=customer, d=priority)
                check_list.append(customer_key)
            if operator:
                operator_key = "{a}{delimit}{b}{delimit}{c}{delimit}{d}".format(
                    delimit=MdMeta.Delimit, a=period, b=WwStatisticTop10Type.Operator, c=operator, d=priority)
                check_list.append(operator_key)
            if country:
                country_key = "{a}{delimit}{b}{delimit}{c}{delimit}{d}".format(
                    delimit=MdMeta.Delimit, a=period, b=WwStatisticTop10Type.Country, c=country, d=priority)
                check_list.append(country_key)

            for eachcheck in check_list:
                result[eachcheck] = result.get(eachcheck, 0) + 1
        return result

    def transfer_data_for_wwsta_top10(self, wwsta_top10_raw):
        all_data = []
        for eachdict in wwsta_top10_raw:
            cr_count = wwsta_top10_raw[eachdict]
            tmp_result = self.get_each_wwsta_top10_data(eachdict, cr_count)
            all_data.append(tmp_result)
        return all_data

    def get_each_wwsta_top10_data(self, data, cr_count):
        tmp_result = data.split(MdMeta.Delimit)
        period = tmp_result[0]
        t_type = tmp_result[1]
        t_value = tmp_result[2]
        priority = tmp_result[3]

        format_data = {
            WwStatisticTop10.DbFieldMap.PERIOD: period,
            WwStatisticTop10.DbFieldMap.TYPE: t_type,
            WwStatisticTop10.DbFieldMap.TYPE_VALUE: t_value,
            WwStatisticTop10.DbFieldMap.PRIORITY: priority,
            WwStatisticTop10.DbFieldMap.CR_COUNT: cr_count
        }
        return format_data

    @transaction.atomic
    def create_all_report_in_db(self, wwsta_top10, wwsta_map, resolved_es, open_es, op_cert, fta, ces):

        if wwsta_top10:
            self.create_wwsta_top10_report(wwsta_top10)
        if wwsta_map:
            self.create_wwsta_map_report(wwsta_map)
        if resolved_es:
            self.create_resolved_es_report(resolved_es)
        if open_es:
            self.create_open_es_report(open_es)
        if op_cert:
            self.create_op_cert_report(op_cert)
        if fta:
            self.create_fta_report(fta)
        if ces:
            self.create_ces_report(ces)

    def gen_wwstatistic_map_raw(self):
        result = {}

        open_state = [e.value for e in getattr(MdState, "Open")]
        resolved_state = [e.value for e in getattr(MdState, "Resolved")]

        for eachdict in self.cr_info:
            state = eachdict[MdCrFieldMap.STATE]
            period = eachdict[MdCrFieldMap.SUBMIT_DATE].year
            country = eachdict[MdCrFieldMap.WW_COUNTRY]
            operator = eachdict[MdCrFieldMap.WW_OPERATOR]
            cr_class = eachdict[MdCrFieldMap.CR_CLASS]
            resolution = eachdict[MdCrFieldMap.RESOLUTION]
            md_class = self.sync_helper.get_md_class(cr_class, resolution)
            priority = eachdict[MdCrFieldMap.PRIORITY]

            if country and operator and cr_class:
                if state in open_state:
                    state = MdState.Open.__name__
                elif state in resolved_state:
                    state = MdState.Resolved.__name__

                combo_key = "{state}{delimit}{period}{delimit}{country}{delimit}{op}{delimit}{md_class}".format(
                    delimit=MdMeta.Delimit, state=state, period=period, country=country, op=operator, md_class=md_class)

                urgent_cr_cnt = 0
                if priority == CrPriority.Urgent:
                    urgent_cr_cnt = 1

                new = {WwStaMap.DbFieldMap.CR_COUNT: 1,
                       WwStaMap.DbFieldMap.URGENT_COUNT: urgent_cr_cnt}

                ori = result.get(combo_key,
                                 {WwStaMap.DbFieldMap.CR_COUNT: 0,
                                  WwStaMap.DbFieldMap.URGENT_COUNT: 0})

                result[combo_key] = dict(Counter(new) + Counter(ori))
        return result

    def get_each_wwsta_map_data(self, data, cr_count, urgent_cr_count):
        tmp_result = data.split(MdMeta.Delimit)
        state = tmp_result[0]
        period = tmp_result[1]
        country = tmp_result[2]
        operator = tmp_result[3]
        md_class = tmp_result[4]

        format_data = {
            WwStaMap.DbFieldMap.STATE: state,
            WwStaMap.DbFieldMap.PERIOD: period,
            WwStaMap.DbFieldMap.COUNTRY: country,
            WwStaMap.DbFieldMap.OPERATOR: operator,
            WwStaMap.DbFieldMap.MD_CLASS: md_class,
            WwStaMap.DbFieldMap.CR_COUNT: cr_count,
            WwStaMap.DbFieldMap.URGENT_COUNT: urgent_cr_count
        }
        return format_data

    def transfer_data_for_wwsta_map(self, wwsta_map_raw):
        all_data = []
        for eachdict in wwsta_map_raw:
            cr_count = wwsta_map_raw[eachdict][WwStaMap.DbFieldMap.CR_COUNT]
            urgent_cr_count = wwsta_map_raw[eachdict].get(
                WwStaMap.DbFieldMap.URGENT_COUNT, 0)  # maybe no key if there's no urgent
            tmp_result = self.get_each_wwsta_map_data(
                eachdict, cr_count, urgent_cr_count)
            all_data.append(tmp_result)
        return all_data

    def gen_resolved_eservices_raw(self):
        result = {}
        state_condition = [e.value for e in getattr(MdState, "Resolved")]
        for eachdict in self.cr_info:
            state = eachdict[MdCrFieldMap.STATE]

            if state not in state_condition:
                continue

            assignee = eachdict[MdCrFieldMap.ASSIGNEE]
            customer = eachdict[MdCrFieldMap.CUSTOMER]
            site = self.get_user_site(assignee)
            resolve_date = eachdict[MdCrFieldMap.RESOLVE_DATE]
            (year_period, week) = DateHelper.calculate_mtk_week(resolve_date)
            month_period = "{}-{}".format(year_period,
                                          "%02d" % resolve_date.month)
            week_period = "{}.w{}".format(year_period, "%02d" % week)
            priority = eachdict[MdCrFieldMap.PRIORITY]
            resolve_time = eachdict[MdCrFieldMap.RESOLVE_TIME]
            check_list = []
            day_count = DateHelper.get_days_from_specific_date(resolve_date)

            if site:
                year_combo_key = "{a}{delimit}{b}{delimit}{c}{delimit}{d}{delimit}{e}".format(
                    delimit=MdMeta.Delimit, a=ResolvedEs.Period.YEAR, b=site, c=customer, d=year_period, e=priority)
                check_list.append(year_combo_key)
                if 0 <= day_count <= 84:
                    week_combo_key = "{a}{delimit}{b}{delimit}{c}{delimit}{d}{delimit}{e}".format(
                        delimit=MdMeta.Delimit, a=ResolvedEs.Period.WEEK, b=site, c=customer, d=week_period, e=priority)
                    check_list.append(week_combo_key)
                if 0 <= day_count <= 365:
                    month_combo_key = "{a}{delimit}{b}{delimit}{c}{delimit}{d}{delimit}{e}".format(
                        delimit=MdMeta.Delimit, a=ResolvedEs.Period.MONTH, b=site, c=customer, d=month_period, e=priority)
                    check_list.append(month_combo_key)
            else:
                self.logger.info("no matching site for %s", assignee)
            for eachcheck in check_list:
                new = {"cr_count": 1, "time_count": resolve_time}
                ori = result.get(eachcheck, {"cr_count": 0, "time_count": 0})
                result[eachcheck] = dict(Counter(new) + Counter(ori))
        return result

    def transfer_data_for_resolved_eservices(self, resolved_es_raw):
        all_data = []
        for eachdict in resolved_es_raw:
            details = resolved_es_raw[eachdict]
            tmp_result = self.get_each_resolved_eservices_data(
                eachdict, details)
            all_data.append(tmp_result)
        return all_data

    def get_each_resolved_eservices_data(self, data, details):
        tmp_result = data.split(MdMeta.Delimit)
        period_type = tmp_result[0]
        site = tmp_result[1]
        customer = tmp_result[2]
        period = tmp_result[3]
        priority = tmp_result[4]

        format_data = {
            ResolvedEs.DbFieldMap.TYPE: period_type,
            ResolvedEs.DbFieldMap.SITE: site,
            ResolvedEs.DbFieldMap.CUSTOMER: customer,
            ResolvedEs.DbFieldMap.PERIOD: period,
            ResolvedEs.DbFieldMap.PRIORITY: priority,
            ResolvedEs.DbFieldMap.CR_COUNT: details.get("cr_count", 0),
            ResolvedEs.DbFieldMap.RESOLVE_TIME_COUNT: details.get(
                "time_count", 0)
        }
        return format_data

    def gen_open_eservices_raw(self):
        result = {}
        state_condition = [e.value for e in getattr(MdState, "Open")]
        for eachdict in self.cr_info:
            state = eachdict[MdCrFieldMap.STATE]

            if state not in state_condition:
                continue

            assignee = eachdict[MdCrFieldMap.ASSIGNEE]
            customer = eachdict[MdCrFieldMap.CUSTOMER]
            submit_date = eachdict[MdCrFieldMap.SUBMIT_DATE]
            priority = eachdict[MdCrFieldMap.PRIORITY]
            site = self.get_user_site(assignee)

            day_count = DateHelper.get_days_from_specific_date(submit_date)
            stay_submitted = self.get_stay_submitted_define(day_count)

            if site:
                combo_key = "{site}{delimit}{cus}{delimit}{stay}{delimit}{priority}".format(
                    delimit=MdMeta.Delimit, site=site, cus=customer, stay=stay_submitted, priority=priority)
                result[combo_key] = result.get(combo_key, 0) + 1
        return result

    def get_each_open_eservices_data(self, data, cr_count):
        tmp_result = data.split(MdMeta.Delimit)
        site = tmp_result[0]
        customer = tmp_result[1]
        stay_submitted = tmp_result[2]
        priority = tmp_result[3]

        format_data = {
            OpenEs.DbFieldMap.SITE: site,
            OpenEs.DbFieldMap.CUSTOMER: customer,
            OpenEs.DbFieldMap.STAY: stay_submitted,
            OpenEs.DbFieldMap.PRIORITY: priority,
            OpenEs.DbFieldMap.CR_COUNT: cr_count,
        }
        return format_data

    def transfer_data_for_open_eservices(self, open_es_raw):
        all_data = []
        for eachdict in open_es_raw:
            cr_count = open_es_raw[eachdict]
            tmp_result = self.get_each_open_eservices_data(eachdict, cr_count)
            all_data.append(tmp_result)
        return all_data

    def get_stay_submitted_define(self, days):
        result = None
        if days > 60:
            result = ">2Month"
        else:
            if days > 27:
                result = "1-2Month"
            else:
                if days > 13:
                    result = "2W-4W"
                else:
                    if days > 6:
                        result = "1W-2W"
                    else:
                        result = "<1W"
        return result

    def create_open_es_report(self, open_es):
        self.logger.info("create report for open_eservices")
        create_open_es_list = list()
        for eachrow in open_es:
            site = eachrow[OpenEs.DbFieldMap.SITE]
            customer = eachrow[OpenEs.DbFieldMap.CUSTOMER]
            stay_submitted = eachrow[OpenEs.DbFieldMap.STAY]
            priority = eachrow[OpenEs.DbFieldMap.PRIORITY]

            t_id = DbTableHelper.get_open_es_id(
                MdMeta.ActivityId, self.sync_job_id, site, customer, stay_submitted, priority)

            eachrow.update({OpenEs.DbFieldMap.ID: t_id,
                            OpenEs.DbFieldMap.SYNC_ID: self.sync_job_id,
                            OpenEs.DbFieldMap.ACT_ID: MdMeta.ActivityId
                            })
            create_open_es_list.append(OpenEservices(**eachrow))

        # note: check for real data to decide whether to adopt page
        # insert, ex. 1000/per commit
        self.logger.info("start bulk open_eservices")
        OpenEservices.objects.bulk_create(
            create_open_es_list, batch_size=REPORT_BULK_BATCH_SIZE)
        self.logger.info("end bulk open_eservices")

    def gen_ces_raw(self):
        result = {}
        state_condition = [e.value for e in getattr(MdState, "Open")]

        for eachdict in self.cr_info:
            country = eachdict[MdCrFieldMap.COUNTRY] if eachdict[MdCrFieldMap.COUNTRY] else ""
            operator = eachdict[MdCrFieldMap.OPERATOR] if eachdict[MdCrFieldMap.OPERATOR] else ""
            priority = eachdict[MdCrFieldMap.PRIORITY]
            state = eachdict[MdCrFieldMap.STATE]

            if not(state in state_condition):
                continue

            if country or operator:
                combo_key = "{country}{delimit}{operator}{delimit}{priority}".format(
                    delimit=MdMeta.Delimit, country=country, operator=operator, priority=priority)
                result[combo_key] = result.get(combo_key, 0) + 1
        return result

    def get_each_ces_data(self, data, cr_count):
        tmp_result = data.split(MdMeta.Delimit)
        country = tmp_result[0]
        operator = tmp_result[1]
        priority = tmp_result[2]

        format_data = {
            Ces.DbFieldMap.COUNTRY: country,
            Ces.DbFieldMap.OPERATOR: operator,
            Ces.DbFieldMap.PRIORITY: priority,
            Ces.DbFieldMap.CR_COUNT: cr_count,
        }
        return format_data

    def transfer_data_for_ces(self, ces_country_raw):
        all_data = []
        for eachdict in ces_country_raw:
            cr_count = ces_country_raw[eachdict]
            tmp_result = self.get_each_ces_data(eachdict, cr_count)
            all_data.append(tmp_result)
        return all_data

    def create_ces_report(self, ces):
        self.logger.info("create report for CES")
        create_ces_list = list()
        for eachrow in ces:
            country = eachrow[Ces.DbFieldMap.COUNTRY]
            operator = eachrow[Ces.DbFieldMap.OPERATOR]
            priority = eachrow[Ces.DbFieldMap.PRIORITY]

            t_id = DbTableHelper.get_ces_specific_id(
                MdMeta.ActivityId, self.sync_job_id, country, operator, priority)

            eachrow.update({Ces.DbFieldMap.ID: t_id,
                            Ces.DbFieldMap.SYNC_ID: self.sync_job_id,
                            Ces.DbFieldMap.ACT_ID: MdMeta.ActivityId
                            })
            create_ces_list.append(CesSpecific(**eachrow))

        # note: check for real data to decide whether to adopt page
        # insert, ex. 1000/per commit
        self.logger.info("start bulk CES")
        CesSpecific.objects.bulk_create(
            create_ces_list, batch_size=REPORT_BULK_BATCH_SIZE)
        self.logger.info("end bulk CES")

    def get_hw_prj_info_in_mytodo(self):
        result = []
        queryset = CrmHwProject.objects.filter(is_active=1)

        for eachrow in queryset:
            tmp_result = {
                CrmHwPrj.DbFieldMap.ID: eachrow.id,
                CrmHwPrj.DbFieldMap.HW_PRJ_ID: eachrow.hw_project_id,
                CrmHwPrj.DbFieldMap.HW_TYPE: eachrow.hw_type,
                CrmHwPrj.DbFieldMap.OPERATOR: eachrow.operator,
                CrmHwPrj.DbFieldMap.IS_COMPLETED: eachrow.completed,
                CrmHwPrj.DbFieldMap.PLATFORM: eachrow.platform,
                CrmHwPrj.DbFieldMap.COMPANY: eachrow.company,
                CrmHwPrj.DbFieldMap.START_DATE: eachrow.start_date,
                CrmHwPrj.DbFieldMap.END_DATE: eachrow.end_date
            }
            result.append(tmp_result)
        return result

    def get_period_week(self, is_completed, start_date, end_date):
        '''
        Two types by is_completed, take not 1 as all ongoing project
        1: Completed, use end_date as period year/week
        0: Ongoing, use start_date as period year/week
        return is string, not number
        '''
        period_year = None
        period_week = None

        if is_completed == "1":
            if end_date:
                (period_year, period_week) = DateHelper.calculate_mtk_week(end_date)
        else:
            if start_date:
                (period_year, period_week) = DateHelper.calculate_mtk_week(start_date)
        if period_year and period_week:
            period_year = "{}".format(period_year)
            period_week = "W{}.{}".format(
                str(period_year)[2:], "%02d" % period_week)
        return (period_year, period_week)

    def gen_prj_status_raw(self, hw_type):
        result = {}
        for eachdict in self.hw_prj_info:
            p_hw_type = eachdict[CrmHwPrj.DbFieldMap.HW_TYPE].lower()

            if hw_type.lower() != p_hw_type:
                continue

            hw_prj_id = eachdict[CrmHwPrj.DbFieldMap.HW_PRJ_ID]
            operator = eachdict[CrmHwPrj.DbFieldMap.OPERATOR].upper()
            is_completed = eachdict[CrmHwPrj.DbFieldMap.IS_COMPLETED]
            platform = eachdict[CrmHwPrj.DbFieldMap.PLATFORM]
            company = eachdict[CrmHwPrj.DbFieldMap.COMPANY]
            start_date = eachdict[CrmHwPrj.DbFieldMap.START_DATE]
            end_date = eachdict[CrmHwPrj.DbFieldMap.END_DATE]
            (period_year, period_week) = self.get_period_week(
                is_completed, start_date, end_date)
            area = self.op_area_info.get(operator, None)

            if is_completed and platform and company and period_week and start_date:
                combo_key = self.get_combo_key_by_hw_type(
                    hw_type, operator, is_completed, platform, company, period_week, period_year, area)

                if combo_key:
                    prj_status = StatusHelper.get_prj_status(
                        period_year, period_week[4:])

                    if prj_status:
                        will_kickoff_count = 0
                        if DateHelper.is_will_kickoff_prj_in_one_mon(start_date):
                            will_kickoff_count = 1

                        cr_count = self.get_urgent_cr_count_by_hw_prj(
                            hw_prj_id, operator)

                        new = {
                            "prj_count": 1,
                            "will_kickoff_count": will_kickoff_count,
                            "u_cr_count": cr_count
                        }

                        ori = result.get(
                            combo_key, {"prj_count": 0, "will_kickoff_count": 0, "u_cr_count": 0})
                        result[combo_key] = dict(Counter(new) + Counter(ori))
                    else:
                        self.logger.info(
                            "no valid prj status or prj start date over 4 weeks, skip")
            else:
                # if data is empty or null, skip
                continue
        return result

    def get_combo_key_by_hw_type(self, hw_type, operator, is_completed, platform, company, period_week, period_year, area):
        combo_key = None
        if hw_type == MdHwPrjType.FTA:
            combo_key = "{completed}{delimit}{platform}{delimit}{company}{delimit}{period_week}{delimit}{period_year}".format(
                delimit=MdMeta.Delimit, completed=is_completed, platform=platform, company=company, period_week=period_week, period_year=period_year)
        elif hw_type == MdHwPrjType.Operator:
            if operator and area:
                combo_key = "{operator}{delimit}{completed}{delimit}{platform}{delimit}{company}{delimit}{period_week}{delimit}{period_year}{delimit}{area}".format(
                    delimit=MdMeta.Delimit, operator=operator, completed=is_completed, platform=platform, company=company, period_week=period_week, period_year=period_year, area=area)
        return combo_key

    def get_urgent_cr_count_by_hw_prj(self, hw_prj_id, operator):
        state_condition = [e.value for e in getattr(MdState, "Open")]
        queryset = Cr.objects.filter(hw_project_id=hw_prj_id, priority=CrPriority.Urgent,
                                     state__in=state_condition, is_active=1, md_info_op_name__iexact=operator)
        result_count = 0

        for eachrow in queryset:
            cr_id = eachrow.cr_id
            check_result = self.query_helper.check_cr_in_activity(
                cr_id, MdMeta.ActivityId)
            if check_result:
                result_count += 1
        return result_count

    def get_each_op_cert_data(self, data, details):
        tmp_result = data.split(MdMeta.Delimit)
        operator = tmp_result[0]
        completed = tmp_result[1]
        platform = tmp_result[2]
        company = tmp_result[3]
        period_week = tmp_result[4]
        period_year = tmp_result[5]
        area = tmp_result[6]

        format_data = {
            OpCert.DbFieldMap.OPERATOR: operator,
            OpCert.DbFieldMap.AREA: area,
            OpCert.DbFieldMap.IS_COMPLETED: completed,
            OpCert.DbFieldMap.PLATFORM: platform,
            OpCert.DbFieldMap.COMPANY: company,
            OpCert.DbFieldMap.PERIOD_WEEK: period_week,
            OpCert.DbFieldMap.PERIOD_YEAR: period_year,
            OpCert.DbFieldMap.PROJECT_COUNT: details.get("prj_count", 0),
            OpCert.DbFieldMap.WILL_KICKOFF_PROJECT_COUNT: details.get("will_kickoff_count", 0),
            OpCert.DbFieldMap.URGENT_CR_COUNT: details.get("u_cr_count", 0)
        }
        return format_data

    def transfer_op_data_for_prj_status(self, op_cert_raw):
        all_data = []
        for eachdict in op_cert_raw:
            details = op_cert_raw[eachdict]
            tmp_result = self.get_each_op_cert_data(
                eachdict, details)
            all_data.append(tmp_result)
        return all_data

    def transfer_fta_data_for_prj_status(self, fta_raw):
        all_data = []
        for eachdict in fta_raw:
            details = fta_raw[eachdict]
            tmp_result = self.get_each_fta_data(eachdict, details)
            all_data.append(tmp_result)
        return all_data

    def get_each_fta_data(self, data, details):
        tmp_result = data.split(MdMeta.Delimit)
        completed = tmp_result[0]
        platform = tmp_result[1]
        company = tmp_result[2]
        period_week = tmp_result[3]
        period_year = tmp_result[4]

        format_data = {
            FTA.DbFieldMap.IS_COMPLETED: completed,
            FTA.DbFieldMap.PLATFORM: platform,
            FTA.DbFieldMap.COMPANY: company,
            FTA.DbFieldMap.PERIOD_WEEK: period_week,
            FTA.DbFieldMap.PERIOD_YEAR: period_year,
            FTA.DbFieldMap.PROJECT_COUNT: details.get("prj_count", 0),
            FTA.DbFieldMap.WILL_KICKOFF_PROJECT_COUNT: details.get("will_kickoff_count", 0),
            FTA.DbFieldMap.URGENT_CR_COUNT: details.get("u_cr_count", 0)
        }
        return format_data

    def create_op_cert_report(self, op_cert):
        self.logger.info("create report for Operator Certification")
        create_op_cert_list = list()
        for eachrow in op_cert:
            operator = eachrow[OpCert.DbFieldMap.OPERATOR]
            is_completed = eachrow[OpCert.DbFieldMap.IS_COMPLETED]
            platform = eachrow[OpCert.DbFieldMap.PLATFORM]
            company = eachrow[OpCert.DbFieldMap.COMPANY]
            period_week = eachrow[OpCert.DbFieldMap.PERIOD_WEEK]

            t_id = DbTableHelper.get_operator_cert_id(
                MdMeta.ActivityId, self.sync_job_id, operator, is_completed, platform, company, period_week)

            eachrow.update({OpCert.DbFieldMap.ID: t_id,
                            OpCert.DbFieldMap.SYNC_ID: self.sync_job_id,
                            OpCert.DbFieldMap.ACT_ID: MdMeta.ActivityId
                            })
            create_op_cert_list.append(OperatorCertification(**eachrow))

        # note: check for real data to decide whether to adopt page
        # insert, ex. 1000/per commit
        self.logger.info("start bulk Operator Certification")
        OperatorCertification.objects.bulk_create(
            create_op_cert_list, batch_size=REPORT_BULK_BATCH_SIZE)
        self.logger.info("end bulk Operator Certification")

    def create_fta_report(self, fta):
        self.logger.info("create report for FTA")
        create_fta_list = list()
        for eachrow in fta:
            is_completed = eachrow[FTA.DbFieldMap.IS_COMPLETED]
            platform = eachrow[FTA.DbFieldMap.PLATFORM]
            company = eachrow[FTA.DbFieldMap.COMPANY]
            period_week = eachrow[FTA.DbFieldMap.PERIOD_WEEK]

            t_id = DbTableHelper.get_fta_id(
                MdMeta.ActivityId, self.sync_job_id, is_completed, platform, company, period_week)

            eachrow.update({FTA.DbFieldMap.ID: t_id,
                            FTA.DbFieldMap.SYNC_ID: self.sync_job_id,
                            FTA.DbFieldMap.ACT_ID: MdMeta.ActivityId
                            })
            create_fta_list.append(Fta(**eachrow))

        # note: check for real data to decide whether to adopt page
        # insert, ex. 1000/per commit
        self.logger.info("start bulk FTA")
        Fta.objects.bulk_create(
            create_fta_list, batch_size=REPORT_BULK_BATCH_SIZE)
        self.logger.info("end bulk FTA")

    def create_wwsta_top10_report(self, wwsta_top10):
        self.logger.info("create report for wwsta_top10")
        create_wwsta_top10_list = list()
        for eachrow in wwsta_top10:
            period = eachrow.get(WwStatisticTop10.DbFieldMap.PERIOD, None)
            figure_type = eachrow.get(WwStatisticTop10.DbFieldMap.TYPE, None)
            type_value = eachrow.get(
                WwStatisticTop10.DbFieldMap.TYPE_VALUE, None)
            priority = eachrow.get(WwStatisticTop10.DbFieldMap.PRIORITY, None)

            t_id = DbTableHelper.get_wwsta_top10_id(
                MdMeta.ActivityId, self.sync_job_id, period, figure_type, type_value, priority)

            eachrow.update({WwStatisticTop10.DbFieldMap.ID: t_id,
                            WwStatisticTop10.DbFieldMap.SYNC_ID: self.sync_job_id,
                            WwStatisticTop10.DbFieldMap.ACT_ID: MdMeta.ActivityId
                            })
            create_wwsta_top10_list.append(Wwstatistictop10(**eachrow))

        # note: check for real data to decide whether to adopt page
        # insert, ex. 1000/per commit
        self.logger.info("start bulk create_wwsta_top10_list")
        Wwstatistictop10.objects.bulk_create(
            create_wwsta_top10_list, batch_size=REPORT_BULK_BATCH_SIZE)
        self.logger.info("end bulk create_wwsta_top10_list")

    def create_wwsta_map_report(self, wwsta_map):
        self.logger.info("create report for wwsta_map")
        create_wwsta_map_list = list()
        for eachrow in wwsta_map:
            state = eachrow.get(WwStaMap.DbFieldMap.STATE, None)
            period = eachrow.get(WwStaMap.DbFieldMap.PERIOD, None)
            country = eachrow.get(WwStaMap.DbFieldMap.COUNTRY, None)
            operator = eachrow.get(WwStaMap.DbFieldMap.OPERATOR, None)
            md_class = eachrow.get(WwStaMap.DbFieldMap.MD_CLASS, None)

            t_id = DbTableHelper.get_wwsta_map_id(
                MdMeta.ActivityId, self.sync_job_id, state, period, country, operator, md_class)

            eachrow.update({WwStaMap.DbFieldMap.ID: t_id,
                            WwStaMap.DbFieldMap.SYNC_ID: self.sync_job_id,
                            WwStaMap.DbFieldMap.ACT_ID: MdMeta.ActivityId
                            })
            create_wwsta_map_list.append(Wwstatisticmap(**eachrow))

        # note: check for real data to decide whether to adopt page
        # insert, ex. 1000/per commit
        self.logger.info("start bulk create_wwsta_map_report")
        Wwstatisticmap.objects.bulk_create(
            create_wwsta_map_list, batch_size=REPORT_BULK_BATCH_SIZE)
        self.logger.info("end bulk create_wwsta_map_report")

    def create_resolved_es_report(self, resolved_es):
        self.logger.info("create report for resolved_eservices")
        create_resolved_es_list = list()
        for eachrow in resolved_es:
            period_type = eachrow.get(ResolvedEs.DbFieldMap.TYPE, None)
            site = eachrow.get(ResolvedEs.DbFieldMap.SITE, None)
            customer = eachrow.get(ResolvedEs.DbFieldMap.CUSTOMER, None)
            period = eachrow.get(ResolvedEs.DbFieldMap.PERIOD, None)
            priority = eachrow.get(ResolvedEs.DbFieldMap.PRIORITY, None)

            t_id = DbTableHelper.get_resolved_es_id(MdMeta.ActivityId, self.sync_job_id,
                                                    period_type, site, customer, period, priority)

            eachrow.update({ResolvedEs.DbFieldMap.ID: t_id,
                            ResolvedEs.DbFieldMap.SYNC_ID: self.sync_job_id,
                            ResolvedEs.DbFieldMap.ACT_ID: MdMeta.ActivityId
                            })
            create_resolved_es_list.append(ResolvedEserives(**eachrow))

        # note: check for real data to decide whether to adopt page
        # insert, ex. 1000/per commit
        self.logger.info("start bulk resolved_eservices")
        ResolvedEserives.objects.bulk_create(
            create_resolved_es_list, batch_size=REPORT_BULK_BATCH_SIZE)
        self.logger.info("end bulk resolved_eservices")

    def get_user_site(self, user):
        check_site = self.user_site.get(user, None)
        site = None

        if check_site:
            site = check_site["site"]
        else:
            self.logger.warning("assignee %s didn't have site, skip", user)
        return site
