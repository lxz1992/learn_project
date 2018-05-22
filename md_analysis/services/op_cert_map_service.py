import logging

from cr_review_sys.models import OperatorCertification
from md_analysis.const import LOG_TRACE_LVL, MdPrjStatus
from md_analysis.errors import DbDataNotFound, ParseResultNotFound
from md_analysis.util.status_helper import StatusHelper
from my_to_do.util import Singleton
from my_to_do.util.compute_helper import ComputeHelper


class OpCertMapService(object, metaclass=Singleton):
    '''
    Operator Certification MAP API
    '''

    def __init__(self):
        '''constructor
        '''
        self.logger = logging.getLogger('aplogger')

    def sum_count(self, ori, new):
        result = ori + new
        return result

    def get_op_cert_map_all_data(self, sync_job_id):

        self.logger.info(
            "begin to get_op_cert_map_all_data with syc_job_id: %s", sync_job_id)

        queryset = OperatorCertification.objects.filter(
            sync_job_id=sync_job_id, is_completed=0)

        data = {}

        if not queryset:
            self.logger.info(
                "end with exception to get_op_cert_map_all_data with syc_job_id: %s", sync_job_id)
            raise DbDataNotFound()  # for db result check

        self.logger.info(
            "begin to handle get_op_cert_map_all_data queryset")
        for eachrow in queryset:
            t_id = eachrow.id
            t_operator = eachrow.operator
            t_area = eachrow.area
            t_prj_cnt = ComputeHelper.update_none_or_empty_to_zero(
                eachrow.project_count)
            t_urgent = ComputeHelper.update_none_or_empty_to_zero(
                eachrow.urgent_cr_count)
            t_year = eachrow.period_year
            t_week = eachrow.period_week[4:]
            prj_status = StatusHelper.get_prj_status(t_year, t_week)
            self.logger.log(LOG_TRACE_LVL, "prj status is :%", prj_status)

            if not prj_status:
                self.logger.log(
                    LOG_TRACE_LVL, "skip %s invalid prj status", t_id)
                continue

            (new_ongoing, new_incoming) = self.get_prj_count_by_status(
                prj_status, t_prj_cnt)

            if new_ongoing or new_incoming:
                if t_area in data:
                    self.logger.log(LOG_TRACE_LVL, "exist area: %s", t_area)
                    if t_operator in data.get(t_area, {}):
                        self.logger.log(
                            LOG_TRACE_LVL, "exist operator: %s", t_operator)

                        ori_ongoing = int(data[t_area][t_operator]["ongoing"])
                        ori_incoming = int(
                            data[t_area][t_operator]["incoming"])
                        ori_urgent = int(data[t_area][t_operator]["urgent"])

                        new = {
                            "ongoing": ori_ongoing + new_ongoing,
                            "incoming": ori_incoming + new_incoming,
                            "urgent": ori_urgent + t_urgent
                        }
                        data[t_area][t_operator] = new
                    else:
                        self.logger.log(
                            LOG_TRACE_LVL, "non-exist operator: %s", t_operator)
                        temp = {
                            t_operator: {
                                "ongoing": new_ongoing,
                                "incoming": new_incoming,
                                "urgent": t_urgent
                            }
                        }
                        data[t_area].update(temp)
                else:
                    self.logger.log(
                        LOG_TRACE_LVL, "non-exist area: %s", t_area)
                    final = {
                        t_area: {
                            t_operator: {
                                "ongoing": new_ongoing,
                                "incoming": new_incoming,
                                "urgent": t_urgent
                            }
                        }
                    }
                    data.update(final)
            else:
                self.logger.log(
                    LOG_TRACE_LVL, "no result for new_ongoing & new_incoming")

        self.logger.info("end to handle get_op_cert_map_all_data queryset")
        self.logger.info(
            "end to get_op_cert_map_all_data with syc_job_id: %s", sync_job_id)
        self.logger.debug("data len %s", len(data))
        if data == {}:
            self.logger.info(
                "end with exception to get_op_cert_map_all_data with syc_job_id: %s", sync_job_id)
            raise ParseResultNotFound()  # for business logic check
        return data

    def get_prj_count_by_status(self, prj_status, count):
        ongoing_cnt = 0
        incoming_cnt = 0

        if prj_status == MdPrjStatus.NEW or prj_status == MdPrjStatus.ONGOING:
            ongoing_cnt = count
        elif prj_status == MdPrjStatus.INCOMING:
            incoming_cnt = count
        else:
            return (None, None)
        return(ongoing_cnt, incoming_cnt)
