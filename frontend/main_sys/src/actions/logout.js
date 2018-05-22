/*jslint node: true */
'use strict';

import {SYS_EVENTS} from '../actions/index';
import Consts from '../constants';
import cmnUtils from '../util/index';
import {defaultProfileState} from '../reducers/login';

function handleLoggedOut(data, redirect) {
    let state = {
        ...defaultProfileState,
        type: SYS_EVENTS.LOGGEDOUT,
        next: redirect
    };
    if (data.hasOwnProperty('error_code')) {
        state.code = data.error_code;
        state.msg = data.error_msg;
    } else {
        if (data.hasOwnProperty('result')) {
            // reset to default page
            state.code = Consts.STATUS_CODE.S_PASS;
            state.msg = '';
        } else {
            state.code = Consts.STATUS_CODE.E_UNKNOWN;
            state.msg = data;
        }
    }
    return state;
}

function onLogout(redirect = null) {
    return dispatch => {
        let url = Consts.URL_STORE.MAIN_LOGOUT;
        let opts = (cmnUtils.isProd())
            ? {
                method: 'post',
                credentials: 'include'
            }
            : null;
        return fetch(url, opts)
            .then(response => cmnUtils.handleResult(response))
            .then(data => dispatch(handleLoggedOut(data, redirect)))
            .catch((reason) => {
                dispatch(handleLoggedOut(reason, redirect));
            });
    };
}

export default onLogout;