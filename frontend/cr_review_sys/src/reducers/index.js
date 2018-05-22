import {
  combineReducers
} from 'redux';
import * as actions from '../actions/index';
import {
  CR_VIEW,
  CR_ACTIVITY
} from '../constants';
import {
  activitiesReducer,
  activityCategoryReducer
} from './activity';
import {
  crListReducer,
  affectedCrListReducer,
  TeamCRCountReducer
} from './crlist';
import {
  userListReducer,
  loginUserReducer
} from './userlist';


function view(state = CR_VIEW.HOME, action) {
  switch (action.type) {
    case actions.SYS_EVENTS.VIEW_CHANGED:
      return action.view;
    default:
      return state;
  }
}

function db(state = [], action) {
  switch (action.type) {
    case actions.SYS_EVENTS.DB_CHANGED:
      return action.db;
    default:
      return state;
  }
}

function activity(state = CR_ACTIVITY.DEFAULT, action) {
  switch (action.type) {
    case actions.SYS_EVENTS.ACTIVITY_CHANGED:
      return action.activity;
    default:
      return state;
  }
}

function activitycategory(state = {}, action) {
  switch (action.type) {
    case actions.SYS_EVENTS.ACTIVITYCATEGORY_CHANGED:
      return action.current_category;
    default:
      return state;
  }
}

function keywordFilters(state = [], action) {
  switch (action.type) {
    case actions.SYS_EVENTS.KEYWORD_CHANGED:
      return action.keywordFilters;
    default:
      return state;
  }
}

function KeywordMergeType(state = '&', action) {
  switch (action.type) {
    case actions.SYS_EVENTS.KEYWORD_MERGE_TYPE_CHANGED:
      return action.KeywordMergeType;
    default:
      return state;
  }
}

function openDayMoreThan(state = '', action) {
  switch (action.type) {
    case actions.SYS_EVENTS.CR_OPEN_DAY_CHANGED:
      return action.crOpenDayInput;
    default:
      return state;
  }
}

function crInDays(state = '', action) {
  switch (action.type) {
    case actions.SYS_EVENTS.CR_IN_DAY_CHANGED:
      return action.crInDayInput;
    default:
      return state;
  }
}

function showAnalysisField(state = false, action) {
  switch (action.type) {
    case actions.SYS_EVENTS.SHOWANALYSISFIELDCLICK:
      return action.showAnalysisField;
    default:
      return state;
  }
}

function crTimeTracking(state = false, action) {
  switch (action.type) {
    case actions.SYS_EVENTS.SHOWTIMEFIELDCLICK:
      return action.crTimeTracking;
    default:
      return state;
  }
}

function showRemarkField(state = false, action) {
  switch (action.type) {
    case actions.SYS_EVENTS.SHOWREMARKFIELDCLICK:
      return action.showRemarkField;
    default:
      return state;
  }
}

function showMpTrackingField(state = false, action) {
  switch (action.type) {
    case actions.SYS_EVENTS.SHOWMPTRACKINGFIELDCLICK:
      return action.showMpTrackingField;
    default:
      return state;
  }
}

function crClassFilter(state = null, action) {
  switch (action.type) {
    case actions.SYS_EVENTS.CR_CLASS_FILTER_CHANGED:
      return action.classfilter;
    default:
      return state;
  }
}

function crStateFilter(state = null, action) {
  switch (action.type) {
    case actions.SYS_EVENTS.CR_STATE_FILTER_CHANGED:
      return action.statefilter;
    default:
      return state;
  }
}

function currCommentView(state = 'Append', action) {
  switch (action.type) {
    case actions.SYS_EVENTS.COMMENTVIEW_CHANGED:
      return action.currCommentView;
    default:
      return state;
  }
}

function currSelectedGroup(state = '', action) {
  switch (action.type) {
    case actions.SYS_EVENTS.FILTERGROUPCHANGED:
      return action.newGroup;
    default:
      return state;
  }
}

function currSelectedTeam(state = '', action) {
  switch (action.type) {
    case actions.SYS_EVENTS.FILTERTEAMCHANGED:
      return action.newTeam;
    default:
      return state;
  }
}

const crReviewReducer = combineReducers({
  currentDB: db,
  currentView: view,
  currentActivity: activity,
  activities: activitiesReducer,
  activityCategory: activityCategoryReducer,
  crlist: crListReducer,
  keywordFilters: keywordFilters,
  KeywordMergeType: KeywordMergeType,
  openDayMoreThan: openDayMoreThan,
  crInDays: crInDays,
  showAnalysisField: showAnalysisField,
  crTimeTracking: crTimeTracking,
  showRemarkField: showRemarkField,
  showMpTrackingField: showMpTrackingField,
  crClassFilter: crClassFilter,
  crStateFilter: crStateFilter,
  currCommentView: currCommentView,
  currGroup: currSelectedGroup,
  currTeam: currSelectedTeam,
  affectedCrList: affectedCrListReducer,
  teamCrCount: TeamCRCountReducer,
  allusers: userListReducer,
  currentActivityCategory: activitycategory,
  loginUser: loginUserReducer
});

export default crReviewReducer;