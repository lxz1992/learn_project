import logging

from cr_review_sys.const import PriorityAbbr
from cr_review_sys.models import ResolvedEserives
from md_analysis.const import LOG_TRACE_LVL
from my_to_do.util import Singleton


class ResolvedEservicesService(object, metaclass=Singleton):
    '''
    Resolved Eservices API, show resolved issues recent 12 weeks
    '''

    def __init__(self):
        '''constructor
        '''
        self.logger = logging.getLogger('aplogger')

    def get_resolved_eservices_all_data(self, sync_job_id):

        queryset = ResolvedEserives.objects.filter(
            sync_job_id=sync_job_id)

        data = {}

        for eachrow in queryset:
            t_assignee_site = eachrow.assignee_site
            t_customer = eachrow.customer_company
            t_period = eachrow.period
            t_priority = getattr(PriorityAbbr, eachrow.priority[2:])
            t_cr_cnt = eachrow.cr_count
            t_resolve_time = eachrow.resolve_time_count

            if t_assignee_site in data:
                if t_customer in data.get(t_assignee_site, {}):
                    self.logger.log(LOG_TRACE_LVL, "exist customer: %s", t_customer)
                    if t_period in data.get(t_assignee_site, {}).get(t_customer, {}):
                        self.logger.log(LOG_TRACE_LVL, "exist period: %s", t_period)
                        self.logger.log(LOG_TRACE_LVL, 
                            "priority non-exist, add priority")
                        temp = {
                            t_priority: {
                                "N": t_cr_cnt,
                                "RT": t_resolve_time
                            }
                        }
                        data[t_assignee_site][t_customer][t_period].update(
                            temp)
                    else:
                        self.logger.log(LOG_TRACE_LVL, "period non-exist, add period")
                        temp = {
                            t_period: {
                                t_priority: {
                                    "N": t_cr_cnt,
                                    "RT": t_resolve_time
                                }
                            }
                        }
                        data[t_assignee_site][t_customer].update(temp)
                else:
                    self.logger.log(LOG_TRACE_LVL, "customer non-exist, add customer")
                    temp = {
                        t_customer: {
                            t_period: {
                                t_priority: {
                                    "N": t_cr_cnt,
                                    "RT": t_resolve_time
                                }
                            }
                        }
                    }
                    data[t_assignee_site].update(temp)
            else:
                self.logger.debug("non-exist site: %s", t_assignee_site)
                final = {
                    t_assignee_site: {
                        t_customer: {
                            t_period: {
                                t_priority: {
                                    "N": t_cr_cnt,
                                    "RT": t_resolve_time
                                }
                            }
                        }
                    }
                }
                data.update(final)
        self.logger.debug("data len %s", len(data))
        return data
