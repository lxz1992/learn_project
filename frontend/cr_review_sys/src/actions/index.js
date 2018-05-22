import {
    CR_VIEW,
    CR_DB
} from '../constants';

/*
 * action type:
 * manage the events in the central.
 */

const SYS_EVENTS = {
    VIEW_CHANGED: "VIEW_CHANGED",
    DB_CHANGED: "DB_CHANGED",
    ACTIVITY_CHANGED: "ACTIVITY_CHANGED",
    ACTIOON_LIST_REQ: "ACTIOON_LIST_REQ",
    ACTIOON_LIST_RESP: "ACTION_LIST_RESP",
    KEYWORD_CHANGED: "KEYWORD_CHANGED",
    KEYWORD_MERGE_TYPE_CHANGED: "KEYWORD_MERGE_TYPE_CHANGED",
    SHOWANALYSISFIELDCLICK: "SHOWANALYSISFIELDCLICK",
    SHOWTIMEFIELDCLICK: 'SHOWTIMEFIELDCLICK',
    SHOWREMARKFIELDCLICK: 'SHOWREMARKFIELDCLICK',
    SHOWMPTRACKINGFIELDCLICK: 'SHOWMPTRACKINGFIELDCLICK',
    CR_OPEN_DAY_CHANGED: "CR_OPEN_DAY_CHANGED",
    CR_IN_DAY_CHANGED: "CR_IN_DAY_CHANGED",
    CR_CLASS_FILTER_CHANGED: 'CR_CLASS_FILTER_CHANGED',
    CR_STATE_FILTER_CHANGED: 'CR_STATE_FILTER_CHANGED',
    COMMENTVIEW_CHANGED: 'COMMENTVIEW_CHANGED',
    CR_LIST_REQ: 'CR_LIST_REQ',
    CR_LIST_RESP: 'CR_LIST_RESP',
    FILTERGROUPCHANGED: 'FILTERGROUPCHANGED',
    FILTERTEAMCHANGED: 'FILTERTEAMCHANGED',
    AFFECTEDCRLIST: 'AFFECTEDCRLIST',
    TEAMCRCOUNT: 'TEAMCRCOUNT',
    USER_LIST_REQ: "USER_LIST_REQ",
    USER_LIST_RESP: "USER_LIST_RESP",
    ACTIVITYCATEGORY_LIST_REQ: "ACTIVITYCATEGORY_LIST_REQ",
    ACTIVITYCATEGORY_LIST_RESP: "ACTIVITYCATEGORY_LIST_RESP",
    ACTIVITYCATEGORY_CHANGED: "ACTIVITYCATEGORY_CHANGED",
    CURRENTUSER_LIST_REQ: "CURRENTUSER_LIST_REQ",
    CURRENTUSER_LIST_RESP: "CURRENTUSER_LIST_RESP"
};


/*
 * action creator:
 * for simple actions only, if the actions are complicate, please use another file to implement
 */

function onViewChanged(view = CR_VIEW.HOME) {
    return {
        type: SYS_EVENTS.VIEW_CHANGED,
        view
    };
}

function onDBChanged(db = []) {
    return {
        type: SYS_EVENTS.DB_CHANGED,
        db
    };
}

function onActivityChanged(activity) {
    return {
        type: SYS_EVENTS.ACTIVITY_CHANGED,
        activity
    };
}

function onCurrCategoryChanged(curr_cat, default_act, cat_name) {
    let current_category = {
        category_id: curr_cat,
        default_activity: default_act,
        activity_cat_name: cat_name
    };
    return {
        type: SYS_EVENTS.ACTIVITYCATEGORY_CHANGED,
        current_category
    };
}

export {
    SYS_EVENTS,
    onViewChanged,
    onDBChanged,
    onActivityChanged,
    CR_VIEW,
    CR_DB,
    onCurrCategoryChanged
};