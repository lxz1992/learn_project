import logging
import re

from cr_review_sys.models import Cr
from md_analysis.const import MdMeta, LOG_TRACE_LVL, MdState
from md_analysis.util.query_helper import QueryHelper
from my_to_do.util import Singleton
from my_to_do.util.sync_helper import SyncHelper


class CrAnalysisByHwPrjService(object, metaclass=Singleton):
    '''
    Get Cr Analysis by Hw Project API
    '''

    def __init__(self):
        '''constructor
        '''
        self.logger = logging.getLogger('aplogger')
        self.md_dept_list = getattr(MdMeta, "Group")
        self.sync_helper = SyncHelper()
        self.query_helper = QueryHelper()

    def cal_data(self, cal_value, **data):
        #         final_data = data.get(cal_type)

        if cal_value in data.keys():
            self.logger.log(LOG_TRACE_LVL, "with %s, add count", cal_value)
            data[cal_value] += 1
        else:
            self.logger.log(
                LOG_TRACE_LVL, "without %s, create new and count", cal_value)
            data.update({cal_value: 1})

        return data

    def get_cr_analysis_by_hwprj_all_data(self, hw_prj_id, act_id, act_cr_list, operator):

        self.logger.info(
            "begin to get_cr_anaylsis_by_hwprj_all_data, hw_prj_id: %s", hw_prj_id)

        open_state_condition = [e.value for e in getattr(MdState, "Open")]

        data = {
            "state": {},
            "group": {"Modem team": 0, "Non modem team": 0},
            "all_patch": {},
            "modem_patch": {},
            "modem_open": {}
        }

        queryset = Cr.objects.filter(
            hw_project_id=hw_prj_id, md_info_op_name__iexact=operator)

        for eachrow in queryset:
            t_crid = eachrow.cr_id
            check_activity = self.query_helper.check_cr_in_activity(t_crid, activity_id=MdMeta.ActivityId)

            if not check_activity:
                continue

            if t_crid in act_cr_list:
                self.logger.log(LOG_TRACE_LVL, "append %s into result", t_crid)

                t_class = eachrow.cr_class
                t_state = eachrow.state
                t_assignee_dept = eachrow.assignee_dept
                t_resolution = eachrow.resolution

                cr_type = self.sync_helper.get_patch_cr_type(
                    t_class, t_resolution)

                md_cr_check = self.check_md_dept_or_not(t_assignee_dept)
                if t_state in open_state_condition and md_cr_check:
                    data["modem_open"] = self.cal_data(
                        t_assignee_dept, **data["modem_open"])

                if md_cr_check:
                    data["group"] = self.cal_data(
                        "Modem team", **data["group"])
                else:
                    data["group"] = self.cal_data(
                        "Non modem team", **data["group"])

                if cr_type:
                    data["all_patch"] = self.cal_data(
                        cr_type, **data["all_patch"])
                    if md_cr_check:
                        data["modem_patch"] = self.cal_data(
                            cr_type, **data["modem_patch"])

                data["state"] = self.cal_data(t_state, **data["state"])

            else:
                self.logger.log(LOG_TRACE_LVL,
                                "%s not in this activity: %s", t_crid, act_id)
                pass

        self.logger.info(
            "end to get_cr_anaylsis_by_hwprj_all_data, hw_prj_id: %s", hw_prj_id)

        if data == {}:
            self.logger.info(
                "no data for %s, hw_prj_id: %s", operator, hw_prj_id)
        return data

    def check_md_dept_or_not(self, assignee_dept):
        for eachdept in self.md_dept_list:
            result = re.findall(eachdept, assignee_dept)
            if result:
                return True
        return False
