import logging

from cr_review_sys.const import PriorityAbbr
from cr_review_sys.models import OpenEservices
from md_analysis.const import LOG_TRACE_LVL
from my_to_do.util import Singleton


class OpenEservicesService(object, metaclass=Singleton):
    '''
    Open Eservices API, return still open eService CR for top 10 customer by site
    '''

    def __init__(self):
        '''constructor
        '''
        self.logger = logging.getLogger('aplogger')

    def get_open_eservices_all_data(self, sync_job_id):

        self.logger.info(
            "begin to get_open_eservices_all_data with syc_job_id: %s", sync_job_id)

        queryset = OpenEservices.objects.filter(
            sync_job_id=sync_job_id)

        data = {}

        self.logger.info(
            "begin to handle get_open_eservices_all_data queryset")
        for eachrow in queryset:
            t_assignee_site = eachrow.assignee_site
            t_customer = eachrow.customer_company
            t_stay_submitted = eachrow.stay_submitted
            t_priority = getattr(PriorityAbbr, eachrow.priority[2:])
            t_cr_cnt = eachrow.cr_count

            if t_assignee_site in data:
                if t_customer in data.get(t_assignee_site, {}):
                    self.logger.log(LOG_TRACE_LVL, "exist customer: %s")
                    if t_stay_submitted in data.get(t_assignee_site, {}).get(t_customer, {}):
                        self.logger.log(
                            LOG_TRACE_LVL, "exist stay_submitted: %s")
                        self.logger.log(LOG_TRACE_LVL, "add priority")
                        temp = {
                            t_priority: t_cr_cnt
                        }
                        data[t_assignee_site][t_customer][t_stay_submitted].update(
                            temp)
                    else:
                        self.logger.log(LOG_TRACE_LVL,
                                        "period stay_submitted, add stay_submitted")
                        temp = {
                            t_stay_submitted: {
                                t_priority: t_cr_cnt
                            }
                        }
                        data[t_assignee_site][t_customer].update(temp)
                else:
                    self.logger.log(
                        LOG_TRACE_LVL, "customer non-exist, add customer")
                    temp = {
                        t_customer: {
                            t_stay_submitted: {
                                t_priority: t_cr_cnt
                            }
                        }
                    }
                    data[t_assignee_site].update(temp)
            else:
                self.logger.log(
                    LOG_TRACE_LVL, "non-exist site: %s", t_assignee_site)
                final = {
                    t_assignee_site: {
                        t_customer: {
                            t_stay_submitted: {
                                t_priority: t_cr_cnt
                            }
                        }
                    }
                }
                data.update(final)
        self.logger.info("end to handle get_open_eservices_all_data queryset")
        self.logger.info(
            "end to get_open_eservices_all_data with syc_job_id: %s", sync_job_id)
        self.logger.debug("data len %s", len(data))
        return data
