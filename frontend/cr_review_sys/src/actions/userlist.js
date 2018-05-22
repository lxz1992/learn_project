import {
    SYS_EVENTS
} from '../actions/index';
import {
    URL_STORE
} from '../constants';

function requestUserlist() {
    return {
        type: SYS_EVENTS.USER_LIST_REQ
    };
}

function receiveuserlist(query_result, url, dispatch) {
    console.log(url);
    if ((url !== '') && (url !== null) && (url !== undefined)) {
        fetch(url, {
                credentials: 'include'
            })
            .then(response => handleResult(response))
            .then(data => {
                url = data.next;
                query_result.push(data);
                receiveuserlist(query_result, url, dispatch);
            })
            .catch((reason) => {
                //dispatch(receiveCRs(reason));
            });
    } else {
        let fail_result = {
            type: SYS_EVENTS.USER_LIST_RESP,
            code: 1,
            message: ''
        };
        let sucess_result = {
            type: SYS_EVENTS.USER_LIST_RESP,
            code: 0,
            receivedAt: Date.now().toLocaleString(),
            message: ''
        };
        let all_query_userlist = [];
        for (let i in query_result) {
            let data = query_result[i];
            if (data.hasOwnProperty('error_code')) {
                console.log('data has error_code.....');
                console.log(JSON.stringify(data));
                sucess_result['code'] = data['error_code'];
                sucess_result['message'] = data['error_msg'];
            } else {
                all_query_userlist = all_query_userlist.concat(data.results);
            }
        }
        sucess_result.user_list = all_query_userlist;
        return (dispatch(sucess_result));
    }
}

function handleResult(response) {
    if (response.status === 200 || response.status === 0) {
        return Promise.resolve(response.json());
    } else {
        return Promise.reject(new Error(`Status: ${response.status}\nMessage: ${response.statusText}`));
    }
}

function fetchUserList() {
    return dispatch => {
        dispatch(requestUserlist());
        let url = URL_STORE.CR_REVIEW.USER_LIST;
        let query_result = [];
        receiveuserlist(query_result, url, dispatch);
        /*return fetch(URL_STORE.CR_REVIEW.USER_LIST, {credentials: 'include'})
            .then(response => handleResult(response))
            .then(data => {
                dispatch(receiveuserlist(dispatch, data));
            })
            .catch((reason) => {
                dispatch(receiveuserlist(dispatch, reason));
            });*/
    };
}

function requestUser() {
    return {
        type: SYS_EVENTS.CURRENTUSER_LIST_REQ
    };
}

function receiveuser(dispatch, data) {
    let result = {
        type: SYS_EVENTS.CURRENTUSER_LIST_RESP,
        code: 0,
        message: '',
        user: {}
    };
    if (data.hasOwnProperty('user')) {
        result.user = data.user;
    } else {
        result.code = 1;
        result.message = data;
    }
    return result;
}

function fetchLoginUser() {
    return dispatch => {
        dispatch(requestUser());
        let url = URL_STORE.CR_REVIEW.LOGIN_USER_INFO;
        return fetch(url, {credentials: 'include'})
            .then(response => handleResult(response))
            .then(data => {
                dispatch(receiveuser(dispatch, data));
            })
            .catch((reason) => {
                dispatch(receiveuser(dispatch, reason));
            });
    };
}


export {
    fetchUserList,
    fetchLoginUser
};