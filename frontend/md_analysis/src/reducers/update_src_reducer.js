/* jslint node: true */
"use strict";

import { SYS_EVENTS } from "../actions/index";

let defaulatSyncStatus = {
    syncStatus: 'finished',
    latestSyncTime: '',
    isSyncing: false,
    errorMsg: '',
    code: 0
};

function syncStatusReducer(state = defaulatSyncStatus, action) {
    switch (action.type) {
        case SYS_EVENTS.UPDATE_SRC_REQ:
            return {
                ...state,
                isSyncing: action.isSyncing
            };
        case SYS_EVENTS.UPDATE_SRC_RESP:
            return {
                ...state,
                isSyncing: action.isSyncing,
                syncStatus: action.syncStatus,
                latestSyncTime: action.latestSyncTime,
                errorMsg: action.errorMsg,
                code: action.code
            }
        default:
            return state;
    }
};

export {syncStatusReducer};