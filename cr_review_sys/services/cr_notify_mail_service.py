'''
@author: mtk10809
'''
import codecs
from collections import OrderedDict
import json
import logging
import os
import re
import tempfile
import urllib

from django import template

from cr_review_sys.const import Const, CrFieldMap, ReviewInfoFieldMap,\
    ReviewCommentFieldMap, MailInfo, ActCrFieldMap, WitsClan
from cr_review_sys.models import ActivityCr, Cr, CrReviewinfo, CrReviewcomments,\
    Activity, Users
from cr_review_sys.services.mail_sender_service import MailSenderService
from my_to_do.util import Singleton
from my_to_do.util.date_helper import DateHelper


class CrNotifyMailService(object, metaclass=Singleton):
    def __init__(self):
        self.logger = logging.getLogger("aplogger")
        self.mail_sender = MailSenderService()
        self.users_mapping = self.get_users_mapping()

    def activity_mail_notice(self, json_file, json_path=None):
        params = self.get_param_by_file(json_file, json_path)

        activity_id = params.get(MailInfo.CommConfig.ACTIVITY_ID, None)
        activity_name = params.get(MailInfo.CommConfig.ACTIVITY_NAME, None)
        days_of_bug = params.get(MailInfo.CommConfig.DAYS_OF_BUG, 0)
        days_of_others = params.get(MailInfo.CommConfig.DAYS_OF_OTHERS, 0)
        to_list = params.get(MailInfo.CommConfig.TO_LIST, [])
        cc_list = params.get(MailInfo.CommConfig.CC_LIST, [])
        to_assignee = params.get(MailInfo.CommConfig.TO_ASSIGNEE, 0)
        cc_manager = params.get(MailInfo.CommConfig.CC_MANAGER, 0)
        raw_addi_info = params.get(MailInfo.CommConfig.ADDI_INFO, {})

        # if to_list is null, default send mail to activity owner
        if not to_list:
            act_info = self.get_activity_info(activity_id)
            act_owner_email = self.get_user_email(
                act_info[ActCrFieldMap.OWNER])
            to_list.append(act_owner_email)
        else:
            to_list = self.get_login_id_list_to_email_list(to_list)

        if cc_list:
            cc_list = self.get_login_id_list_to_email_list(cc_list)

        (std_config, cus_config) = self.get_valid_addi_info(**raw_addi_info)

        cr_info = self.get_activity_cr_info(activity_id)
        review_info = self.get_review_info(activity_id)
        review_comments = self.get_review_comments(
            activity_id) if MailInfo.AddiConfig.COMMENTS.value in std_config else {}
        column_list = self.get_column_list(std_config, cus_config)
        cr_count = 0
        act_url = "test_url, need to confrim with front-end"
        cook_cr_info = []
        for cr in cr_info:
            cr_id = cr[CrFieldMap.Wits.id]
            wits_db = self.get_cr_url(cr_id)
            clan = getattr(WitsClan, wits_db)
            cr_link = "{}_{}_{}{}{}".format(
                Const.SECWEB_PREFIX, clan, wits_db, Const.SECWEB_CR_URL, cr_id)
            check_waived = self.get_cr_waived_or_not(cr_id, **review_info)

            if check_waived:
                continue
            else:
                assignee_id = cr[CrFieldMap.Wits.Assignee]
                if to_assignee:
                    cr_assignee_email = self.get_user_email(assignee_id)
                    if cr_assignee_email not in to_list:
                        to_list.append(cr_assignee_email)
                if cc_manager:
                    cr_manager = self.get_user_manager(assignee_id)
                    cc_mangr_email = self.get_user_email(cr_manager)
                    if cc_mangr_email not in cc_list:
                        cc_list.append(cc_mangr_email)
                # gen content for cr notify
                assign_date = cr[CrFieldMap.Wits.Assign_Date]
                assign_count = DateHelper.get_days_from_specific_date(
                    assign_date)
                assign_dept_link = "http://{}{}".format(
                    Const.PEOPLE_FINDER, urllib.parse.quote(cr[CrFieldMap.Wits.Assignee_Dept]))
                assignee_full_name = self.get_users_full_name(assignee_id)
                assignee_link = "http://{}{}".format(
                    Const.PEOPLE_FINDER, urllib.parse.quote(assignee_full_name))
                cr_state = cr[CrFieldMap.Wits.State]
                first_hand_analysis = self.get_first_hand_analysis(cr_state)
                cr_review_comments = review_comments.get(cr_id, [])
                if MailInfo.AddiConfig.TIME.value in std_config:
                    assign_date = DateHelper.datetime_to_str(assign_date)
                else:
                    assign_date = DateHelper.datetime_to_str(
                        assign_date, str_format="%m/%d")

                data = (
                    (MailInfo.HtmlFieldMap.ID, cr_id),
                    (MailInfo.HtmlFieldMap.CR_LINK, cr_link),
                    (MailInfo.HtmlFieldMap.TITLE, cr[CrFieldMap.Wits.Title]),
                    (MailInfo.HtmlFieldMap.PRIORITY,
                     cr[CrFieldMap.Wits.Priority]),
                    (MailInfo.HtmlFieldMap.CLASS, cr[CrFieldMap.Wits.Class]),
                    (MailInfo.HtmlFieldMap.STATE, cr_state),
                    (MailInfo.HtmlFieldMap.ASSIGN_TEAM,
                     cr[CrFieldMap.Wits.Assignee_Dept]),
                    (MailInfo.HtmlFieldMap.ASSIGN_DEPT_LINK, assign_dept_link),
                    (MailInfo.HtmlFieldMap.ASSIGNEE, assignee_full_name),
                    (MailInfo.HtmlFieldMap.ASSIGNEE_LINK, assignee_link),
                    (MailInfo.HtmlFieldMap.ASSIGN, assign_date),
                    (MailInfo.HtmlFieldMap.ASSIGN_COUNT, assign_count),
                    (MailInfo.HtmlFieldMap.IMPORTANCE, review_info.get(
                        cr_id, {}).get(ReviewInfoFieldMap.IMPORTANCE, "")),
                    (MailInfo.HtmlFieldMap.WAR_ROOM, review_info.get(
                        cr_id, {}).get(ReviewInfoFieldMap.WAR_ROOM, "")),
                    (MailInfo.HtmlFieldMap.PROGRESS, review_info.get(
                        cr_id, {}).get(ReviewInfoFieldMap.PROGRESS, "")),
                    (MailInfo.HtmlFieldMap.ANALYSIS, first_hand_analysis),
                    (MailInfo.HtmlFieldMap.REMARK, review_info.get(
                        cr_id, {}).get(ReviewInfoFieldMap.REMARK, ""))
                )
                order_dict = OrderedDict(data)
                # handle custom config
                cus_cr_info = review_info.get(cr_id, {}).get(
                    ReviewInfoFieldMap.ADDITIONAL_FIELDS, {})
                for each_cus in cus_config:
                    tmp_value = cus_cr_info.get(each_cus, "")
                    order_dict.update({each_cus: tmp_value})
                # review comment should always at last
                order_dict.update(
                    {MailInfo.HtmlFieldMap.REVIEW_COMMENTS: cr_review_comments})

                cook_cr_info.append(order_dict)
                cr_count += 1

        if cr_count:
            mail_msg = self.get_mail_msg(
                activity_name, days_of_bug, days_of_others, act_url, cr_count, column_list, cook_cr_info)
            cr_notify_date = DateHelper.get_today()
            subject = "CR Notify - {} ({})".format(activity_name,
                                                   cr_notify_date)
            self.mail_sender.send_mail(to_list, cc_list, subject, mail_msg)
        else:
            self.logger.info("[%s][%s] no cr to send cr notify",
                             activity_id, activity_name)

    def get_column_list(self, std_config, cus_config):
                # set column list default
        column_list = [
            MailInfo.HtmlFieldMap.ID,
            MailInfo.HtmlFieldMap.TITLE,
            MailInfo.HtmlFieldMap.PRIORITY,
            MailInfo.HtmlFieldMap.CLASS,
            MailInfo.HtmlFieldMap.STATE,
            MailInfo.HtmlFieldMap.ASSIGN_TEAM,
            MailInfo.HtmlFieldMap.ASSIGNEE,
            MailInfo.HtmlFieldMap.ASSIGN
        ]

        if MailInfo.AddiConfig.TRACKING.value in std_config:
            column_list.append(MailInfo.HtmlFieldMap.IMPORTANCE)
            column_list.append(MailInfo.HtmlFieldMap.WAR_ROOM)
            column_list.append(MailInfo.HtmlFieldMap.PROGRESS)

        if MailInfo.AddiConfig.ANALYSIS.value in std_config:
            column_list.append(MailInfo.HtmlFieldMap.ANALYSIS)

        if MailInfo.AddiConfig.REMARK.value in std_config:
            column_list.append(MailInfo.HtmlFieldMap.REMARK)

        for eachcus in cus_config:
            column_list.append(eachcus)

        if MailInfo.AddiConfig.COMMENTS.value in std_config:
            column_list.append(MailInfo.HtmlFieldMap.REVIEW_COMMENTS)

        return column_list

    def get_cr_waived_or_not(self, cr_id, **review_info):
        result = None
        details_review_info = review_info.get(cr_id, None)

        if details_review_info:
            waived = details_review_info.get(ReviewInfoFieldMap.WAIVED, None)
            if waived:
                result = True if int(waived) == 1 else None

        return result

    def get_valid_addi_info(self, **raw_addi_info):
        # check which stardard addi info needed to show in cr notify mail
        # two lists: std_config & cus_config
        std_config = []
        cus_config = []
        standard_addi_info_key = [
            e.value for e in getattr(MailInfo, "AddiConfig")]

        for key in raw_addi_info:
            if key in standard_addi_info_key:
                value = int(raw_addi_info[key])
                std_config.append(key) if value else None
            else:
                value = int(raw_addi_info[key])
                if value:
                    cus_config.append(key) if value else None
        return (std_config, cus_config)

    def get_param_by_file(self, json_file, json_path):
        '''
        params = {
            "days_of_bug": 3,
            "days_of_others": 4,
            "to_list": [claire.hsieh@mediatek.com, cash.chang@mediatek.com],
            "cc_list": [],
            "to_assignee": 1,
            "cc_manager": 1,
            "raw_addi_info": {
                                            "Time": 0,
                                            "Remark": 0,
                                            "Analysis": 0,
                                            "Tracking": 0,
                                            "Comments": 0,
                                            "WTIS_Field1" : 1,
                                            "Add_Field1" : 1
                                            }"
        }
        '''
        params = {}
        try:
            file_path = json_path if json_path else tempfile.gettempdir()
            params_json = open(os.path.join(file_path, json_file)).read()
            params = json.loads(params_json)
        except Exception as e:
            self.logger.exception("load json file error: %s", e)
        return params

    def get_user_email(self, user):
        result = None
        queryset = Users.objects.filter(login_name=user)

        for eachrow in queryset:
            result = eachrow.e_mail

        return result

    def get_user_manager(self, user):
        result = None
        queryset = Users.objects.filter(login_name=user)

        for eachrow in queryset:
            result = eachrow.reporting_manager

        return result

    def get_activity_info(self, activity_id):
        result = {}
        queryset = Activity.objects.filter(activity_id=activity_id)

        for eachrow in queryset:
            tmp = {ActCrFieldMap.OWNER: eachrow.owner}
            result.update(tmp)
        return result

    def get_mail_msg(self, activity_name, days_of_bug, days_of_others, act_url, cr_count, column_list, cr_info):
        html_path = "cr_review_sys/templates/cr_review_mail/cr_notify_mail.html"
        with codecs.open(html_path, "r", encoding='utf-8', errors='ignore') as reader:
            content = reader.read()
            t = template.Template(content)
        c = template.Context({'activity_name': activity_name,
                              'days_of_bug': days_of_bug,
                              'days_of_others': days_of_others,
                              'url': act_url,
                              'cr_count': cr_count,
                              'column_list': column_list,
                              'cr_info': cr_info
                              })
        result = t.render(c)
        return result

    def get_activity_cr_list(self, activity_id):
        result = None
        queryset = ActivityCr.objects.filter(
            activity_id=activity_id, active=Const.IS_ACTIVE).values_list('cr_id', flat=True).distinct()
        result = list(queryset)
        return result

    def get_cr_url(self, cr_id):
        result = None
        rule = re.compile(r'[^a-zA-z]')
        result = rule.sub('', cr_id)
        return result

    def get_activity_cr_info(self, activity_id):
        result = []
        open_state_condition = [e.value for e in getattr(MailInfo, "State")]
        cr_list = self.get_activity_cr_list(activity_id)
        queryset = Cr.objects.filter(
            cr_id__in=cr_list, state__in=open_state_condition)

        for eachrow in queryset:
            tmp = {
                CrFieldMap.Wits.id: eachrow.cr_id,
                CrFieldMap.Wits.Title: eachrow.title,
                CrFieldMap.Wits.Priority: eachrow.priority,
                CrFieldMap.Wits.Class: eachrow.cr_class,
                CrFieldMap.Wits.State: eachrow.state,
                CrFieldMap.Wits.Assignee_Dept: eachrow.assignee_dept,
                CrFieldMap.Wits.Assignee: eachrow.assignee,
                CrFieldMap.Wits.Assign_Date: eachrow.assign_date
            }
            result.append(tmp)
        return result

    def get_review_info(self, activity_id):
        result = {}
        queryset = CrReviewinfo.objects.filter(activity_id=activity_id)

        for eachrow in queryset:
            additional_fields = {}
            cr_id = eachrow.cr_id

            try:
                additional_fields = json.loads(eachrow.additional_fields)
            except Exception:
                self.logger.error(
                    "[%s][%s] no addtional infor", activity_id, cr_id)
            tmp = {
                ReviewInfoFieldMap.WAIVED: eachrow.waived if eachrow.waived else "",
                ReviewInfoFieldMap.REMARK: eachrow.remark if eachrow.remark else "",
                ReviewInfoFieldMap.IMPORTANCE: eachrow.importance if eachrow.importance else "",
                ReviewInfoFieldMap.WAR_ROOM: eachrow.war_room if eachrow.war_room else "",
                ReviewInfoFieldMap.PROGRESS: eachrow.progress if eachrow.progress else "",
                ReviewInfoFieldMap.ADDITIONAL_FIELDS: additional_fields
            }
            result.update({cr_id: tmp})
        return result

    def get_review_comments(self, activity_id):
        result = {}
        queryset = CrReviewcomments.objects.filter(activity_id=activity_id)

        for eachrow in queryset:
            tmp = {
                ReviewCommentFieldMap.LOGIN_NAME: self.get_users_full_name(eachrow.login_name),
                ReviewCommentFieldMap.REVIEW_COMMENTS: eachrow.review_comments,
                ReviewCommentFieldMap.UPDATED_TIME: DateHelper.get_localtime_from_db(
                    eachrow.update_time, str_format="%Y%m%d")
            }

            if eachrow.cr_id in result:
                result[eachrow.cr_id].append(tmp)
            else:
                result.update({
                    eachrow.cr_id: [tmp]
                })
        return result

    def get_users_mapping(self):
        result = {}
        queryset = Users.objects.all()

        for eachrow in queryset:
            result.update({eachrow.login_name: eachrow.full_name})
        return result

    def get_users_full_name(self, login_name):
        result = None
        if login_name in self.users_mapping:
            result = self.users_mapping[login_name]
        return result

    def get_first_hand_analysis(self, cr_state):
        result = ""
        state_condition = [e.value for e in getattr(MailInfo, "State")]

        if cr_state in state_condition:
            result = Const.ONGOING
        return result

    def get_login_id_list_to_email_list(self, ori_list):
        # map login_name into email
        new_list = []
        for login_name in ori_list:
            tmp_email = self.get_user_email(login_name)
            if tmp_email not in new_list:
                new_list.append(tmp_email)
        return new_list
