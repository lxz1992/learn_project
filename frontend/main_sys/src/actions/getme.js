/*jslint node: true */
'use strict';

import {SYS_EVENTS} from '../actions/index';
import Consts from '../constants';
import cmnUtils from '../util/index';
import {defaultProfileState} from '../reducers/login';

function gettingMe() {
    return {type: SYS_EVENTS.GETTING_ME};
}

function gottenMe(data) {
    let state = {
        ...defaultProfileState,
        type: SYS_EVENTS.GOTTEN_ME
    };
    if (data.hasOwnProperty('error_code')) {
        state.code = data.error_code;
        state.msg = data.error_msg;
    } else {
        if (data.hasOwnProperty('user')) {
            state.code = Consts.STATUS_CODE.S_PASS;
            state.msg = '';
            state.user = data.user;
        } else if (cmnUtils.isEmptyObj(data)) {
            console.log("default get me state, by pass");
        } else {
            state.code = Consts.STATUS_CODE.E_UNKNOWN;
            state.msg = data;
        }
    }
    return state;
}

function onGetMe() {
    return dispatch => {
        // dispatch(gettingMe());
        let url = Consts.URL_STORE.MAIN_GETME;
        let opts = (cmnUtils.isProd())
            ? {
                credentials: 'include'
            }
            : null;
        return fetch(url, opts)
            .then(response => cmnUtils.handleResult(response))
            .then(data => dispatch(gottenMe(data)))
            .catch((reason) => {
                dispatch(gottenMe(reason));
            });
    };
}

export default onGetMe;