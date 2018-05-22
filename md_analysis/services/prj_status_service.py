import datetime
import logging

from cr_review_sys.models import OperatorCertification, Fta
from md_analysis.const import LOG_TRACE_LVL, MdPrjStatus
from md_analysis.errors import DbDataNotFound, ParseResultNotFound
from md_analysis.util.status_helper import StatusHelper
from my_to_do.util import Singleton
from my_to_do.util.compute_helper import ComputeHelper
from my_to_do.util.date_helper import DateHelper


class PrjStatusService(object, metaclass=Singleton):
    '''
    Project Status Related API
    1. Get Operator Project Status
    2. Get FTA Project Status
    '''

    def __init__(self):
        '''constructor
        '''
        self.logger = logging.getLogger('aplogger')

    def sum_count(self, ori, new):
        result = ori + new
        return result

    def recalculate_dict_for_hash(self, **kwds):
        check_list = ["chip", "customer"]
        new_prj_cnt = kwds["prj_cnt"]
        new_data = kwds["ori_data"]

        self.logger.log(LOG_TRACE_LVL,
                        "start check_type_value_exist, %s", kwds)

        for member in check_list:
            check_type = kwds[member]

            if check_type in new_data[member].keys():
                self.logger.log(
                    LOG_TRACE_LVL, "[%s] exists, re-calculate sum", check_type)
                ori_value = new_data[member][check_type]
                new_data[member][check_type] = self.sum_count(
                    ori_value, new_prj_cnt)
            else:
                self.logger.log(
                    LOG_TRACE_LVL, "non exist chip %s, create", check_type)
                new_data[member].update({check_type: new_prj_cnt})

        self.logger.log(LOG_TRACE_LVL,
                        "end check_type_value_exist, %s", kwds)
        return new_data

    def handle_query_set(self, sync_job_id, queryset):

        # initial dict key for return
        data = {
            "ongoing": {},
            "new": {},
            "incoming": {},
            "year": {}
        }

        if not queryset:
            self.logger.info(
                "end with exception to handle_query_set with syc_job_id: %s", sync_job_id)
            raise DbDataNotFound()  # for db result check

        self.logger.info(
            "begin to handle calculate prj status and count, sync_job_id: %s", sync_job_id)
        for eachrow in queryset:
            t_completed = eachrow.is_completed
            t_chip = eachrow.platform
            t_customer = eachrow.company
            t_year = eachrow.period_year
            t_full_week = eachrow.period_week
            t_short_week = eachrow.period_week[4:6]
            t_prj_cnt = ComputeHelper.update_none_or_empty_to_zero(
                eachrow.project_count)
            t_will_kickoff_prj_cnt = ComputeHelper.update_none_or_empty_to_zero(
                eachrow.will_kickoff_project_count)

            if t_completed == MdPrjStatus.COMPLETED:
                self.logger.log(
                    LOG_TRACE_LVL, "handle for distribution yearly")

                if t_year in data.get(MdPrjStatus.DIS_YEARLY, {}):
                    self.logger.log(
                        LOG_TRACE_LVL, "year exist, check customer & chip")

                    year_check = {
                        "chip": t_chip,
                        "customer": t_customer,
                        "prj_cnt": t_prj_cnt,
                        "ori_data": data[MdPrjStatus.DIS_YEARLY][t_year]
                    }
                    data[MdPrjStatus.DIS_YEARLY][t_year] = self.recalculate_dict_for_hash(
                        **year_check)
                else:
                    self.logger.log(LOG_TRACE_LVL, "year non-exist, create")
                    new_year = {
                        t_year: {
                            "chip": {
                                t_chip: t_prj_cnt
                            },
                            "customer": {
                                t_customer: t_prj_cnt
                            }
                        }
                    }
                    data[MdPrjStatus.DIS_YEARLY].update(new_year)
            else:
                self.logger.log(LOG_TRACE_LVL, "handle for ongoing & new")
                prj_status = StatusHelper.get_prj_status(t_year, t_short_week)
                self.logger.log(LOG_TRACE_LVL, "prj status is %s", prj_status)

                if prj_status == MdPrjStatus.NEW or prj_status == MdPrjStatus.ONGOING:

                    if t_full_week in data.get(prj_status, {}):
                        self.logger.log(
                            LOG_TRACE_LVL, "week exist, check chip & customer")
                        new_check = {
                            "chip": t_chip,
                            "customer": t_customer,
                            "prj_cnt": t_prj_cnt,
                            "ori_data": data[prj_status][t_full_week]
                        }
                        data[prj_status][t_full_week] = self.recalculate_dict_for_hash(
                            **new_check)
                    else:
                        self.logger.log(
                            LOG_TRACE_LVL, "new week: %s", t_full_week)
                        new_data = {
                            t_full_week: {
                                "chip": {
                                    t_chip: t_prj_cnt
                                },
                                "customer": {
                                    t_customer: t_prj_cnt
                                }
                            }
                        }
                        data[prj_status].update(new_data)
                elif prj_status == MdPrjStatus.INCOMING:
                    if not t_will_kickoff_prj_cnt:
                        self.logger.log(
                            LOG_TRACE_LVL, "no incoming prj in 4 weeks")
                        continue
                    if t_full_week in data.get("incoming", {}):
                        self.logger.log(
                            LOG_TRACE_LVL, "week exist, check chip & customer")
                        incoming_check = {
                            "chip": t_chip,
                            "customer": t_customer,
                            "prj_cnt": t_will_kickoff_prj_cnt,
                            "ori_data": data[MdPrjStatus.INCOMING][t_full_week]
                        }
                        data[MdPrjStatus.INCOMING][t_full_week] = self.recalculate_dict_for_hash(
                            **incoming_check)
                    else:
                        self.logger.log(
                            LOG_TRACE_LVL, "new week: %s", t_full_week)

                        incoming_data = {
                            t_full_week: {
                                "chip": {
                                    t_chip: t_will_kickoff_prj_cnt
                                },
                                "customer": {
                                    t_customer: t_will_kickoff_prj_cnt
                                }
                            }
                        }
                        data[MdPrjStatus.INCOMING].update(incoming_data)

                else:
                    self.logger.log(
                        LOG_TRACE_LVL, "skip invalid null prj status")

        self.logger.info(
            "end to handle calculate prj status and count, sync_job_id: %s", sync_job_id)
        return data

    def get_prj_status_by_operator_all_data(self, **kwds):

        sync_job_id = kwds["sync_job_id"]
        op_name = kwds["op_name"]

        self.logger.info(
            "begin to get_prj_status_by_operator_all_data with syc_job_id: %s", sync_job_id)

        queryset = OperatorCertification.objects.filter(
            sync_job_id=sync_job_id, operator=op_name)

        data = self.handle_query_set(sync_job_id, queryset)

        if data["ongoing"] == {} and data["incoming"] == {} and data["year"] == {} and data["new"] == {}:
            self.logger.info(
                "end with exception to get_op_cert_map_all_data with syc_job_id: %s", sync_job_id)
            raise ParseResultNotFound()  # for business logic check
        return data

    def get_prj_status_for_FTA_all_data(self, **kwds):
        sync_job_id = kwds["sync_job_id"]

        self.logger.info(
            "begin to get_prj_status_for_FTA_all_data with syc_job_id: %s", sync_job_id)

        queryset = Fta.objects.filter(sync_job_id=sync_job_id)

        data = self.handle_query_set(sync_job_id, queryset)

        if data["ongoing"] == {} and data["incoming"] == {} and data["year"] == {} and data["new"] == {}:
            self.logger.info(
                "end with exception to get_prj_status_for_FTA_all_data with syc_job_id: %s", sync_job_id)
            raise ParseResultNotFound()  # for business logic check
        return data
