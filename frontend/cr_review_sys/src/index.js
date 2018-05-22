import '../../node_modules/bootstrap/dist/css/bootstrap.min.css';
import '../../node_modules/highcharts/css/highcharts.css';
import '../../lib/font-awesome-4.7.0/css/font-awesome.min.css';
import '../../node_modules/datatables.net-dt/css/jquery.dataTables.css';
import 'jquery';
import 'bootstrap';
import '../resources/css/cr_review.scss';
import store from './store';
import {
    fetchActivities,
    fetchActivityCategory
} from './actions/activity';
import '../lib/boot-side-menu-1.0.0/BootSideMenu';
import './listener/listener';
import {
    loadFilterSort
} from './show/loadFilterSort';
import {
    refreshPage
} from './data/datasource';
import isEqual from 'is-equal';
import watch from 'redux-watch';
import {
    REDUCER_NAME,
    VIEWHINT
} from './constants';
import {
    onActivityChanged,
    onDBChanged,
    onCurrCategoryChanged
} from './actions/index';
import {
    setCrStateFilter,
    setCrClassFilter,
    setMPTrackingFiled,
} from './actions/filter';
import {
    fetchActivityCrs,
    onCrlistChanged,
    onTeamCountChanged
} from './actions/crlist';
import {
    refreshGroupTeamFilter
} from './show/loadFilterSort';
import {
    fetchUserList,
    fetchLoginUser
} from './actions/userlist';
import {
    parseAffectedCrInformation
} from './data/parsecrdata';

const jq = jQuery.noConflict();
let prevMsg = "";

jq(document).ready((e) => {
    //store.dispatch(fetchActivities(jq));
    store.dispatch(fetchActivityCategory());
    store.dispatch(fetchUserList());
    store.dispatch(fetchLoginUser());
    jq('.cr-sidebar').BootSideMenu({
        side: 'left',
        pushBody: false,
        width: '360px'
    });
    loadContentPage('Home');
});

function updateViewOption(newVal) {
    loadContentPage(newVal);
    console.log('view change to:' + newVal);
    let state = store.getState();
    let activity = state.currentActivity;
    store.dispatch(setCrClassFilter(newVal, activity));
    store.dispatch(setCrStateFilter(newVal, activity));
    loadFilterSort();
    updateAffectedCrlist(newVal);
    refreshPage();
}

function updateDBOption(newVal, oldVal) {
    let viewId = 'curDB';
    oldVal.forEach((val) => {
        jq(`li[data-toggle="${viewId}"][data-title="${val}"]`).removeClass('active').addClass('notActive');
    });
    newVal.forEach((val) => {
        jq(`#${viewId}`).prop('value', val);
        jq(`li[data-toggle="${viewId}"][data-title="${val}"]`).removeClass('notActive').addClass('active');
    });
}

function updateActivityList(activities) {
    let state = store.getState();
    //console.log("currentActivity ===>" + JSON.stringify(state.currentActivity));
    if ((state.currentActivity === 'default-activity') || (state.currentActivity === '')) {
        store.dispatch(onActivityChanged(activities["default"]));
    }
    if (activities["code"] && prevMsg !== activities["message"]) {
        jq("#errorModal").modal();
    } else {
        let subMenuActivity = "";
        let subMenuConfigActivity = "";
        jq(".cr-sidebar #activity-list #ongoing-list").html('');
        jq(".cr-sidebar #activity-list #finished-list").html('');
        jq(".cr-sidebar #config-list #configongoing-list").html('');
        jq(".cr-sidebar #config-list #configfinished-list").html('');
        activities["onGoing"].forEach((val) => {
            let id = activities["detail"][val]['activity_id'];
            subMenuActivity += `<a href="#${val}" data-value="${id}" class="list-group-item activity-item">${val}</a>`;
            subMenuConfigActivity += `<a href="#${val}" data-value="${id}" class="list-group-item config-activity-item">${val}</a>`;
        });

        let subMenuFinished = "";
        let subMenuConfigFinished = "";
        activities["finished"].forEach((val) => {
            let id = activities["detail"][val]['activity_id'];
            subMenuFinished += `<a href="#${val}" data-value="${id}" class="list-group-item activity-item">${val}</a>`;
            subMenuConfigFinished += `<a href="#${val}" data-value="${id}" class="list-group-item config-activity-item">${val}</a>`;
        });
        jq(".cr-sidebar #activity-list #ongoing-list").append(subMenuActivity);
        jq(".cr-sidebar #activity-list #finished-list").append(subMenuFinished);
        jq(".cr-sidebar #config-list #configongoing-list").append(subMenuConfigActivity);
        jq(".cr-sidebar #config-list #configfinished-list").append(subMenuConfigFinished);
    }
    prevMsg = activities['message'];
    let view = state.currentView;
    if (((view === 'Home') || (view === 'CR Notify')) && (state.crlist.ready)) {
        updateGraph();
    }
    
    //jq('.cr-content-title .cr-review-home-title-update-time .cr-review-update-time').text(activities["updatedAt"]);
}

function loadContentPage(curView) {
    jq('.cr-review-content-home').hide();
    jq('.cr-review-content-list').hide();
    jq('#activity-config-div').hide();
    if (curView === 'Home') {
        jq('.cr-review-content-home').show();
    } else {
        jq('.cr-review-content-list').show();
    }
    let viewhint = VIEWHINT[curView];
    jq('#viewHint').html(viewhint);
    let sel = curView;
    let viewId = 'curView';

    jq(`#${viewId}`).prop('value', sel);
    jq(`li[data-toggle="${viewId}"]`).not(`[data-title="${sel}"]`).removeClass('active').addClass('notActive');
    jq(`li[data-toggle="${viewId}"][data-title="${sel}"]`).removeClass('notActive').addClass('active');
}

function refreshDBScope(state) {
    let curActivity = state.currentActivity;
    let act_detail = state.activities.detail[curActivity];
    let actQueryDefine = '{"ALPS":""}';
    if ((act_detail !== undefined) && (act_detail.db_scope !== '')) {
        actQueryDefine = act_detail.db_scope;
    }
    if (typeof (actQueryDefine) === 'string') {
        try {
            actQueryDefine = JSON.parse(actQueryDefine);
        } catch (err) {
            alert("db_scope type error: " + err + '\n' + actQueryDefine);
            return;
        }

    }
    let all_cqdb = [];
    let htmlStr = '';
    jq('#review-dbscope').html(htmlStr);
    if (typeof (actQueryDefine) === 'object') {
        for (let cqdb in actQueryDefine) {
            all_cqdb.push(cqdb);
            htmlStr += `<li class="cr-topmenu-item cr-review-dbscope" data-toggle="curDB" data-title="${cqdb}"> <a href="#"> <span class="fa fa-database"></span>${cqdb}</a> </li>`;
        }
        jq('#review-dbscope').html(htmlStr);
        all_cqdb.forEach((val) => {
            jq(`#curDB`).prop('value', val);
            jq(`li[data-toggle="curDB"][data-title="${val}"]`).removeClass('notActive').addClass('active');
        });
        store.dispatch(onDBChanged(all_cqdb));
    } else {
        alert('the db_scope for this activity is not follow right spec:' + actQueryDefine);
    }

    jq('.cr-review-dbscope').click((e) => {
        let self = e.currentTarget;
        let title = jq(self).data('title');
        state = store.getState();
        let currDB = state.currentDB;
        let newDB = [];
        let findinDB = 0;
        currDB.forEach((val) => {
            if (val !== title) {
                newDB.push(val);
            } else {
                findinDB = 1;
            }
        });
        if (!findinDB) {
            newDB.push(title);
        }
        store.dispatch(onDBChanged(newDB));
        let activity_name = state.currentActivity;
        let id = state.activities.detail[activity_name].activity_id;
        store.dispatch(fetchActivityCrs(id, newDB));
    });
}

function updateForActivity(newVal) {
    //console.log('current activity');
    //console.log(newVal);
    jq('.cr-content-title .cr-review-home-title-activity .cr-review-activity').text(newVal);
    let state = store.getState();
    let curview = state.currentView;
    store.dispatch(setCrClassFilter(curview, newVal));
    store.dispatch(setCrStateFilter(curview, newVal));
    store.dispatch(setMPTrackingFiled(newVal));
    refreshDBScope(state);
    //store.dispatch(setCommentView(newVal));
    let id = 0;
    let date_from = null;
    if (newVal !== '') {
        id = state.activities.detail[newVal].activity_id;
        date_from = state.activities.detail[newVal].date_from;
    }
    store.dispatch(fetchActivityCrs(id, state.currentDB));
    loadFilterSort();
    jq('.cr-content-title .cr-review-home-title-update-time .cr-review-activity-start-date').text(date_from);
}

function updateAffectedCrlist(newVal) {
    let state = store.getState();
    //store.dispatch(onCrlistChanged(state));
    let crlist = state.crlist;
    //crlist is fetched, not in default state, or datatable maybe recive wrong data
    if ((!crlist.isFetching) && (!(crlist.cr.hasOwnProperty('default-state')))) {
        parseAffectedCrInformation(state);
    }
}

function updateGraph(newVal) {
    console.log('refresh graph....');
    refreshPage();
}

function onGroupChanged(newVal) {
    refreshGroupTeamFilter();
    updateAffectedCrlist();
}

function onCategoryChanged(newVal) {
    if (!newVal.isFetching) {
        let cat_detail = newVal.detail;
        let curr_cat = '';
        let default_act = '';
        let htmlStr = '';
        let cat_name = '';
        let state = store.getState();
        if((state.currentActivityCategory.activity_cat_name === undefined) || (state.currentActivityCategory.activity_cat_name === '')){
            jq('#review-category').html('');
            for (let item in cat_detail) {
                if (curr_cat === '') {
                    curr_cat = item;
                    default_act = cat_detail[item].default_activity;
                    cat_name = cat_detail[item].activity_cat_name;
                }
                htmlStr += `<li class="cr-topmenu-item cr-review-actcategory" data-toggle="curCategory" data-value-title="${cat_detail[item].activity_cat_name}"`;
                htmlStr += ` data-value-cat="${item}" data-value-act="${cat_detail[item].default_activity}"> <a href="#"> <span class="fa fa-database"></span>${cat_detail[item].activity_cat_name}</a> </li>`;
            }
            jq('#review-category').html(htmlStr);
            store.dispatch(onCurrCategoryChanged(curr_cat, default_act, cat_name));
        } else {
            let curr_cat = state.currentActivityCategory.category_id;
            let default_act = state.currentActivityCategory.default_activity;
            let category_activity = state.activityCategory.detail[curr_cat].activities;
            store.dispatch(fetchActivities(curr_cat, default_act, category_activity));
        }
    }

    jq('.cr-review-actcategory').click((e) => {
        let curr_cat = jq(e.currentTarget).attr('data-value-cat');
        let default_act = jq(e.currentTarget).attr('data-value-act');
        let cat_name = jq(e.currentTarget).text();
        store.dispatch(onCurrCategoryChanged(curr_cat, default_act, cat_name));
    });
}

function updateForCategory(newVal) {
    let viewId = 'curCategory';
    let curr_cat = newVal.category_id;
    let default_act = newVal.default_activity;
    let cat_name = newVal.activity_cat_name;
    jq(`li[data-toggle="${viewId}"]`).not(`[data-value-cat="${curr_cat}"]`).removeClass('active').addClass('notActive');
    jq(`li[data-toggle="${viewId}"][data-value-cat="${curr_cat}"]`).removeClass('notActive').addClass('active');
    let state = store.getState();
    let category_activity = state.activityCategory.detail[curr_cat].activities;
    if ((state.currentActivity === 'default-activity') || (state.currentActivity === '') || (category_activity.activity_name !== state.currentActivity)) {
        for (let i in category_activity) {
            let activity = category_activity[i];
            if (activity.activity_id === curr_cat) {
                let activity_name = activity.activity_name;
                store.dispatch(onActivityChanged(activity_name));
            }
        }
        //
    }
    store.dispatch(fetchActivities(curr_cat, default_act, category_activity));
}

function isEqualString(x, y) {
    //console.log(JSON.stringify(x));
    //console.log(JSON.stringify(y));
    return JSON.stringify(x) === JSON.stringify(y);
}


let subscribeReducer = (reducerPath, evenhandler, ...params) => {
    let w = watch(store.getState, reducerPath, isEqualString);
    store.subscribe(w((newVal, oldVal, objectPath) => {
        evenhandler(newVal, oldVal, objectPath, ...params);
    }));
};

subscribeReducer(REDUCER_NAME.currentView, updateViewOption);
subscribeReducer(REDUCER_NAME.currentDB, updateDBOption);
subscribeReducer(REDUCER_NAME.activities, updateActivityList);
subscribeReducer(REDUCER_NAME.currentActivity, updateForActivity);
subscribeReducer(REDUCER_NAME.crlist, updateAffectedCrlist);
subscribeReducer(REDUCER_NAME.affectedCrList, updateGraph);
subscribeReducer(REDUCER_NAME.teamCrCount, refreshGroupTeamFilter);
subscribeReducer(REDUCER_NAME.keywordFilters, updateAffectedCrlist);
subscribeReducer(REDUCER_NAME.KeywordMergeType, updateAffectedCrlist);
subscribeReducer(REDUCER_NAME.openDayMoreThan, updateAffectedCrlist);
subscribeReducer(REDUCER_NAME.crInDays, updateAffectedCrlist);
subscribeReducer(REDUCER_NAME.crClassFilter, updateAffectedCrlist);
subscribeReducer(REDUCER_NAME.crStateFilter, updateAffectedCrlist);
subscribeReducer(REDUCER_NAME.currTeam, updateAffectedCrlist);
subscribeReducer(REDUCER_NAME.currGroup, onGroupChanged);
subscribeReducer(REDUCER_NAME.activityCategory, onCategoryChanged);
subscribeReducer(REDUCER_NAME.currentActivityCategory, updateForCategory);