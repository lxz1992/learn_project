'''
Created on Dec 18, 2017

@author: claire
'''
from enum import Enum

BULK_BATCH_SIZE = 500
REPORT_BULK_BATCH_SIZE = 1000

# primitive types
LOG_TRACE_LVL = 5


class MdMeta:
    ActivityId = 3
    Delimit = "%%"
    MEATop10 = "MEA top 10"
    OpCountryType = "Country"
    Group = ("wcs_se2", "wcs_se3", "wcs_sd", "wct_msp", "wcs_mdd",
             "wcs_sse", "wcs_st", "wsp_se7", "wcs_se8", "wsd_oss8_me9",
             "wct_se1_se9", "wsp_msd", "wsp_cnopd1_pss2", 'msz_wsp_sv_mcs1',
             'mshc_wsp_sv_mcs2', 'mshc_wsp_sv_mcs3', 'mti_wsp_sv_gmcs',
             'wsp_sv_msv', 'wsp_mce_mce1', 'mkr_wsp_mce_mce2')


class MdPrjStatus:
    ONGOING = "ongoing"
    NEW = "new"
    INCOMING = "incoming"
    DIS_YEARLY = "year"
    COMPLETED = "1"
    NOTCOMPLETED = "0"


class MdState:

    class Open(Enum):
        Submitted = "Submitted"
        Assigned = "Assigned"
        Working = "Working"
        Reworking = "Reworking"

    class Resolved(Enum):
        Closed = "Closed"
        Resolved = "Resolved"
        Verified = "Verified"

    class Submit(Enum):
        Submitted = "Submitted"
        Assigned = "Assigned"
        Working = "Working"
        Reworking = "Reworking"
        Closed = "Closed"
        Resolved = "Resolved"
        Verified = "Verified"


class ValidCrType:
    map_cr = ("state", "from_year", "to_year", "country")
    urgent_cr = ("operator",)
    ces_country_cr = ("country",)
    ces_group_cr = ("group",)


class MdHwPrjType:
    '''
    There are two hw type for operator certification/FTA use
    '''
    Operator = "Operator"
    FTA = "FTA"

    class OperatorCategory:
        OPTR = "OPTR Entry"
        TYPE = "OPTR"

    class FTAType:
        GCF = "Lab Test (GCF)"
        PTCRB = "Lab Test (PTCRB)"


class MdCrFieldMap:
    CR_ID = "CR_ID"
    SUBMIT_DATE = "SUBMIT_DATE"
    PRIORITY = "PRIORITY"
    CUSTOMER = "CUSTOMER"
    COUNTRY = "MD_INFO_COUNTRY"
    OPERATOR = "MD_INFO_OP_NAME"
    STATE = "STATE"
    CR_CLASS = "CR_CLASS"
    RESOLUTION = "RESOLUTION"
    ASSIGNEE_DEPT = "ASSIGNEE_DEPT"
    RESOLVE_TIME = "RESOLVE_TIME"
    ASSIGNEE = "ASSIGNEE"
    WW_COUNTRY = "COUNTRY"
    WW_OPERATOR = "OPERATOR"
    RESOLVE_DATE = "RESOLVE_DATE"


class WwStatisticTop10Type:
    Operator = "Operator"
    Customer = "Customer"
    Country = "Country"


class WwStatisticTop10:
    class DbFieldMap:
        ID = "id"
        ACT_ID = "activity_id"
        SYNC_ID = "sync_job_id"
        PERIOD = "period"
        TYPE = "type"
        TYPE_VALUE = "type_value"
        PRIORITY = "priority"
        CR_COUNT = "cr_count"


class WwStaMap:
    URGENT_CR_KEY = "Urgent"

    class DbFieldMap:
        ID = "id"
        ACT_ID = "activity_id"
        SYNC_ID = "sync_job_id"
        STATE = "state"
        PERIOD = "period"
        COUNTRY = "country"
        OPERATOR = "operator"
        MD_CLASS = "md_class"
        CR_COUNT = "cr_count"
        URGENT_COUNT = "urgent_cr_count"


class ResolvedEs:
    class DbFieldMap:
        ID = "id"
        ACT_ID = "activity_id"
        SYNC_ID = "sync_job_id"
        TYPE = "type"
        SITE = "assignee_site"
        CUSTOMER = "customer_company"
        PERIOD = "period"
        PRIORITY = "priority"
        CR_COUNT = "cr_count"
        RESOLVE_TIME_COUNT = "resolve_time_count"

    class Period:
        YEAR = "Year"
        MONTH = "Month"
        WEEK = "Week"


class OpenEs:
    class DbFieldMap:
        ID = "id"
        ACT_ID = "activity_id"
        SYNC_ID = "sync_job_id"
        SITE = "assignee_site"
        CUSTOMER = "customer_company"
        STAY = "stay_submitted"
        PRIORITY = "priority"
        CR_COUNT = "cr_count"


class Ces:
    GROUP = "Operator"
    OTHERS = "others"

    class DbFieldMap:
        ID = "id"
        ACT_ID = "activity_id"
        SYNC_ID = "sync_job_id"
        COUNTRY = "country"
        OPERATOR = "operator"
        PRIORITY = "priority"
        CR_COUNT = "cr_count"


class CrmHwPrj:
    class DbFieldMap:
        ID = "id"
        HW_PRJ_ID = "hw_prj_id"
        HW_TYPE = "hw_type"
        OPERATOR = "operator"
        IS_COMPLETED = "is_completed"
        PLATFORM = "platform"
        COMPANY = "company"
        START_DATE = "start_date"
        END_DATE = "end_date"


class OpCert:
    class DbFieldMap:
        ID = "id"
        ACT_ID = "activity_id"
        SYNC_ID = "sync_job_id"
        OPERATOR = "operator"
        AREA = "area"
        IS_COMPLETED = "is_completed"
        PLATFORM = "platform"
        COMPANY = "company"
        PERIOD_YEAR = "period_year"
        PERIOD_WEEK = "period_week"
        PROJECT_COUNT = "project_count"
        WILL_KICKOFF_PROJECT_COUNT = "will_kickoff_project_count"
        URGENT_CR_COUNT = "urgent_cr_count"


class FTA:
    class DbFieldMap:
        ID = "id"
        ACT_ID = "activity_id"
        SYNC_ID = "sync_job_id"
        OPERATOR = "operator"
        AREA = "area"
        IS_COMPLETED = "is_completed"
        PLATFORM = "platform"
        COMPANY = "company"
        PERIOD_YEAR = "period_year"
        PERIOD_WEEK = "period_week"
        PROJECT_COUNT = "project_count"
        WILL_KICKOFF_PROJECT_COUNT = "will_kickoff_project_count"
        URGENT_CR_COUNT = "urgent_cr_count"
