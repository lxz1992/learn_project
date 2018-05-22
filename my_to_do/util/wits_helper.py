import json
import logging
from time import sleep

import requests
from requests.exceptions import HTTPError

from cr_review_sys.const import CrFieldMap, HwPrjFieldMap, Const, UsersFieldMap,\
    WitsUsersFieldMap, MdChangeLog
from md_analysis.const import MdState


class Wits(object):

    def __init__(self, clan, db):
        self.session = None
        self.clan = clan
        self.db = db
        self.user = 'cqsrv_mytodo'
        self.pwds = 'mytodo_rocks'
        self.url = 'http://172.21.101.232/secweb-web-script/mtk/'
        self.url_login = 'mtkScriptLogin.action'
        self.url_move_query = 'movedQuery.cq'
        self.method_common_query = 'getQueryResultCommonQuery'
        self.login()
        self.logger = logging.getLogger('aplogger')
        self.retryCnt = 3
        self.param_by_query_name = 'queryName'
        self.param_by_query_define = 'queryDefine'

    def __del__(self):
        self.logout()

    def login(self):
        self.session = requests.Session()
        param = {'method': 'login', 'repository': self.clan,
                 'userDb': self.db, 'loginId': self.user, 'password': self.pwds}
        response = self.session.post(self.url + self.url_login, data=param)
        response.raise_for_status()

    def logout(self):
        param = {'method': 'logout'}
        self.session.post(self.url + self.url_login, data=param)

    def invalidateSession(self):
        try:
            self.logout()
        except Exception:
            self.logger.exception("Fail to logout, directly login...")

        finally:
            self.login()

    def checkSession(self):
        url = self.url + self.url_move_query
        query_param = {'method': 'getCrMainInfo', 'crId': 'ALPS00059971'}
        resonpse_result = self.__post(url, data=query_param)
        result = json.loads(resonpse_result.text)

        # if no logined key, means session exists
        login_result = result.get('logined', True)

        if login_result == 'false':
            self.logger.info("wits session expired, need to login again")
            return False
        return True

    def __post(self, url, data=None, **kwds):
        for i in range(self.retryCnt):
            try:
                resp = self.session.post(url, data=data, **kwds)
                resp.raise_for_status()

                return resp
            except HTTPError:
                if i == self.retryCnt - 1:
                    self.logger.exception(
                        "Fail to post and retry for {} times...".format(i))

                    raise Exception("post to {} fail!".format(url))

                self.logger.exception("Fail to post, retry %s...", i + 1)
                self.invalidateSession()

    def post_request_by_query_define(self, url, method, query_param, query_value, start_rows):
        query_param = {'method': method,
                       query_param: query_value, 'startRow': start_rows}
        resonpse_result = self.__post(url, data=query_param)
        result = json.loads(resonpse_result.text)
        return result

    def __get_all_result_by_query_define(self, method, query_param, query_value):
        self.logger.info('method:' + method)
        self.logger.info('query_param:' + query_param)
        self.logger.info('query_value:' + query_value)
        ini_data = self.post_request_by_query_define(
            self.url + self.url_move_query, method, query_param, query_value, 1)

        result = {}
        check_result = ini_data.get('total', False)
        if check_result:
            pagination = 1000
            page = int(int(ini_data['total']) / pagination) + 1
            result = ini_data['rows']
            count = 1
            self.logger.info('page: %s', page)
            while(count < page):
                start_rows = count * pagination + 1
                temp_data = self.post_request_by_query_define(
                    self.url + self.url_move_query, method, query_param, query_value, start_rows)
                result = result + temp_data['rows']
                self.logger.debug("finish getting %s page", count)
                count += 1
                sleep(5)
        else:
            self.logger.error("no key total, dump ini_data: %s", ini_data)
        return result

    def __format_users_to_dict(self, data_list):
        result_dict = {}

        i = 0
        self.logger.info("total not mtk user qty: %s", len(data_list))
        while i < len(data_list):

            key = None
            values = None

            # user login_name as result dict key
            key = data_list[i][WitsUsersFieldMap.LOGIN_NAME]

            if key in result_dict.keys():
                new_group = "{};{}".format(
                    data_list[i][WitsUsersFieldMap.DEPT_NAME], result_dict[key][UsersFieldMap.DEPT_NAME])
                result_dict[key][UsersFieldMap.DEPT_NAME] = new_group

            else:
                is_active = True if data_list[i][WitsUsersFieldMap.IS_ACTIVE] else False
                values = {
                    UsersFieldMap.DEPT_NAME: data_list[i][WitsUsersFieldMap.DEPT_NAME],
                    UsersFieldMap.LOGIN_NAME: data_list[i][WitsUsersFieldMap.LOGIN_NAME],
                    UsersFieldMap.FULL_NAME: data_list[i][WitsUsersFieldMap.FULL_NAME],
                    UsersFieldMap.E_MAIL: data_list[i][WitsUsersFieldMap.E_MAIL],
                    UsersFieldMap.IS_ACTIVE: is_active}
                result_dict[key] = values
            i += 1
        return result_dict

    def get_not_mtk_users(self):
        tmp_all_user_list = self.__get_all_result_by_query_define(
            self.method_common_query, self.param_by_query_name, Const.NOT_MTK_USERS_QUERY)
        all_user_dict = self.__format_users_to_dict(tmp_all_user_list)

        return all_user_dict

    def get_activity_cr_by_act_def(self, query_name):
        tmp_all_data = self.__get_all_result_by_query_define(
            self.method_common_query, self.param_by_query_name, query_name)
        all_data = self.__format_activity_cr_to_dict(tmp_all_data)
        return all_data

    def __format_activity_cr_to_dict(self, data):
        result_dict = {}

        i = 0
        while i < len(data):

            crid = str(data[i]['id'])
            values = {'crid': crid}

            result_dict[crid] = values

            i += 1

        return result_dict

    def get_cr_info(self, cr_id):

        query_define = '{"recordType":"CR","filter":{"operation":"and","children":[{"fieldOperation":"eq","fieldPath":"id","fieldValue":[{"value":"' + cr_id + \
            '","type":"normal"}]}]},"display":[{"isVisible":"true","fieldPath":"id","fieldLabel":"id","sortOrder":"","sortType":null},{"sortType":null,"sortOrder":"","fieldLabel":"Title","isVisible":"true","fieldPath":"Title"},{"sortType":null,"fieldLabel":"Priority","sortOrder":"","isVisible":"true","fieldPath":"Priority"},{"sortType":null,"fieldLabel":"Class","sortOrder":"","isVisible":"true","fieldPath":"Class"},{"sortOrder":"","fieldLabel":"State","sortType":null,"fieldPath":"State","isVisible":"true"},{"fieldPath":"Source","isVisible":"true","sortType":null,"fieldLabel":"Source","sortOrder":null},{"fieldLabel":"Submitter","sortOrder":null,"sortType":null,"isVisible":"true","fieldPath":"Submitter"},{"sortOrder":null,"fieldLabel":"Submit_Date","sortType":null,"isVisible":"true","fieldPath":"Submit_Date"},{"sortType":null,"sortOrder":null,"fieldLabel":"Assignee","fieldPath":"Assignee","isVisible":"true"},{"sortOrder":null,"fieldLabel":"Assignee.groups","sortType":null,"isVisible":"true","fieldPath":"Assignee.groups"},{"sortOrder":null,"fieldLabel":"Dispatch_Count","sortType":null,"isVisible":"true","fieldPath":"Dispatch_Count"},{"fieldPath":"Assign_Date","isVisible":"true","sortType":null,"fieldLabel":"Assign_Date","sortOrder":null},{"isVisible":"true","fieldPath":"Resolve_Date","fieldLabel":"Resolve_Date","sortOrder":null,"sortType":null},{"isVisible":"true","fieldPath":"Resolve_Time","sortType":null,"fieldLabel":"Resolve_Time","sortOrder":null},{"fieldPath":"Resolution","isVisible":"true","sortType":null,"sortOrder":"","fieldLabel":"Resolution"},{"isVisible":"true","fieldPath":"Customer_Company","sortOrder":null,"fieldLabel":"Customer_Company","sortType":null},{"fieldPath":"Solution","isVisible":"true","sortType":null,"sortOrder":null,"fieldLabel":"Solution"},{"isVisible":"true","fieldPath":"Inner_Solution","sortType":null,"fieldLabel":"Inner_Solution","sortOrder":null},{"fieldPath":"Solution_Category_Level1","isVisible":"true","sortType":null,"fieldLabel":"Solution_Category_Level1","sortOrder":null},{"fieldPath":"Solution_Category_Level2","isVisible":"true","sortType":null,"fieldLabel":"Solution_Category_Level2","sortOrder":null},{"sortType":null,"fieldLabel":"HW_Project.Platform_Group","sortOrder":null,"isVisible":"true","fieldPath":"HW_Project.Platform_Group"},{"fieldPath":"MD_Info.Patch_ID","isVisible":"true","sortOrder":null,"fieldLabel":"MD_Info.Patch_ID","sortType":null},{"fieldLabel":"MD_Info.SV_MCE_effort","sortOrder":null,"sortType":null,"fieldPath":"MD_Info.SV_MCE_effort","isVisible":"true"},{"sortType":null,"sortOrder":null,"fieldLabel":"MD_Info.PLMN1","fieldPath":"MD_Info.PLMN1","isVisible":"true"},{"sortOrder":null,"fieldLabel":"MD_Info.PLMN2","sortType":null,"fieldPath":"MD_Info.PLMN2","isVisible":"true"},{"isVisible":"true","fieldPath":"MD_Info.Country","sortType":null,"sortOrder":null,"fieldLabel":"MD_Info.Country"},{"fieldLabel":"MD_Info.OP_Name","sortOrder":"","sortType":null,"isVisible":"true","fieldPath":"MD_Info.OP_Name"},{"sortOrder":"","fieldLabel":"MD_Info.RAT1","sortType":null,"isVisible":"true","fieldPath":"MD_Info.RAT1"},{"fieldPath":"MD_Info.RAT2","isVisible":"true","sortType":null,"fieldLabel":"MD_Info.RAT2","sortOrder":""},{"sortType":null,"fieldLabel":"MD_Info.Cell_ID","sortOrder":"","isVisible":"true","fieldPath":"MD_Info.Cell_ID"},{"fieldPath":"MD_Info.TAC_LAC","isVisible":"true","sortOrder":"","fieldLabel":"MD_Info.TAC_LAC","sortType":null},{"isVisible":"true","fieldPath":"HW_Project.HW_Project_ID","sortType":null,"sortOrder":"","fieldLabel":"HW_Project.HW_Project_ID"},{"sortType":null,"sortOrder":null,"fieldLabel":"MD_Info.Other_Info","fieldPath":"MD_Info.Other_Info","isVisible":"true"},{"fieldPath":"Bug_Reason","isVisible":"true","sortType":null,"fieldLabel":"Bug_Reason","sortOrder":null},{"fieldPath":"User_Field3","isVisible":"true","sortType":null,"fieldLabel":"User_Field3","sortOrder":null},{"fieldPath":"Test_Category","isVisible":"true","sortType":null,"fieldLabel":"Test_Category","sortOrder":null}]}'

        tmp_cr_info = self.__get_all_result_by_query_define(
            self.method_common_query, self.param_by_query_define, query_define)
        cr_info = self.__format_cr_info_to_dict(tmp_cr_info)
        self.logger.debug(u"create infor: %s", cr_info)
        return cr_info

    def get_cr_info_no_changelog(self, cr_id):
        query_define = '{"recordType":"CR","filter":{"operation":"and","children":[{"fieldOperation":"eq","fieldPath":"id","fieldValue":[{"value":"' + cr_id + \
            '","type":"normal"}]}]},"display":[{"fieldLabel":"MD_Info.Patch_ID","sortType":null,"fieldPath":"MD_Info.Patch_ID","sortOrder":null,"isVisible":"true"},{"sortType":null,"fieldLabel":"MD_Info.SV_MCE_effort","sortOrder":null,"isVisible":"true","fieldPath":"MD_Info.SV_MCE_effort"},{"sortType":null,"fieldLabel":"MD_Info.PLMN1","isVisible":"true","sortOrder":null,"fieldPath":"MD_Info.PLMN1"},{"sortType":null,"fieldLabel":"MD_Info.PLMN2","isVisible":"true","sortOrder":null,"fieldPath":"MD_Info.PLMN2"},{"sortType":null,"fieldLabel":"MD_Info.Country","isVisible":"true","sortOrder":null,"fieldPath":"MD_Info.Country"},{"isVisible":"true","sortOrder":"","fieldPath":"MD_Info.OP_Name","sortType":null,"fieldLabel":"MD_Info.OP_Name"},{"isVisible":"true","sortOrder":"","fieldPath":"MD_Info.RAT1","sortType":null,"fieldLabel":"MD_Info.RAT1"},{"fieldPath":"MD_Info.RAT2","isVisible":"true","sortOrder":"","fieldLabel":"MD_Info.RAT2","sortType":null},{"fieldLabel":"MD_Info.Cell_ID","sortType":null,"fieldPath":"MD_Info.Cell_ID","isVisible":"true","sortOrder":""},{"fieldPath":"MD_Info.TAC_LAC","isVisible":"true","sortOrder":"","fieldLabel":"MD_Info.TAC_LAC","sortType":null},{"sortType":null,"sortOrder":null,"fieldLabel":"MD_Info.Other_Info","fieldPath":"MD_Info.Other_Info","isVisible":"true"}]}'
        tmp_cr_info = self.__get_all_result_by_query_define(
            self.method_common_query, self.param_by_query_define, query_define)
        cr_info = self.__format_cr_info_no_changelog_to_dict(tmp_cr_info)
        self.logger.debug(u"update infor: %s", cr_info)
        return cr_info

    '''
    gather all updated info for particular crid
        1. infor query from change log
        2. not in change log data, ex. MD_INFO.xxxx
    '''

    def get_updated_cr_info(self, last_sync_time, cr_id):
        final_cr_info = {Const.CR_ID: cr_id}
        cr_info = self.get_cr_info_by_changelog(last_sync_time, cr_id)
        no_change_log_cr_info = self.get_cr_info_no_changelog(cr_id)
        final_cr_info[Const.DATA] = {**cr_info, **no_change_log_cr_info}
        return final_cr_info

    def get_cr_info_by_changelog(self, last_time, cr_id):

        query_define = '{"recordType":"CR_Log","filter":{"operation":"and","children":[{"fieldPath":"When","fieldValue":[{"type":"normal","value":"' + last_time + '"},{"type":"special","value":"[TODAY]"}],"fieldOperation":"between"},{"fieldValue":[{"value":"' + cr_id + \
            '","type":"normal"}],"fieldPath":"Cr_Id","fieldOperation":"eq"}]},"display":[{"sortOrder":null,"sortType":null,"isVisible":"true","fieldPath":"Cr_Id","fieldLabel":"Cr_Id"},{"sortOrder":null,"sortType":null,"isVisible":"true","fieldPath":"Field_Name","fieldLabel":"Field_Name"},{"fieldPath":"New_Value","isVisible":"true","sortType":null,"fieldLabel":"New_Value","sortOrder":null},{"sortType":null,"fieldPath":"When","isVisible":"true","fieldLabel":"When","sortOrder":"1"}]}'
        self.logger.info("last_time: %s", last_time)
        tmp_changelog = self.__get_all_result_by_query_define(
            self.method_common_query, self.param_by_query_define, query_define)
        update_cr_info = self.__format_cr_changelog_to_dict(tmp_changelog)
        self.logger.debug(u"update infor by changelog: %s", update_cr_info)

        is_state_change = update_cr_info.get(
            CrFieldMap.Wits.State, None)
        if is_state_change:
            state = update_cr_info[CrFieldMap.Wits.State]
            self.logger.info("%s state change to %s", cr_id, state)
            if state == MdState.Resolved.Resolved.value or state == MdState.Resolved.Closed.value or state == MdState.Resolved.Verified.value:
                resolved_info = self.get_cr_resolved_time(cr_id)
                self.logger.debug("get resolved info: %s", resolved_info)
                if resolved_info:
                    update_cr_info.update(resolved_info)
        return update_cr_info

    def get_cr_resolved_time(self, cr_id):

        query_define = '{"recordType":"CR","filter":{"children":[{"fieldOperation":"eq","fieldPath":"id","fieldValue":[{"type":"normal","value":"' + cr_id + \
            '"}]}],"operation":"and"},"display":[{"sortType":null,"sortOrder":null,"isVisible":"true","fieldLabel":"Resolve_Date","fieldPath":"Resolve_Date"},{"fieldPath":"Resolve_Time","fieldLabel":"Resolve_Time","isVisible":"true","sortOrder":null,"sortType":null}]}'

        tmp_result = self.__get_all_result_by_query_define(
            self.method_common_query, self.param_by_query_define, query_define)
        resolved_info = self.__format_cr_resolved_info_to_dict(tmp_result)
        return resolved_info

    def __format_cr_resolved_info_to_dict(self, data):
        result_dict = {}
        if data:
            tmp_data = dict(data[0])
            resolve_date = tmp_data["Resolve_Date"]
            resolve_time = tmp_data["Resolve_Time"]

            if resolve_date:
                result_dict.update(
                    {CrFieldMap.Wits.Resolve_Date: resolve_date})
            if resolve_time:
                result_dict.update(
                    {CrFieldMap.Wits.Resolve_Time: resolve_time})

        return result_dict

    def __format_cr_changelog_to_dict(self, data):
        cr_id_db_field = CrFieldMap.Wits.id
        cr_id = None
        tmp_result = {}
        for x in range(0, len(data)):
            cr_id = data[x].get("Cr_Id", cr_id)
            field = data[x].get("Field_Name", "").replace(".", "_")
            value = data[x].get("New_Value", "")

            try:
                db_field = getattr(CrFieldMap.Wits, field)
                tmp_result.update({db_field: value})
                self.logger.info("get field: %s", db_field)
            except AttributeError:
                self.logger.warn("no need to update for [%s]", field)
        return tmp_result

    def __format_cr_info_to_dict(self, data):
        tmp_cr = dict(data[0])

        result_dict = {
            CrFieldMap.Wits.id: tmp_cr.get("id", ""),
            CrFieldMap.Wits.Title: tmp_cr.get("Title", ""),
            CrFieldMap.Wits.Priority: tmp_cr.get("Priority", ""),
            CrFieldMap.Wits.Class: tmp_cr.get("Class", ""),
            CrFieldMap.Wits.State: tmp_cr.get("State", ""),
            CrFieldMap.Wits.Source: tmp_cr.get("Source", ""),
            CrFieldMap.Wits.Submitter: tmp_cr.get("Submitter", ""),
            CrFieldMap.Wits.Assignee: tmp_cr.get("Assignee", ""),
            CrFieldMap.Wits.Assignee_Dept: tmp_cr.get("Assignee.groups", ""),
            CrFieldMap.Wits.Resolution: tmp_cr.get("Resolution", ""),
            CrFieldMap.Wits.Customer_Company: tmp_cr.get("Customer_Company", ""),
            CrFieldMap.Wits.Solution: tmp_cr.get("Solution", ""),
            CrFieldMap.Wits.Inner_Solution: tmp_cr.get("Inner_Solution", ""),
            CrFieldMap.Wits.Solution_Category_Level1: tmp_cr.get("Solution_Category_Level1", ""),
            CrFieldMap.Wits.Solution_Category_Level2: tmp_cr.get("Solution_Category_Level2", ""),
            CrFieldMap.Wits.HW_Project_Platform_Group: tmp_cr.get("HW_Project.Platform_Group", ""),
            CrFieldMap.Wits.MD_Info_Patch_ID: tmp_cr.get("MD_Info.Patch_ID", ""),
            CrFieldMap.Wits.MD_Info_SV_MCE_effort: tmp_cr.get("MD_Info.SV_MCE_effort", ""),
            CrFieldMap.Wits.MD_Info_PLMN1: tmp_cr.get("MD_Info.PLMN1", ""),
            CrFieldMap.Wits.MD_Info_PLMN2: tmp_cr.get("MD_Info.PLMN2", ""),
            CrFieldMap.Wits.MD_Info_Country: tmp_cr.get("MD_Info.Country", ""),
            CrFieldMap.Wits.MD_Info_OP_Name: tmp_cr.get("MD_Info.OP_Name", ""),
            CrFieldMap.Wits.MD_Info_RAT1: tmp_cr.get("MD_Info.RAT1", ""),
            CrFieldMap.Wits.MD_Info_RAT2: tmp_cr.get("MD_Info.RAT2", ""),
            CrFieldMap.Wits.MD_Info_Cell_ID: tmp_cr.get("MD_Info.Cell_ID", ""),
            CrFieldMap.Wits.MD_Info_TAC_LAC: tmp_cr.get("MD_Info.TAC_LAC", ""),
            CrFieldMap.Wits.HW_Project_HW_Project_ID: tmp_cr.get("HW_Project.HW_Project_ID", ""),
            CrFieldMap.Custom.Country: None,
            CrFieldMap.Custom.Operator: None,
            CrFieldMap.Custom.Is_Active: "1",
            CrFieldMap.Wits.MD_Info_OTHER_INFO: tmp_cr.get("MD_Info.Other_Info", ""),
            CrFieldMap.Wits.Bug_Reason: tmp_cr.get("Bug_Reason", ""),
            CrFieldMap.Wits.Test_Category: tmp_cr.get("Test_Category", ""),
            CrFieldMap.Wits.Local_Issue: tmp_cr.get("User_Field3", "")
        }

        submit_date = tmp_cr.get("Submit_Date", "")
        assign_date = tmp_cr.get("Assign_Date", "")
        resolve_date = tmp_cr.get("Resolve_Date", "")
        dispatch_count = tmp_cr.get("Dispatch_Count", "")
        resolve_time = tmp_cr.get("Resolve_Time", "")

        if submit_date:
            result_dict.update({CrFieldMap.Wits.Submit_Date: submit_date})
        if assign_date:
            result_dict.update({CrFieldMap.Wits.Assign_Date: assign_date})
        if resolve_date:
            result_dict.update({CrFieldMap.Wits.Resolve_Date: resolve_date})
        if dispatch_count:
            result_dict.update(
                {CrFieldMap.Wits.Dispatch_Count: int(dispatch_count)})
        if resolve_time:
            result_dict.update(
                {CrFieldMap.Wits.Resolve_Time: int(resolve_time)})
        return result_dict

    def __format_cr_info_no_changelog_to_dict(self, data):
        tmp_cr = dict(data[0])
        result_dict = {
            CrFieldMap.Wits.MD_Info_Patch_ID: tmp_cr["MD_Info.Patch_ID"],
            CrFieldMap.Wits.MD_Info_SV_MCE_effort: tmp_cr["MD_Info.SV_MCE_effort"],
            CrFieldMap.Wits.MD_Info_PLMN1: tmp_cr["MD_Info.PLMN1"],
            CrFieldMap.Wits.MD_Info_PLMN2: tmp_cr["MD_Info.PLMN2"],
            CrFieldMap.Wits.MD_Info_Country: tmp_cr["MD_Info.Country"],
            CrFieldMap.Wits.MD_Info_OP_Name: tmp_cr["MD_Info.OP_Name"],
            CrFieldMap.Wits.MD_Info_RAT1: tmp_cr["MD_Info.RAT1"],
            CrFieldMap.Wits.MD_Info_RAT2: tmp_cr["MD_Info.RAT2"],
            CrFieldMap.Wits.MD_Info_Cell_ID: tmp_cr["MD_Info.Cell_ID"],
            CrFieldMap.Wits.MD_Info_TAC_LAC: tmp_cr["MD_Info.TAC_LAC"],
            CrFieldMap.Wits.MD_Info_OTHER_INFO: tmp_cr["MD_Info.Other_Info"]
        }
        return result_dict

    def __format_md_info_to_dict(self, data):
        result = []
        for eachrow in data:
            tmp_data = {
                CrFieldMap.Wits.MD_Info_Patch_ID: eachrow["Patch_ID"],
                CrFieldMap.Wits.MD_Info_SV_MCE_effort: eachrow["SV_MCE_effort"],
                CrFieldMap.Wits.MD_Info_PLMN1: eachrow["PLMN1"],
                CrFieldMap.Wits.MD_Info_PLMN2: eachrow["PLMN2"],
                CrFieldMap.Wits.MD_Info_Country: eachrow["Country"],
                CrFieldMap.Wits.MD_Info_OP_Name: eachrow["OP_Name"],
                CrFieldMap.Wits.MD_Info_RAT1: eachrow["RAT1"],
                CrFieldMap.Wits.MD_Info_RAT2: eachrow["RAT2"],
                CrFieldMap.Wits.MD_Info_Cell_ID: eachrow["Cell_ID"],
                CrFieldMap.Wits.MD_Info_TAC_LAC: eachrow["TAC_LAC"],
                CrFieldMap.Wits.MD_Info_OTHER_INFO: eachrow["Other_Info"]
            }

            tmp_result = {
                CrFieldMap.Wits.id: eachrow["CR_ID"],
                Const.DATA: tmp_data
            }
            result.append(tmp_result)
        return result

    def get_hw_prj_info(self, hw_prj_id):
        query_define = '{"recordType":"HW_Project","filter":{"operation":"and","children":[{"fieldValue":[{"value":"' + hw_prj_id + '","type":"normal"}],"fieldOperation":"eq","fieldPath":"HW_Project_ID"}]},"display":[{"sortType":null,"fieldPath":"HW_Project_Status","fieldLabel":"HW_Project_Status","sortOrder":null,"isVisible":"true"},{"sortType":null,"fieldPath":"Name","isVisible":"true","sortOrder":null,"fieldLabel":"Name"},{"fieldPath":"Company","sortType":null,"isVisible":"true","fieldLabel":"Company","sortOrder":null},{"sortOrder":null,"fieldLabel":"SWPM.fullname","isVisible":"true","fieldPath":"SWPM.fullname","sortType":null},{"fieldPath":"Platform","sortType":null,"isVisible":"true","fieldLabel":"Platform","sortOrder":null}]}'

        tmp_prj_info = self.__get_all_result_by_query_define(
            self.method_common_query, self.param_by_query_define, query_define)
        prj_info = self.__format_prj_info_to_dict(tmp_prj_info)
        self.logger.debug("prj infor: %s", prj_info)
        return prj_info

    def __format_prj_info_to_dict(self, data):
        if data == []:
            self.logger.info("no data")
            return {}
        tmp_prj = dict(data[0])

        result_dict = {
            HwPrjFieldMap.HW_Project_Status: tmp_prj.get("HW_Project_Status", ""),
            HwPrjFieldMap.Name: tmp_prj.get("Name", ""),
            HwPrjFieldMap.Company: tmp_prj.get("Company", ""),
            HwPrjFieldMap.SWPM_fullname: tmp_prj.get("SWPM.fullname", ""),
            HwPrjFieldMap.Platform: tmp_prj.get("Platform", "")
        }
        return result_dict

    '''
    The logic is addressed in the query define in WITS(CQ)
    current rule: open CR + resolved CR within 2 days, 2018.01.16
    '''

    def get_md_whilelist_change(self):
        query_value = 'Personal Queries/New_Mytodo/Md_analysis/Modem_Analysis_CRs_whitelist_change'
        tmp_result = self.__get_all_result_by_query_define(
            self.method_common_query, self.param_by_query_name, query_value)
        cr_dict = self.__format_md_whilelist_to_list(tmp_result)
        return cr_dict

    def __format_md_whilelist_to_list(self, data):
        DEPT_ADD = "+"
        DEPT_CUT = "-"
        new_list = []
        disable_list = []
        result = {Const.NEW_CR: [], Const.DISABLE_CR: []}
        tmp_result = {}
        i = 0
        while i < len(data):
            crid = str(data[i]['CR_ID'])
            cr_type = str(data[i]['TYPE'])
            tmp_result.update({crid: cr_type})
            i += 1

        for eachdata in tmp_result:
            if tmp_result[eachdata] == DEPT_ADD:
                new_list.append(eachdata)
            elif tmp_result[eachdata] == DEPT_CUT:
                disable_list.append(eachdata)
            else:
                self.logger.warning("couldn't get valid type for %s", eachdata)
        result[Const.NEW_CR] = new_list
        result[Const.DISABLE_CR] = disable_list
        return result

    '''
    Send last_time to address the time interval for query
    '''

    def get_updated_md_info(self, last_time):
        query_define = '{"recordType":"Modem_Info","filter":{"children":[{"fieldValue":[{"value":"' + last_time + '","type":"normal"}],"fieldOperation":"ge","fieldPath":"last_updated_date"}],"operation":"and"},"display":[{"sortOrder":"","isVisible":"true","fieldPath":"CR_ID","sortType":null,"fieldLabel":"CR_ID"},{"fieldLabel":"Patch_ID","isVisible":"true","sortOrder":null,"fieldPath":"Patch_ID","sortType":null},{"fieldLabel":"SV_MCE_effort","sortType":null,"sortOrder":null,"isVisible":"true","fieldPath":"SV_MCE_effort"},{"isVisible":"true","sortOrder":null,"fieldPath":"PLMN1","sortType":null,"fieldLabel":"PLMN1"},{"fieldLabel":"PLMN2","sortOrder":null,"isVisible":"true","fieldPath":"PLMN2","sortType":null},{"fieldLabel":"Country","fieldPath":"Country","sortOrder":null,"isVisible":"true","sortType":null},{"fieldLabel":"OP_Name","sortOrder":null,"fieldPath":"OP_Name","isVisible":"true","sortType":null},{"sortType":null,"fieldPath":"RAT1","sortOrder":null,"isVisible":"true","fieldLabel":"RAT1"},{"sortOrder":null,"isVisible":"true","fieldPath":"RAT2","sortType":null,"fieldLabel":"RAT2"},{"fieldLabel":"Cell_ID","fieldPath":"Cell_ID","sortOrder":null,"isVisible":"true","sortType":null},{"fieldLabel":"TAC_LAC","fieldPath":"TAC_LAC","sortOrder":null,"isVisible":"true","sortType":null},{"fieldLabel":"Other_Info","isVisible":"true","sortOrder":null,"fieldPath":"Other_Info","sortType":null},{"fieldLabel":"last_updated_date","sortOrder":null,"fieldPath":"last_updated_date","isVisible":"true","sortType":"ASC"}]}'
        tmp_info = self.__get_all_result_by_query_define(
            self.method_common_query, self.param_by_query_define, query_define)
        md_info = self.__format_md_info_to_dict(tmp_info)
        return md_info

    def get_md_changelog(self, last_time):
        query_define = '{"recordType":"CR","filter":{"operation":"and","children":[{"children":[{"fieldValue":[{"value":"wsp_sv_msv","type":"normal"}],"fieldOperation":"like","fieldPath":"Assignee_Dept"},{"fieldPath":"Assignee_Dept","fieldValue":[{"type":"normal","value":"wct_sa_sv"}],"fieldOperation":"like"},{"fieldPath":"Assignee_Dept","fieldValue":[{"type":"normal","value":"wcp1_sa1_sqa"}],"fieldOperation":"like"},{"fieldPath":"Assignee_Dept","fieldValue":[{"type":"normal","value":"wcp1_sa_sqa"}],"fieldOperation":"like"},{"fieldValue":[{"value":"wcp1_sa2_sv","type":"normal"}],"fieldOperation":"like","fieldPath":"Assignee_Dept"},{"fieldPath":"Assignee_Dept","fieldOperation":"like","fieldValue":[{"value":"mti_wsp_sv","type":"normal"}]},{"fieldOperation":"like","fieldValue":[{"type":"normal","value":"mti_wct_sa"}],"fieldPath":"Assignee_Dept"},{"fieldValue":[{"type":"normal","value":"mti_wcp1sa"}],"fieldOperation":"like","fieldPath":"Assignee_Dept"},{"fieldPath":"Assignee_Dept","fieldOperation":"like","fieldValue":[{"value":"msz_wsp_sv","type":"normal"}]},{"fieldPath":"Assignee_Dept","fieldValue":[{"value":"msz_wct","type":"normal"}],"fieldOperation":"like"},{"fieldPath":"Assignee_Dept","fieldValue":[{"value":"msz_wcp1s","type":"normal"}],"fieldOperation":"like"},{"fieldOperation":"like","fieldValue":[{"value":"mshc_wsp_sv","type":"normal"}],"fieldPath":"Assignee_Dept"},{"fieldOperation":"like","fieldValue":[{"value":"msh_wct_sa","type":"normal"}],"fieldPath":"Assignee_Dept"},{"fieldValue":[{"type":"normal","value":"msh_wcp1s"}],"fieldOperation":"like","fieldPath":"Assignee_Dept"},{"fieldOperation":"like","fieldValue":[{"type":"normal","value":"mshc_wct_sa"}],"fieldPath":"Assignee_Dept"},{"fieldPath":"Assignee_Dept","fieldOperation":"like","fieldValue":[{"value":"wcs_sd","type":"normal"}]},{"fieldValue":[{"type":"normal","value":"wcs_se2"}],"fieldOperation":"like","fieldPath":"Assignee_Dept"},{"fieldPath":"Assignee_Dept","fieldValue":[{"value":"wcs_se3","type":"normal"}],"fieldOperation":"like"},{"fieldPath":"Assignee_Dept","fieldOperation":"like","fieldValue":[{"value":"wct_msp","type":"normal"}]},{"fieldOperation":"like","fieldValue":[{"type":"normal","value":"wcs_mdd"}],"fieldPath":"Assignee_Dept"},{"fieldPath":"Assignee_Dept","fieldOperation":"like","fieldValue":[{"value":"wcs_sse","type":"normal"}]},{"fieldPath":"Assignee_Dept","fieldValue":[{"value":"wcs_st","type":"normal"}],"fieldOperation":"like"},{"fieldPath":"Assignee_Dept","fieldOperation":"like","fieldValue":[{"type":"normal","value":"wsp_se7"}]},{"fieldValue":[{"value":"wcs_se8","type":"normal"}],"fieldOperation":"like","fieldPath":"Assignee_Dept"},{"fieldPath":"Assignee_Dept","fieldValue":[{"value":"wct_se1","type":"normal"}],"fieldOperation":"like"},{"fieldPath":"Assignee_Dept","fieldValue":[{"type":"normal","value":"wct_se9"}],"fieldOperation":"like"},{"fieldPath":"Assignee_Dept","fieldOperation":"like","fieldValue":[{"type":"normal","value":"wsp_msd"}]},{"fieldPath":"Assignee_Dept","fieldOperation":"like","fieldValue":[{"value":"wsp_cnopd1_pss","type":"normal"}]},{"fieldPath":"Assignee_Dept","fieldOperation":"like","fieldValue":[{"type":"normal","value":"mti_wsp_sv_sv-sd"}]},{"fieldValue":[{"value":"wsd_oss8_me9","type":"normal"}],"fieldOperation":"like","fieldPath":"Assignee_Dept"},{"fieldPath":"Assignee_Dept","fieldOperation":"like","fieldValue":[{"value":"wsp_mce","type":"normal"}]}],"operation":"or"},{"fieldPath":"Source","fieldOperation":"eq","fieldValue":[{"value":"Customer","type":"normal"}]},{"operation":"and","children":[{"fieldValue":[{"type":"normal","value":"' + last_time + '"}],"fieldOperation":"ge","fieldPath":"Change_Log.When"}]}]},"display":[{"isVisible":"true","sortOrder":"1","sortType":"ASC","fieldLabel":"id","fieldPath":"id"},{"fieldPath":"Change_Log.Field_Name","fieldLabel":"Change_Log.Field_Name","sortType":null,"sortOrder":null,"isVisible":"true"},{"fieldPath":"Change_Log.New_Value","fieldLabel":"Change_Log.New_Value","sortType":null,"sortOrder":null,"isVisible":"true"},{"fieldPath":"Change_Log.When","sortType":"ASC","fieldLabel":"Change_Log.When","isVisible":"true","sortOrder":"2"}]}}'
        self.logger.info("last_time: %s", last_time)
        tmp_changelog = self.__get_all_result_by_query_define(
            self.method_common_query, self.param_by_query_define, query_define)
        update_cr_info = self.__format_md_changelog_to_list(tmp_changelog)
        return update_cr_info

    def __format_md_changelog_to_list(self, data):
        result = []
        for x in range(0, len(data)):
            cr_id = data[x][MdChangeLog.CR_ID]
            field = data[x][MdChangeLog.FIELD]
            value = data[x][MdChangeLog.VALUE]

            try:
                db_field = getattr(CrFieldMap.Wits, field)
                self.logger.info("get field: %s", db_field)

                cr_detail_info = {db_field: value}

                if db_field == CrFieldMap.Wits.State:
                    self.logger.info("%s state change to %s", cr_id, field)
                if value == MdState.Resolved.Resolved.value or value == MdState.Resolved.Closed.value or value == MdState.Resolved.Verified.value:
                    resolved_info = self.get_cr_resolved_time(cr_id)
                    self.logger.debug("get resolved info: %s", resolved_info)
                    if resolved_info:
                        cr_detail_info.update(resolved_info)

                check_value = None
                try:
                    check_value = next(
                        element for element in result if element[Const.CR_ID] == cr_id)

                    list_index = result.index(
                        check_value)    # exist and get index
                    result[list_index][Const.DATA].update(cr_detail_info)
                except StopIteration:
                    # this crid didn't exist in result, added
                    tmp = {Const.CR_ID: cr_id, Const.DATA: cr_detail_info}
                    result.append(tmp)
            except AttributeError:
                self.logger.warn("no need to update for [%s]", field)
        return result
