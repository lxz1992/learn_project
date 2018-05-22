import logging

from cr_review_sys.const import PriorityAbbr
from cr_review_sys.models import CesSpecific, OpGroup
from md_analysis.const import MdMeta, LOG_TRACE_LVL
from md_analysis.errors import DbDataNotFound, ParseResultNotFound,\
    MeaTop10NotFound
from my_to_do.util import Singleton


class CesSpecificService(object, metaclass=Singleton):
    '''
    CES Specific Related API
    1. CES Specific by Country
    2. CES Specific by Group 
    (Group by Operator, ex. Orange Group, Vodafone Group, 
    DT - Deutsche Telekom  Group, SFR France, Telefonica Group, etc.)
    '''

    def __init__(self):
        '''constructor
        '''
        self.logger = logging.getLogger('aplogger')
        self.op_group_mapping = self.get_op_group()
        self.mea_top10 = self.get_mea_top10()

    def get_op_group(self):
        result = {}

        queryset = OpGroup.objects.filter(type="Operator")

        for eachrow in queryset:
            t_op = eachrow.value
            t_group = eachrow.group_name

            result.update({t_op: t_group})
        return result

    def get_by_country_all_data(self, sync_job_id):

        queryset = CesSpecific.objects.filter(sync_job_id=sync_job_id)

        data = {}

        # by user's request, initial mea top10 data for showing abscissa
        for each_country in self.mea_top10:
            data.update({each_country: {PriorityAbbr.High: 0}})

        for eachrow in queryset:
            t_country = eachrow.country.upper()
            t_priority = getattr(PriorityAbbr, eachrow.priority[2:])
            t_cr_cnt = eachrow.cr_count

            if t_country not in self.mea_top10:
                continue

            if t_country in data:
                if t_priority in data.get(t_country, {}):
                    self.logger.debug(
                        "exist priority: %s, add cr_count", t_priority)

                    ori_cr_cnt = data.get(t_country, {}).get(t_priority)
                    new_cr_cnt = ori_cr_cnt + t_cr_cnt
                    self.logger.debug(
                        "original cr count: %s, add new cr count: %s, total %s", ori_cr_cnt, t_cr_cnt, new_cr_cnt)
                    data[t_country][t_priority] = new_cr_cnt
                else:
                    self.logger.debug("priority non-exist, add priority")
                    temp = {
                        t_priority: t_cr_cnt
                    }
                    data[t_country].update(temp)
            else:
                self.logger.debug("non-exist: %s", t_country)
                final = {
                    t_country: {
                        t_priority: t_cr_cnt
                    }
                }
                data.update(final)
        self.logger.debug("data len %s", len(data))
        return data

    def get_by_group_all_data(self, sync_job_id):

        queryset = CesSpecific.objects.filter(sync_job_id=sync_job_id)

        data = {}

        if not queryset:
            raise DbDataNotFound()  # for db result check

        for eachrow in queryset:
            # mapping operator to operator by group
            t_operator = self.op_group_mapping.get(eachrow.operator)
            if t_operator == None:
                t_operator = "Others"
            t_priority = getattr(PriorityAbbr, eachrow.priority[2:])
            t_cr_cnt = eachrow.cr_count

            if t_operator in data:
                if t_priority in data.get(t_operator, {}):
                    self.logger.log(LOG_TRACE_LVL,
                                    "exist priority: %s, add cr_count", t_priority)

                    ori_cr_cnt = data.get(t_operator, {}).get(t_priority)
                    new_cr_cnt = ori_cr_cnt + t_cr_cnt
                    self.logger.log(LOG_TRACE_LVL,
                                    "original cr count: %s, add new cr count: %s, total %s", ori_cr_cnt, t_cr_cnt, new_cr_cnt)
                    data[t_operator][t_priority] = new_cr_cnt
                else:
                    self.logger.log(
                        LOG_TRACE_LVL, "priority non-exist, add priority")
                    temp = {
                        t_priority: t_cr_cnt
                    }
                    data[t_operator].update(temp)
            else:
                self.logger.log(LOG_TRACE_LVL, "non-exist: %s", t_operator)
                final = {
                    t_operator: {
                        t_priority: t_cr_cnt
                    }
                }
                data.update(final)
        self.logger.debug("data len %s", len(data))
        if data == {}:
            raise ParseResultNotFound()  # for business logic check
        return data

    def get_mea_top10(self):
        result = []
        queryset = OpGroup.objects.filter(
            group_name=MdMeta.MEATop10, type=MdMeta.OpCountryType)

        for eachrow in queryset:
            result.append(eachrow.value.upper())
        return result
