import cmnUtils from './util/index';

const CR_VIEW = {
    HOME: "Home",
    CR_LIST: "CR List",
    CR_Review: "CR Review",
    WAIVED_CR: "Waived CR",
    CR_NOTIFY: "CR Notify",
};

const CR_DB = {
    MOLY: "MOLY",
    ALPS: "ALPS",
    MOLY_ALPS: "MOLY_ALPS"
};

const CR_ACTIVITY = {
    DEFAULT: "default-activity"
};

let URL_STORE = ((cmnUtils.isProd()) ? {
    CR_REVIEW: {
        ACTIVITY: `/cr_review/api/activity/`,
        ACTIVITYCATEGORY: `/cr_review/api/activity_category/?act_cat_type=${encodeURIComponent("CR Review")}`,
        ALLCR: '/cr_review/api/cr_by_activity/',
        ACTIVITY_CONFIG: '/cr_review/api/activity/',
        USER_LIST: '/cr_review/api/users/',
        ADMIN_CONFIG_SUBMIT: '/cr_review/api/submit_act_config/',
        CR_REVIEW_SUBMIT: '/cr_review/api/submit_review_info/',
        CR_REVIEW_INFO: '/cr_review/api/cr_review_info/',
        CR_REVIEW_COMMENT: '/cr_review/api/cr_review_comments/',
        LOGIN_USER_INFO: '/me/'
    }
} : {
    CR_REVIEW: {
        ACTIVITY: `/cr_review_sys/resources/json/activity_info.json`,
        ACTIVITYCATEGORY: '/cr_review_sys/resources/json/activity_category_info.json',
        ALLCR: '/cr_review_sys/resources/json/alps_all_cr.json',
        ACTIVITY_CONFIG: '/cr_review_sys/resources/json/activity_config.json',
        USER_LIST: '/cr_review_sys/resources/json/user_list.json',
        ADMIN_CONFIG_SUBMIT: '/cr_review_sys/resources/submit.py',
        CR_REVIEW_SUBMIT: '/cr_review/api/cr_review/',
        CR_REVIEW_INFO: '/cr_review_sys/resources/json/cr_review_info.json',
        CR_REVIEW_COMMENT: '/cr_review_sys/resources/json/cr_review_comment.json',
        LOGIN_USER_INFO: '/cr_review_sys/resources/json/login.json'
    }
});

const COLOR = {
    MTK_WHITE: 'white',
    MTK_GRAY: '#999999',
    MTK_RED: '#aa7777',
    MTK_GREEN: '#77aa77',
    MTK_DARK_GREEN: '#669966',
    MTK_ORANGE: '#ff8855',
    MTK_LIGHT_ORANGE: '#ffccaa',
    MTK_GRAY_RED: '#a42d00',
    MTK_LIGHT_RED: '#ff8888',
    MTK_LIGHT_BLUE: '#66aaff',
    MTK_LIGHT_ORANGE2: '#ffddcc', //remark
    MTK_LIGHT_YELLOW: '#f7e1c1', //analysis
    MTK_LIGHT_YELLOW2: '#f7e1c1', //analysis
    MTK_LIGHT_RED2: '#ff8888',
    MTK_LIGHT_BLUE2: '#ccddff' //tracking
};

const CONFIG_ADDITIONAL_LIST = {
    Time: 'time',
    Analysis: 'analysis',
    Tracking: 'tracking',
    Remark: 'remark',
    Comments: 'comments',
    Others: 'others'
};

const VIEWHINT = {
    'Home': '<b>Home - </b> CR Statistics for selected activity.',
    'CR List': '<b>CR List - </b> Customize your CR display format.',
    'CR Review': '<b>CR Review - </b> Hold a CR review meeting to update comments. (exclude waived CR)',
    'Waived CR': '<b>Waived CR - </b> Exclude these CR from review list.',
    'CR Notify': '<b>CR Notify - </b> Send daily CR notify mail. (also exclude waived CR)'
};

const GV = {
    wePeopleFinderPage: 'http://peoplefinder.mediatek.inc/PeopleFinder/Home/Detail/',
    wePeopleFinderKeywordPage: 'http://peoplefinder.mediatek.inc/PeopleFinder/Home/SearchResult/ViewByCategories?keyword=',
    maxAssignDays: {
        'Bug': 3,
        'Others': 7
    },
    webCqLink: {
        'MOLY': 'http://mtkcqweb.mediatek.inc/mtkcqweb_WCX_FeaturePhone_MOLY/mtk/sec/cr/cr_view.jsp?crId=',
        'ALPS': 'http://mtkcqweb.mediatek.inc/mtkcqweb_WCX_SmartPhone_ALPS/mtk/sec/cr/cr_view.jsp?crId='
    },
    showField: {
        'CR List': ['id', 'Title', 'Priority', 'Class', 'State', 'User_Field3', 'Source', 'Submitter.fullname', 'Submit_Date', 'Open_Days',
            'Assignee_Dept', 'Assignee_Name', 'Dispatch_Count', 'Assign_Date', 'Assign_Days', 'Resolve_Date', 'Resolve_Days', 'Resolution', 'Solution_Category_Level1', 'Bug_Reason'
        ],
        'CR Review': ['id', 'Title', 'Priority', 'Class', 'User_Field3', 'Assignee_Dept', 'Assignee_Name', 'Submit_Date', 'Assign_Date', 'Dispatch_Count', 'Waived', 'Comment'],
        'Waived CR': ['id', 'Title', 'Priority', 'Class', 'User_Field3', 'Assignee_Dept', 'Assignee_Name', 'Submit_Date', 'Assign_Date', 'Dispatch_Count', 'Waived', 'Comment'],
        'CR Notify': ['id', 'Title', 'Priority', 'Class', 'State', 'Assignee_Dept', 'Assignee_Name', 'Open_Days', 'Assign_Date','Assign_Days', 'Comment']
    },
    fieldColumn: {
        'id': 0,
        'Title': 1,
        'Priority': 2,
        'Class': 3,
        'State': 4,
        'User_Field3': 5,
        'Source': 6,
        'Submitter.fullname': 7,
        'Submit_Date': 8,
        'Open_Days': 9,
        'Submit_DateTimeNum': 10,
        'Assignee_Dept': 11,
        'Assignee_Name': 12,
        'Dispatch_Count': 13,
        'Assign_Date': 14,
        'Assign_Days': 15,
        'Assign_DateTimeNum': 16,
        'Resolve_Date': 17,
        'Resolve_Days': 18,
        'Resolve_DateTimeNum': 19,
        'Resolution': 20,
        'Solution_Category_Level1': 21,
        'Bug_Reason': 22,
        'Waived': 23,
        'Importance': 24,
        'WarRoom': 25,
        'Progress': 26,
        'Analysis': 27,
        'Remark': 28,
        'Comment': 29
    },
    fieldMap: {
        'Submit_DateTime': 'submit_date',
        'State': 'state',
        'Assignee_Dept': 'assignee_dept',
        'Resolve_Time': 'resolve_time',
        'Title': 'title',
        'id': 'cr_id',
        'Class': 'cr_class',
        'Assign_DateTime': 'assign_date',
        'Bug_Reason': 'bug_reason',
        'Solution_Category_Level1': 'solution_category_level1',
        'Resolve_DateTime': 'resolve_date',
        'User_Field3': 'local_issue',
        //"Submitter": "Justin Oommen",
        'Submitter.fullname': 'submitter',
        'Resolution': 'resolution',
        'Priority': 'priority',
        'Source': 'cr_source',
        'Dispatch_Count': 'dispatch_count',
        'Assignee_Name': 'assignee',
        'Waived': 'waived',
        'Importance': 'importance',
        'WarRoom': 'warRoom',
        'Progress': 'progress',
        'Analysis': 'analysis',
        'Remark': 'remark',
        'Comment': 'comments'
    },
    fieldRename: {
        'id': 'ID',
        'Assign_Date': 'Assign',
        'Submit_Date': 'Submit',
        'Dispatch_Count': 'Dispatch Count',
        'Resolve_Date': 'Resolve',
        'Assignee_Dept': 'Assign Team',
        'Assignee_Name': 'Assignee',
        'User_Field3': 'Local Issue',
        'Submitter.fullname': 'Submitter',
        'Solution_Category_Level1': 'Issue',
        'Bug_Reason': 'Reason',
        'Coworkers.fullname': 'Coworker',
        'Change_Log.Who.fullname': 'Action RD',
        'Change_Log.Old_Value': 'From',
        'Change_Log.New_Value': 'To',
        'Change_Log.When': 'When',
        'Note_List.Who.fullname': 'Note RD',
        'Copy_Crs': 'Copy From',
        'zip_cnt': 'zip',
        'muxz_cnt': 'muxz',
        'muxz_dir_cnt': 'muxdir',
        'elg_cnt': 'elg',
        'ppat_cnt': 'ppat',
        'err': 'Error Info',
        'Assign_DateTimeNum': 'Assign Time',
        'Submit_DateTimeNum': 'Submit Time',
        'Resolve_DateTimeNum': 'Resolve Time',
        'Open_Days': 'Open Days',
        'Resolve_Days': 'Resolve Days',
        'Assign_Days': 'Assign Days'
    },

    fieldAllowSorting: {
        'ID': '',
        'Priority': '',
        'Class': '',
        'State': '',
        'Local Issue': '',
        'Source': '',
        'Submitter': '',
        'Assign Team': '',
        'Assignee': '',
        'Submit': '',
        'Assign': '',
        'Resolve': '',
        'Resolution': '',
        'Issue': '',
        'Reason': '',
        'Dispatch Count': '',
        'To': '',
        'Test Category': ''
    },
    crDaysMap: {
        'submit_date': 'Open_Days',
        'assign_date': 'Assign_Days',
        'resolve_date': 'Resolve_Days'
    },
    crDateMap: {
        'submit_date': 'Submit_Date',
        'assign_date': 'Assign_Date',
        'resolve_date': 'Resolve_Date'
    },
    keywordFilterCombinedType: '&', // '&'(AND) or '+'(OR)
    crTimeTrackingField: {
        'SubmitTime': 'Submit_DateTimeNum',
        'AssignTime': 'Assign_DateTimeNum'
    },
    highlightRuleJson: 'highlight_rule.json',
    enableHighlight: true,
    crStatisticFieldHash: {
        'Submit_Date': '',
        'Resolve_Date': '',
        'Verify_Date': '',
        'Close_Date': '',
        'Effective Check-in': ''
    },
    resolutionList: ['Completed', 'Rejected', 'Duplicated', 'Not reproducible'],
    openStateList: ['Assigned', 'Working', 'Reworking', 'Submitted'],
    crFieldList: {
        'State': ['Submitted', 'Assigned', 'Working', 'Reworking', 'Resolved', 'Verified', 'Closed'],
        'Class': ['Bug', 'New feature', 'Change feature', 'Question', 'Others']
    },
    classHash: {
        'Bug': '',
        'New feature': '',
        'Change feature': '',
        'Question': ''
    },
    groupKeywordHash: {
        'MD': ['_se', '_sd', 'csd_', 'cnopd', 'sse', 'msp'],
        'AP': ['acf_', '_oss', 'hsd'],
        'SV': ['sv_', '_sqa']
    }

};

const REDUCER_NAME = {
    currentDB: 'currentDB',
    currentView: 'currentView',
    currentActivity: 'currentActivity',
    activities: 'activities',
    crlist: 'crlist',
    keywordFilters: 'keywordFilters',
    KeywordMergeType: 'KeywordMergeType',
    openDayMoreThan: 'openDayMoreThan',
    crInDays: 'crInDays',
    showAnalysisField: 'showAnalysisField',
    crTimeTracking: 'crTimeTracking',
    showRemarkField: 'showRemarkField',
    showMpTrackingField: 'showMpTrackingField',
    crClassFilter: 'crClassFilter',
    crStateFilter: 'crStateFilter',
    currCommentView: 'currCommentView',
    currGroup: 'currGroup',
    currTeam: 'currTeam',
    affectedCrList: 'affectedCrList',
    teamCrCount: 'teamCrCount',
    activityCategory: 'activityCategory',
    currentActivityCategory: 'currentActivityCategory'
};

const CRTRACKINGOPTION = {
    importance: {
        '': '',
        'P0': 'Critical',
        'P1': 'High',
        'P2': 'Medium',
        'P3': 'Low'
    },
    warroom: {
        '': '',
        'W1': 'War Room',
        'W2': 'Virtual War Room'
    },
    progress: {
        '': '',
        'PG0': 'To be analyzed',
        'PG1': 'Reproducing',
        'PG2': 'Analyzing',
        'PG3': 'High dispatch count',
        'PG4': 'Test environment check',
        'PG5': 'Resolving',
        'PG6': 'Verifying',
        'PG7': 'Duplicate',
        'PG8': 'High risk known issue',
        'PG9': 'Others'
    }
};


export {
    CR_VIEW,
    CR_DB,
    CR_ACTIVITY,
    URL_STORE,
    COLOR,
    GV,
    REDUCER_NAME,
    CONFIG_ADDITIONAL_LIST,
    VIEWHINT,
    CRTRACKINGOPTION
};