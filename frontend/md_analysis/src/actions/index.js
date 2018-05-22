/* jslint node: true */
"use strict";
import { MD_VIEW } from '../constants';

/*
 * action type:
 * manage the events in the central.
 */

const SYS_EVENTS = {
    VIEW_CHANGED: 'VIEW_CHANGED',
    MD_DATA_REQ: 'MD_DATA_REQ',
    MD_DATA_RESP: 'MD_DATA_RESP',
    UPDATE_SRC_REQ: 'UPDATE_SRC_REQ',
    UPDATE_SRC_RESP: 'UPDATE_SRC_RESP',
    OPTION_INIT: 'OPTION_INIT',
    REFRESH_TOP10_DATA: 'REFRESH_TOP10_DATA',
    REFRESH_MAP_DATA: 'REFRESH_MAP_DATA',
    REFRESH_WW_DATA: 'REFRESH_WW_DATA',
    REFRESH_RESOLVE_DATA: 'REFRESH_RESOLVE_DATA',
    REFRESH_OPEN_DATA: 'REFRESH_OPEN_DATA',
    REFRESH_CERT_DATA: 'REFRESH_CERT_DATA',
    REFRESH_FTA_DATA: 'REFRESH_FTA_DATA',
    REFRESH_CES_COUNTRY_DATA: 'REFRESH_CES_COUNTRY_DATA',
    REFRESH_CES_GROUP_DATA: 'REFRESH_CES_GROUP_DATA',
    GETSTATISTICDATA: 'GETSTATISTICDATA',
    GETWWMAPDATA: 'GETWWMAPDATA',
    GETRESOLVEDDATA: 'GETRESOLVEDDATA',
    GETOPENDATA: 'GETOPENDATA',
    GETCERTDATA: 'GETCERTDATA',
    GETFTADATA: 'GETFTADATA',
    GETCESCOUNTRYDATA: 'GETCESCOUNTRYDATA',
    GETCESGROUPDATA: 'GETCESGROUPDATA',
};


/*
 * action creator:
 * for simple actions only, if the actions are complicate, please use another file to implement
 */

function onViewChanged(view = MD_VIEW.STATISTICS) {
    return { type: SYS_EVENTS.VIEW_CHANGED, view };
}

function onOptionChanged(view = MD_VIEW.STATISTICS) {
    return { type: SYS_EVENTS.OPTION_CHANGED, view };
}

export { SYS_EVENTS, onViewChanged, MD_VIEW, onOptionChanged };
