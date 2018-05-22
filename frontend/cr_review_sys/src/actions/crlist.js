import {
    SYS_EVENTS
} from '../actions/index';
import {
    URL_STORE,
    GV
} from '../constants';
import {
    getNowTimeText,
    getSecondBetween,
    sprintf,
    crDaysBetween
} from '../data/cr_datetime';
import cmnUtils from '../util/index';

function requestCrs() {
    return {
        type: SYS_EVENTS.CR_LIST_REQ
    };
}

function getCrDays(from_time, to_time) {
    let result = '';
    if (to_time === '') {
        to_time = getNowTimeText();
    }
    result = crDaysBetween(from_time, to_time);

    return result;
}

function getCrTimeBetween(from_time, to_time) {
    let result = '';
    //console.log(from_time);
    //console.log(from_time);
    if ((from_time === null) || (from_time === undefined)) {
        return result;
    }
    if ((to_time === '') || (to_time === null) || (to_time === undefined)) {
        to_time = getNowTimeText();
    }
    let secondBetween = getSecondBetween(from_time, to_time);
    let hourBetween = parseInt(secondBetween / 3600);
    result = hourBetween + 'hr';
    if (hourBetween < 10) {
        let miniteBetween = parseInt((secondBetween - 3600 * hourBetween) / 60);
        result = sprintf('%2d:%02d', hourBetween, miniteBetween);
    } else {
        let daysBetween = parseInt(secondBetween / (3600 * 24));
        if (daysBetween > 0) {
            result += "\n(" + daysBetween + "days)";
        }

    }

    return result;
}

function parsetodocr(querycr) {
    let resultcr = {};
    let all_cr_info = {};
    for (let i in querycr) {
        let ori_crinfo = querycr[i];
        let ready_crinfo = {};
        for (let field in GV.fieldMap) {
            let ori_field = GV.fieldMap[field];
            let ori_value = '';
            if (ori_crinfo.hasOwnProperty(ori_field)) {
                ori_value = ori_crinfo[ori_field];
                if (ori_value === null) {
                    ori_value = '';
                }
                if (GV.crDaysMap[ori_field] !== undefined) {
                    if (ori_value !== null) {
                        ori_value = ori_value.replace('T', ' ');
                        ori_value = ori_value.replace('Z', '');
                        ori_value = ori_value.replace('+08:00', '');

                        let arrTime = ori_value.split(' ');
                        let date_value = arrTime[0];
                        if (GV.crDateMap[ori_field] !== undefined) {
                            ready_crinfo[GV.crDateMap[ori_field]] = date_value;
                        } else {
                            ready_crinfo[ori_field] = date_value;
                        }

                    } else {
                        if (GV.crDateMap[ori_field] !== undefined) {
                            ready_crinfo[GV.crDateMap[ori_field]] = '';
                        } else {
                            ready_crinfo[ori_field] = '';
                        }
                    }

                }
            }
            ready_crinfo[field] = ori_value;
        }
        let finishedDate = '';
        if ((ori_crinfo.resolve_date !== null) && (ori_crinfo.submit_date !== '')) {
            finishedDate = ori_crinfo.resolve_date;
        }
        let open_days = getCrDays(ready_crinfo.Submit_DateTime, finishedDate);
        let assign_days = getCrDays(ready_crinfo.Assign_DateTime, finishedDate);
        let resolve_days = '';
        if (finishedDate !== '') {
            resolve_days = assign_days;
        }
        ready_crinfo.Open_Days = open_days;
        ready_crinfo.Assign_Days = assign_days;
        ready_crinfo.Resolve_Days = resolve_days;
        let submit_time = getCrTimeBetween(ready_crinfo.Submit_DateTime, finishedDate);
        let assign_time = getCrTimeBetween(ready_crinfo.Assign_DateTime, finishedDate);
        let resolve_time = '';
        if (finishedDate !== '') {
            resolve_time = assign_time;
        }
        ready_crinfo.Submit_DateTimeNum = submit_time;
        ready_crinfo.Assign_DateTimeNum = assign_time;
        ready_crinfo.Resolve_DateTimeNum = resolve_time;
        all_cr_info[ori_crinfo.cr_id] = ready_crinfo;
    }
    resultcr = all_cr_info;
    return resultcr;
}

function receiveCRs(query_result, url, dispatch) {
    console.log('url:' + url);
    if ((url !== '') && (url !== null) && (url !== undefined)) {
        fetch(url, {
                credentials: 'include'
            })
            .then(response => handleResult(response))
            .then(data => {
                url = data.next;
                query_result.push(data);
                receiveCRs(query_result, url, dispatch);
            })
            .catch((reason) => {
                //dispatch(receiveCRs(reason));
            });
    } else {
        let fail_result = {
            type: SYS_EVENTS.CR_LIST_RESP,
            code: 1,
            message: ''
        };
        let sucess_result = {
            type: SYS_EVENTS.CR_LIST_RESP,
            code: 0,
            //updateTime: data['updateTime'],
            message: ''
        };
        let all_query_cr = [];
        for (let i in query_result) {
            let data = query_result[i];
            if (data.hasOwnProperty('error_code')) {
                console.log('data has error_code.....');
                console.log(JSON.stringify(data));
                sucess_result['code'] = data['error_code'];
                sucess_result['message'] = data['error_msg'];
            } else {
                all_query_cr = all_query_cr.concat( data.results );
            }
        }
        sucess_result.cr = parsetodocr(all_query_cr);
        //console.log(JSON.stringify(sucess_result));
        //return sucess_result;
        return (dispatch(sucess_result));
        //return ((data.hasOwnProperty('message')) ?
        //    fail_result :
        //    sucess_result);
    }

}


function handleResult(response) {
    if (response.status === 200 || response.status === 0) {
        return Promise.resolve(response.json());
    } else {
        return Promise.reject(new Error(`Status: ${response.status}\nMessage: ${response.statusText}`));
    }
}

function fetchActivityCrs(activity, dblist) {
    console.log(activity + '/?cr_db=' + dblist.join('/'));
    return dispatch => {
        dispatch(requestCrs());
        let url = URL_STORE.CR_REVIEW.ALLCR; // + activity + '/' + dblist;
        if (cmnUtils.isProd()) {
            url += activity + '/?cr_db=' + dblist.join(',');
        }
        let query_result = [];
        receiveCRs(query_result, url, dispatch);
        /*return fetch(url, {credentials: 'include'})
            .then(response => handleResult(response))
            .then(data => dispatch(receiveCRs(data)))
            .catch((reason) => {
                dispatch(receiveCRs(reason));
            });
            */
    };
}

function onCrlistChanged(affectedCrList) {
    return dispatch => {
        dispatch({
            type: SYS_EVENTS.AFFECTEDCRLIST,
            affectedCrList: affectedCrList
        });
    };

}

function onTeamCountChanged(teamcrcount) {
    return dispatch => {

        dispatch({
            type: SYS_EVENTS.TEAMCRCOUNT,
            teamcrcount: teamcrcount
        });
    };

}

export {
    fetchActivityCrs,
    onCrlistChanged,
    onTeamCountChanged
};