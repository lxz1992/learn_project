/* jslint node: true */
"use strict";
import config from '../config';
import {SYS_EVENTS} from './index';
import {fetchModemData} from './mddata';
import cmnUtils from '../util/index';
import {MD_UPDATE_STATUS} from '../constants';
import store from '../store';

function requestUpdate() {
    return {type: SYS_EVENTS.UPDATE_SRC_REQ, 'isSyncing': true};
}

function receiveUpdateResult(syncStatus) {
    return (syncStatus.hasOwnProperty('error_code'))
        ? {
            type: SYS_EVENTS.UPDATE_SRC_RESP,
            'isSyncing': false,
            'code': syncStatus.error_code,
            'errorMsg': syncStatus.error_msg
        }
        : {
            type: SYS_EVENTS.UPDATE_SRC_RESP,
            'syncStatus': syncStatus.status,
            'latestSyncTime': syncStatus.last_update_time,
            'isSyncing': (syncStatus.status === MD_UPDATE_STATUS.ongoing)
                ? true
                : false,
            'code': 0,
            'errorMsg': ''
        };
}

function errorHandling(error) {
    return {
        'type': SYS_EVENTS.UPDATE_SRC_RESP,
        'code': -1,
        'errorMsg': `Error: ${JSON.stringify(error)}`,
        'isSyncing': false
    };
}

function updateSource(getTimeOnly, forceQuery=false) {
    let url = config.API.UPDATE_SOURCE;
    if (cmnUtils.isProd() && getTimeOnly) {
        url += '&get_last_time=1';
    }
    return dispatch => {
        dispatch(requestUpdate());
        return fetch(url, {credentials: 'include'}).then(resp => resp.json()) // async
            .then((syncStatus) => {
            console.debug(`get sync source result: ${JSON.stringify(syncStatus)}`);
            // no error message, only finish or ongoing
            dispatch(receiveUpdateResult(syncStatus));

            // only finish with success needs to udpate the current view
            if (syncStatus.status === MD_UPDATE_STATUS.finish || forceQuery) {
                let state = store.getState();
                console.debug(state.currentView);
                dispatch(fetchModemData(state.currentView));
            }

        }).catch((error) => {
            // any connection or parse error
            console.trace(error.message);
            dispatch(errorHandling(error.message));
        });
    };
}

export {updateSource};