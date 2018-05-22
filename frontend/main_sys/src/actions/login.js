/*jslint node: true */
'use strict';

import {SYS_EVENTS} from '../actions/index';
import Consts from '../constants';
import cmnUtils from '../util/index';
import {defaultProfileState} from '../reducers/login';

function loggingIn() {
    return {type: SYS_EVENTS.LOGGINGIN};
}

function handleLoggedIn(data, redirect) {
    let state = {
        ...defaultProfileState,
        type: SYS_EVENTS.LOGGEDIN,
        next: redirect
    };
    if (data.hasOwnProperty('error_code')) {
        state.code = data.error_code;
        state.msg = data.error_msg;
    } else {
        if (data.hasOwnProperty('user')) {
            state.code = Consts.STATUS_CODE.S_PASS;
            state.user = data.user;
            state.msg = '';
        } else {
            state.code = Consts.STATUS_CODE.E_UNKNOWN;
            state.msg = data;
        }
    }
    return state;
}

function onLogin(user = "", pwd = "", redirect = null) {
    return dispatch => {
        // dispatch(loggingIn());
        let url = Consts.URL_STORE.MAIN_LOGIN; // + activity + '/' + dblist;
        let opts = (cmnUtils.isProd())
            ? {
                method: 'post',
                credentials: 'include',
                headers: {
                    "Authorization": "Basic " + btoa(`${user}:${pwd}`)
                }
            }
            : null;
        return fetch(url, opts)
            .then(response => cmnUtils.handleResult(response))
            .then(data => dispatch(handleLoggedIn(data, redirect)))
            .catch((reason) => {
                dispatch(handleLoggedIn(reason, redirect));
            });
    };
}

export default onLogin;