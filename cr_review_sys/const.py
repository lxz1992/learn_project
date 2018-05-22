'''
Created on Dec 20, 2017

@author: claire
'''
from enum import Enum


# primitive types
class CrFieldMap:

    '''
    Map for CR field from WITS with DB column in mytodo
    '''
    class Wits:
        Assignee_Dept = "assignee_dept"
        Customer_Company = "customer_company"
        Assign_Date = "assign_date"
        Assignee = "assignee"
        Source = "cr_source"
        Resolve_Time = "resolve_time"
        Class = "cr_class"
        Submitter = "submitter"
        Inner_Solution = "inner_solution"
        id = "cr_id"
        Solution = "solution"
        Solution_Category_Level1 = "solution_category_level1"
        Solution_Category_Level2 = "solution_category_level2"
        Resolution = "resolution"
        Resolve_Date = "resolve_date"
        Title = "title"
        Priority = "priority"
        State = "state"
        Dispatch_Count = "dispatch_count"
        Submit_Date = "submit_date"
        Bug_Reason = "bug_reason"
        Local_Issue = "local_issue"
        Test_Category = "test_category"

        '''
        replace . with _, ex. HW_Project.HW_Project_ID => HW_Project_HW_Project_ID
        '''
        HW_Project_HW_Project_ID = "hw_project_id"
        HW_Project_Platform_Group = "platform_group"
        MD_Info_SV_MCE_effort = "sv_mce_effort"
        MD_Info_Patch_ID = "patch_id"
        MD_Info_Country = "md_info_country"
        MD_Info_OP_Name = "md_info_op_name"
        MD_Info_PLMN1 = "plmn1"
        MD_Info_PLMN2 = "plmn2"
        MD_Info_Cell_ID = "cell_id"
        MD_Info_RAT1 = "rat1"
        MD_Info_RAT2 = "rat2"
        MD_Info_TAC_LAC = "tac_lac"
        MD_Info_OTHER_INFO = "other_info"

    '''
    Custom field map, which data source not from WITS
    '''
    class Custom:
        BU_Type = "bu_type"
        Country = "country"
        Operator = "operator"
        Is_Active = "is_active"


class HwPrjFieldMap:
    HW_Project_Status = "hw_project_status"
    Name = "hw_project_name"
    Company = "company"
    SWPM_fullname = "swpm_fullname"
    Platform = "platform"


class PriorityAbbr:
    '''
    Ignore first two char for priority
    Map with abbreviation
    Ex.
        0.Urgent => Urgent
        1.High => High
        2.Medium => Medium
        3.Low => Low
    '''
    Urgent = "U"
    High = "H"
    Medium = "M"
    Low = "L"


class CrPriority:
    '''
    Address valid priorty from WITS(CQ)
    '''
    Urgent = "0.Urgent"
    High = "1.High"
    Medium = "2.Medium"
    Low = "3.Low"


class Const:
    STATUS = "status"
    ONGOING = "ongoing"
    FINISH = "finish"
    LAST_UPDATE_TIME = "last_update_time"
    ERROR_CODE = "error_code"
    ERROR_MSG = "error_msg"
    UPDATE_TIME = "update_time"
    IS_ACTIVE = "1"
    NOT_ACTIVE = "0"
    SYNC_JOB_ID = "sync_job_id"
    UPDATINGFLAG = "2"
    FULLSYNC = "full_sync"
    PARTIALSYNC = "partial_sync"
    CR_LIST = "cr_list"
    MD_ANALYS_ACT_STATUS_ID = "md_analysys_activity"
    CR_REVIEW_ACT_WL_STATUS_ID = "cr_review_activity_whilelist"
    SYNC_INTERVAL = "sync_interval"
    GET_LAST_TIME = "get_last_time"
    ACTIVITY_ID = "activity_id"
    CLAN = "clan"
    DB = "db"
    USERS_DEPTS_ID = "users_depts"
    DATA = "Data"
    NOT_MTK_USERS_QUERY = "Personal Queries/New_Mytodo/Cr_review/All_Not_MTK_users"
    MTK_PREFIX = "mtk"
    NOT_MTK = "not_mtk"
    ACTIVE = "Active"
    CR_ID = "cr_id"
    NEW_CR = "new"
    DISABLE_CR = "disable"
    API_DETAIL = "detail"
    REVIEW_INFO = "review_info"
    REVIEW_COMMENTS = "review_comments"
    UPDATED_TIME = "updated_time"
    UTF8 = "utf-8"
    MAIL_FROM = "CrReviewSystem@mediatek.com"
    MAIL_CONFIG_INFO = "additional_info_for_send_mail"
    SECWEB_PREFIX = "http://mtkcqweb.mediatek.inc/mtkcqweb"
    SECWEB_CR_URL = "/mtk/sec/cr/cr_view.jsp?crId="
    PEOPLE_FINDER = "peoplefinder.mediatek.inc/PeopleFinder/Home/SearchResult/ViewByCategories?pSiteGroup=MTK&keyword="


class CrMeta:
    ACT_CAT_TYPE = "CR Review"
    PREFIX_SYNC_JOB_ID = "CR"


class WitsClan:
    ALPS = "WCX_SmartPhone"
    MOLY = "WCX_FeaturePhone"
    tstdb = "Staging_Area"


class WitsDb:
    ALPS = "ALPS"
    MOLY = "MOLY"
    tstdb = "tstdb"


class ActCrFieldMap:
    ID = "id"
    ACTIVITY_ID = "activity_id"
    CR_ID = "cr_id"
    CR_DB = "cr_db"
    OWNER = "owner"


class SyncControlTag:
    MD_INFO = "SyncMDInfo"
    CR_INFO = "SyncCR"
    HW_PRJ = "SyncHWPrj"
    HW_MILESTONE = "SyncHWPrjMilestone"


class WitsUsersFieldMap:
    LOGIN_NAME = "LOGIN_NAME"
    FULL_NAME = "FULLNAME"
    E_MAIL = "EMAIL"
    IS_ACTIVE = "IS_ACTIVE"
    DEPT_NAME = "NAME"


class UsersFieldMap:
    DEPT_ID = "dept_id"
    LOGIN_NAME = "login_name"
    FULL_NAME = "full_name"
    E_MAIL = "e_mail"
    IS_ACTIVE = "is_active"
    DEPT_NAME = "dept_name"
    SITE = "site"
    REPORTING_MANAGER = "reporting_manager"


class DbConnStr:
    ODR = "mytodoreader/mytodoreader_mtk@172.21.104.226:1521/odrq"


class DeptsFieldMap:
    DEPT_ID = "dept_id"
    DEPT_NAME = "dept_name"
    IS_ACTIVE = "is_active"
    SITE = "site"
    DEPT_MANGR = "dept_mangr"
    PARENT_DEPT = "parent_dept"


class MdChangeLog:
    CR_ID = "id"
    WHEN = "Change_Log.When"
    FIELD = "Change_Log.Field_Name"
    VALUE = "Change_Log.New_Value"


class SubmitReviewInfo:
    class Param(Enum):
        CR_ID = "cr_id"
        UPDATED_TIME = "updated_time"
        WAIVED = "waived"
        ACTIVITY_ID = "activity_id"
        IMPORTANCE = "importance"
        WAR_ROOM = "war_room"
        PROGRESS = "progress"
        REMARK = "remark"
        ADDITIONAL_FIELDS = "additional_fields"
        LOGIN_NAME = "login_name"
        REVIEW_COMMENTS = "review_comments"


class ReviewInfoFieldMap:
    CR_ID = "cr_id"
    UPDATED_TIME = "updated_time"
    SYNC_TO_WITS = "sync_to_wits"
    WAIVED = "waived"
    ACTIVITY_ID = "activity_id"
    IMPORTANCE = "importance"
    WAR_ROOM = "war_room"
    PROGRESS = "progress"
    REMARK = "remark"
    REVIEWED = "reviewed"
    ID = "id"
    ADDITIONAL_FIELDS = "additional_fields"


class ReviewCommentFieldMap:
    CR_ID = "cr_id"
    ACTIVITY_ID = "activity_id"
    LOGIN_NAME = "login_name"
    UPDATED_TIME = "updated_time"
    REVIEW_COMMENTS = "review_comments"
    is_synced = "is_synced"


class MailInfo:
    class State(Enum):
        Submitted = "Submitted"
        Assigned = "Assigned"
        Working = "Working"
        Reworking = "Reworking"

    class CommConfig:
        ACTIVITY_ID = "activity_id"
        ACTIVITY_NAME = "activity_name"
        DAYS_OF_BUG = "days_of_bug"
        DAYS_OF_OTHERS = "days_of_others"
        TO_LIST = "to_list"
        CC_LIST = "cc_list"
        TO_ASSIGNEE = "to_assignee"
        CC_MANAGER = "cc_manager"
        ADDI_INFO = "addi_info"

    class AddiConfig(Enum):
        TIME = "Time"
        REMARK = "Remark"
        ANALYSIS = "Analysis"
        TRACKING = "Tracking"
        COMMENTS = "Comments"

    class HtmlFieldMap:
        ID = "ID"
        CR_LINK = "cr_link"
        TITLE = "Title"
        PRIORITY = "Priority"
        CLASS = "Class"
        STATE = "State"
        ASSIGN_TEAM = "Assign Team"
        ASSIGNEE = "Assignee"
        ASSIGN = "Assign"
        ASSIGN_COUNT = "assign_count"
        REVIEW_COMMENTS = "Review Comments"
        ANALYSIS = "First-hand Analysis"
        REMARK = "Remark"
        IMPORTANCE = "Importance"
        WAR_ROOM = "WarRoom"
        PROGRESS = "Progress"
        ASSIGN_DEPT_LINK = "assign_dept_link"
        ASSIGNEE_LINK = "assginee_link"
