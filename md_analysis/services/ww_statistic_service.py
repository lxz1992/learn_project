import logging

from cr_review_sys.const import PriorityAbbr
from cr_review_sys.models import Wwstatistictop10, Wwstatisticmap, MdMccMnc
from md_analysis.const import LOG_TRACE_LVL, WwStaMap
from md_analysis.errors import DbDataNotFound, ParseResultNotFound,\
    CountryCodeNotFount
from my_to_do.util import Singleton
from my_to_do.util.compute_helper import ComputeHelper


class WwStatisticService(object, metaclass=Singleton):
    '''
    WW Statistic Related API
    1. WW Statistic Top 10
    2. WW Statistic MAP
    '''

    def __init__(self):
        '''constructor
        '''
        self.logger = logging.getLogger('aplogger')

    def get_top10_all_data(self, sync_job_id):

        queryset = Wwstatistictop10.objects.filter(sync_job_id=sync_job_id)
        # set default key for return
        data = {"Country": {}, "Operator": {}, "Customer": {}}

        for eachrow in queryset:
            t_priority = getattr(PriorityAbbr, eachrow.priority[2:])
            t_type = eachrow.type
            t_type_value = eachrow.type_value
            t_period = eachrow.period
            t_cr_count = eachrow.cr_count

            if t_type in data:
                if t_period in data.get(t_type, {}):
                    self.logger.log(LOG_TRACE_LVL, "exist period: %s", t_type)

                    if t_type_value in data.get(t_type, {}).get(t_period, {}):
                        self.logger.log(LOG_TRACE_LVL, "t_type_value exist")
                        data[t_type][t_period][t_type_value].update(
                            {t_priority: t_cr_count})
                    else:
                        self.logger.log(
                            LOG_TRACE_LVL, "t_type_value non exist")
                        temp = {
                            t_type_value: {
                                t_priority: t_cr_count
                            }
                        }
                        data[t_type][t_period].update(temp)
                else:
                    self.logger.log(LOG_TRACE_LVL, "period non-exist")
                    temp = {
                        t_period: {
                            t_type_value: {
                                t_priority: t_cr_count
                            }
                        }
                    }
                    data[t_type].update(temp)
            else:
                self.logger.debug("non-exist: %s", t_type)
                final = {
                    t_type: {
                        t_period: {
                            t_type_value: {
                                t_priority: t_cr_count
                            }
                        }
                    }
                }
                data.update(final)
        self.logger.debug("data len %s", len(data))
        return data

    def get_map_all_data(self, sync_job_id):

        queryset = Wwstatisticmap.objects.filter(sync_job_id=sync_job_id)
        country_code = []
        country_list = []
        data = {}

        for eachrow in queryset:
            t_period = eachrow.period
            t_state = eachrow.state.lower()
            t_country = eachrow.country
            t_oper = eachrow.operator
            t_md_cls = eachrow.md_class
            t_cr_cnt = eachrow.cr_count
            t_urgent_cr_cnt = ComputeHelper.update_none_or_empty_to_zero(eachrow.urgent_cr_count)

            if t_country not in country_list:
                # add country code mapping
                try:
                    new_country_code_mapping = self.get_country_code_mapping(
                        t_country)
                    country_code.append(new_country_code_mapping)
                    country_list.append(t_country)
                except DbDataNotFound as e:
                    self.logger.warning(
                        "couldn't find country code for: %s, %s", t_country, e)

            if t_period in data:
                if t_state in data.get(t_period, {}):
                    self.logger.log(LOG_TRACE_LVL, "exist state: %s", t_state)
                    if t_country in data.get(t_period, {}).get(t_state, {}):
                        if t_oper in data.get(t_period, {}).get(t_state, {}).get(t_country, {}):
                            self.logger.log(LOG_TRACE_LVL,
                                            "non-exits md_class: %s, created", t_md_cls)
                            temp = {
                                t_md_cls: t_cr_cnt
                            }

                            data[t_period][t_state][t_country][t_oper].update(
                                temp)

                            if t_urgent_cr_cnt:
                                ori_urgent_cr_cnt = data[t_period][t_state][t_country][t_oper][WwStaMap.URGENT_CR_KEY]
                                new_urgent_cr_cnt = ori_urgent_cr_cnt + t_urgent_cr_cnt
                                data[t_period][t_state][t_country][t_oper][WwStaMap.URGENT_CR_KEY] = new_urgent_cr_cnt

                        else:
                            self.logger.log(LOG_TRACE_LVL,
                                            "non-exits operator: %s, created", t_oper)
                            temp = {
                                t_oper: {
                                    t_md_cls: t_cr_cnt,
                                    WwStaMap.URGENT_CR_KEY: t_urgent_cr_cnt
                                }
                            }
                            data[t_period][t_state][t_country].update(temp)
                    else:
                        self.logger.log(LOG_TRACE_LVL,
                                        "non-exits country: %s, created", t_country)
                        temp = {
                            t_country: {
                                t_oper: {
                                    t_md_cls: t_cr_cnt,
                                    WwStaMap.URGENT_CR_KEY: t_urgent_cr_cnt
                                }
                            }
                        }
                        data[t_period][t_state].update(temp)
                else:
                    self.logger.log(
                        LOG_TRACE_LVL, "non-exits state: %s, created", t_state)
                    temp = {
                        t_state: {
                            t_country: {
                                t_oper: {
                                    t_md_cls: t_cr_cnt,
                                    WwStaMap.URGENT_CR_KEY: t_urgent_cr_cnt
                                }
                            }
                        }
                    }
                    data[t_period].update(temp)
            else:
                self.logger.log(
                    LOG_TRACE_LVL, "non-exits period: %s, created", t_period)
                final = {
                    t_period: {
                        t_state: {
                            t_country: {
                                t_oper: {
                                    t_md_cls: t_cr_cnt,
                                    WwStaMap.URGENT_CR_KEY: t_urgent_cr_cnt
                                }
                            }
                        }
                    }
                }
                data.update(final)
        if data == {}:
            raise ParseResultNotFound()
        if country_code == []:
            raise CountryCodeNotFount()

        return (data, country_code)

    def get_country_code_mapping(self, country):
        result = {}

        queryset = MdMccMnc.objects.filter(country=country)
        if not queryset:
            raise DbDataNotFound()  # for db result check

        for eachrow in queryset:
            result = {'name': eachrow.country, 'code': eachrow.country_code}

        return result
