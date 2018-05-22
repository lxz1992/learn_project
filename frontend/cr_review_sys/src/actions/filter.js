import {
    GV
} from '../constants';
import {
    SYS_EVENTS
} from './index';

/*
 * action creator:
 * for filter action
 */


function onKeywordChanged(keywordFilters = []) {
    return {
        type: SYS_EVENTS.KEYWORD_CHANGED,
        keywordFilters
    };
}

function onKeywordMergeTypeChanged(KeywordMergeType = GV.keywordFilterCombinedType) {
    return {
        type: SYS_EVENTS.KEYWORD_MERGE_TYPE_CHANGED,
        KeywordMergeType
    };
}

function oncrOpenDayChanged(crOpenDayInput = '') {
    return {
        type: SYS_EVENTS.CR_OPEN_DAY_CHANGED,
        crOpenDayInput
    };
}

function oncrInDayChanged(crInDayInput = '') {
    return {
        type: SYS_EVENTS.CR_IN_DAY_CHANGED,
        crInDayInput
    };
}

function setCrClassFilter(curview, curactivity) {
    let classfilter = {
        'Bug': 1,
        'New feature': 1,
        'Change feature': 1,
        'Question': 1,
        'Others': 1
    };
    if (curactivity.indexOf('_Bug') >= 0) {
        classfilter = {
            'Bug': 1
        };
    } else if (curactivity.indexOf('_NonBug') >= 0) {
        classfilter = {
            'New feature': 1,
            'Change feature': 1,
            'Question': 1,
            'Others': 1
        };
    } else if ((curactivity.indexOf('Check-in') >= 0) | (curactivity.indexOf('Patch') >= 0)) {
        classfilter = {
            'Bug': 1,
            'New feature': 1,
            'Change feature': 1
        };
    }

    return {
        type: SYS_EVENTS.CR_CLASS_FILTER_CHANGED,
        classfilter
    };

}

function setCrStateFilter(curview, curactivity) {
    let statefilter = {
        'Submitted': 1,
        'Assigned': 1,
        'Working': 1,
        'Reworking': 1,
        'Resolved': 0,
        'Verified': 0,
        'Closed': 0
    };
    if ((curview === 'CR List') || (curview === 'Home')) {
        statefilter = {
            'Submitted': 1,
            'Assigned': 1,
            'Working': 1,
            'Reworking': 1,
            'Resolved': 1,
            'Verified': 1,
            'Closed': 1
        };
    }
    if ((curactivity.indexOf('Check-in') >= 0) | (curactivity.indexOf('Patch') >= 0)) {
        statefilter = {
            'Submitted': 0,
            'Assigned': 0,
            'Working': 0,
            'Reworking': 0,
            'Resolved': 1,
            'Verified': 1,
            'Closed': 1
        };
    }

    return {
        type: SYS_EVENTS.CR_STATE_FILTER_CHANGED,
        statefilter
    };
}

function setMPTrackingFiled(activity) {
    let showMpTrackingField = false;
    if (activity.indexOf('_MP') > 0) {
        showMpTrackingField = true;
    }
    return {
        type: SYS_EVENTS.SHOWMPTRACKINGFIELDCLICK,
        showMpTrackingField
    };
}

function setCommentView(activity) {
    let currCommentView = 'Append';
    if (activity.indexOf('_MP') > 0) {
        currCommentView = 'Inline';
    }
    return {
        type: SYS_EVENTS.COMMENTVIEW_CHANGED,
        currCommentView
    };
}

function oncrClassChanged(classfilter) {
    return {
        type: SYS_EVENTS.CR_CLASS_FILTER_CHANGED,
        classfilter
    };
}

function oncrStateChanged(statefilter) {
    return {
        type: SYS_EVENTS.CR_STATE_FILTER_CHANGED,
        statefilter
    };
}

function onCommentViewChanged(currCommentView) {
    return {
        type: SYS_EVENTS.COMMENTVIEW_CHANGED,
        currCommentView
    };
}

function oncrTimeTrackingChanged(crTimeTracking) {
    return {
        type: SYS_EVENTS.SHOWTIMEFIELDCLICK,
        crTimeTracking
    };
}

function onshowRemarkFieldChanged(showRemarkField) {
    return {
        type: SYS_EVENTS.SHOWREMARKFIELDCLICK,
        showRemarkField
    };
}

function onshowMpTrackingFieldChanged(showMpTrackingField) {
    return {
        type: SYS_EVENTS.SHOWMPTRACKINGFIELDCLICK,
        showMpTrackingField
    };
}

function onshowAnalysisFieldChanged(showAnalysisField) {
    return {
        type: SYS_EVENTS.SHOWANALYSISFIELDCLICK,
        showAnalysisField
    };
}

function onFilterGroupChanged(newGroup) {
    return {
        type: SYS_EVENTS.FILTERGROUPCHANGED,
        newGroup: newGroup
    };
}

function onFilterTeamChanged(newTeam) {
    return {
        type: SYS_EVENTS.FILTERTEAMCHANGED,
        newTeam: newTeam
    };
}

export {
    onKeywordChanged,
    onKeywordMergeTypeChanged,
    oncrOpenDayChanged,
    oncrInDayChanged,
    setCrClassFilter,
    setCrStateFilter,
    setMPTrackingFiled,
    setCommentView,
    oncrClassChanged,
    oncrStateChanged,
    onCommentViewChanged,
    oncrTimeTrackingChanged,
    onshowRemarkFieldChanged,
    onshowMpTrackingFieldChanged,
    onshowAnalysisFieldChanged,
    onFilterGroupChanged,
    onFilterTeamChanged
};