import {
    SYS_EVENTS
} from '../actions/index';
import {
    URL_STORE
} from '../constants';

import cmnUtils from '../../../main_sys/src/util/index';

function requestActivities() {
    return {
        type: SYS_EVENTS.ACTIOON_LIST_REQ
    };
}

function parseActivityData(activitydata, default_act) {
    //console.log('default activity id:' + default_act);
    //let activitydata = data.results;
    let result = {
        "Default": '',
        "Ongoing": [],
        "Finished": [],
        "detail": {}
    };
    let defaultactivity = '';
    for (let i in activitydata) {
        let activityInfo = activitydata[i];
        //result.detail[activityInfo.activity_name] = {};
        result.detail[activityInfo.activity_name] = activityInfo;
        //console.log(JSON.stringify(activityInfo));
        if (parseInt(activityInfo.activity_id) === parseInt(default_act)) {
            result.Default = activityInfo.activity_name;
            defaultactivity = activityInfo.activity_name;
        }
        if (activityInfo.active) {
            result.Ongoing.push(activityInfo.activity_name);
            if (defaultactivity === '') {
                defaultactivity = activityInfo.activity_name;
            }
        } else {
            result.Finished.push(activityInfo.activity_name);
        }
    }
    result.Default = defaultactivity;
    //console.log(JSON.stringify(result));
    return result;
}

function receiveActivities(data, default_act) {
    let fail_result = {
        type: SYS_EVENTS.ACTIOON_LIST_RESP,
        code: 1,
        message: data['detail']
    };
    let sucess_result = {
        type: SYS_EVENTS.ACTIOON_LIST_RESP,
        code: 0,
        //updatedAt: data['UpdatedAt'],
        receivedAt: Date.now().toLocaleString(),
        default: '',
        message: ''
    };
    /*if (data.hasOwnProperty('error_code')) {
        sucess_result['code'] = data['error_code'];
        sucess_result['message'] = data['detail'];
    }*/
    if (!(data.hasOwnProperty("error_code"))) {
        let myactivitydata = parseActivityData(data, default_act);
        sucess_result.default = myactivitydata.Default;
        sucess_result.onGoing = myactivitydata.Ongoing;
        sucess_result.finished = myactivitydata.Finished;
        sucess_result.detail = myactivitydata.detail;
    }
    /*
    return ((data.hasOwnProperty('error_code')) ?
        fail_result :
        sucess_result);*/
    return sucess_result;
}

function handleResult(response) {
    if (response.status === 200 || response.status === 0) {
        return Promise.resolve(response.json());
    } else {
        return Promise.reject(new Error(`Status: ${response.status}\nMessage: ${response.statusText}`));
    }
}

function fetchActivities(curr_cat, default_act, category_activity) {
    /*return dispatch => {
        dispatch(requestActivities());
        let url = URL_STORE.CR_REVIEW.ACTIVITY + 'curr_cat';
        return cmnUtils.oauthFetch(URL_STORE.CR_REVIEW.ACTIVITY)
            .then(response => handleResult(response))
            .then(data => {
                dispatch(receiveActivities(dispatch, data, default_act));
            })
            .catch((reason) => {
                dispatch(receiveActivities(dispatch, reason, default_act));
            });
    };*/
    return receiveActivities( category_activity, default_act);
}

function requestActivityCategory() {
    return {
        type: SYS_EVENTS.ACTIVITYCATEGORY_LIST_REQ
    };
}

function receiveActivityCategory(dispatch, data) {
    let fail_result = {
        type: SYS_EVENTS.ACTIVITYCATEGORY_LIST_RESP,
        code: 1,
        message: data['detail']
    };
    let sucess_result = {
        type: SYS_EVENTS.ACTIVITYCATEGORY_LIST_RESP,
        code: 0,
        message: '',
        detail: {}
    };
    if (data.hasOwnProperty('error_code')) {
        sucess_result['code'] = data['error_code'];
        sucess_result['message'] = data['detail'];
    }
    if (!(data.hasOwnProperty("error_code"))) {
        let categorydata = data.results;
        for (let i in categorydata) {
            let categoryInfo = categorydata[i];
            //console.log(JSON.stringify(categoryInfo));

            if ((categoryInfo.active === undefined) || (categoryInfo.active)) {
                //console.log('active category.....');
                sucess_result.detail[categoryInfo.activity_cat_id] = categoryInfo;
                //console.log(JSON.stringify(sucess_result));
            }
        }
    }
    //console.log(JSON.stringify(sucess_result));
    return ((data.hasOwnProperty('error_code')) ?
        fail_result :
        sucess_result);
}

function fetchActivityCategory() {
    return dispatch => {
        dispatch(requestActivityCategory());
        return fetch(URL_STORE.CR_REVIEW.ACTIVITYCATEGORY, {credentials: 'include'})
            .then(response => handleResult(response))
            .then(data => {
                dispatch(receiveActivityCategory(dispatch, data));
            })
            .catch((reason) => {
                dispatch(receiveActivityCategory(dispatch, reason));
            });
    };
}

export {
    fetchActivities,
    fetchActivityCategory
};