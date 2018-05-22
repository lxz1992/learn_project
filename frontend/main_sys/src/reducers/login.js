/*jslint node: true */
'use strict';

import {SYS_EVENTS} from '../actions/index';
import Consts from '../constants';
import {REHYDRATE} from 'redux-persist';

let defaultProfileState = {
    code: Consts.STATUS_CODE.S_NOTRUN,
    msg: '',
    user: {
        "first_name": '',
        "last_name": '',
        "email": '',
        "id": 'default',
        "last_login": ''
    },
    type: '',
    next: null,
    fetching: false
};

function userInfoReducer(state = defaultProfileState, action) {
    switch (action.type) {
        case SYS_EVENTS.LOGGINGIN:
        case SYS_EVENTS.LOGGINGOUT:
            return {
                ...state,
                type: action.type,
                fetching: true
            };
        case SYS_EVENTS.LOGGEDIN:
            return {
                ...action,
                fetching: false
            };
        case SYS_EVENTS.LOGGEDOUT:
            return {
                ...action,
                fetching: false
            };
        case SYS_EVENTS.LOGINOUT_REDIRECT:
            return {
                ...state,
                type: action.type,
                next: null
            };
        case SYS_EVENTS.GOTTEN_ME:
            return {
                ...action
            };
        default:
            return state;
    }
}

export default userInfoReducer;
export {defaultProfileState};