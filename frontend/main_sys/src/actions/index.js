/* jslint node: true */
"use strict";
import Consts from '../constants';

/*
 * action type:
 * manage the events in the central.
 */

const SYS_EVENTS = {
    SYS_CHANGED: "SYS_CHANGED",
    LOGGINGIN: "LOGGINGIN",
    LOGGEDIN: "LOGGEDIN",
    LOGGINGOUT: "LOGGINGOUT",
    LOGGEDOUT: "LOGGEDOUT",
    LOGINOUT_REDIRECT: "LOGINOUT_REDIRECT",
    GETTING_ME: "GETTING_ME",
    GOTTEN_ME : "GOTTEN_ME"
};

/*
 * action creator:
 * for simple actions only, if the actions are complicate, please use another file to implement
 */

function onSysChanged(sys = Consts.SYSTEMS.CR_REVEW) {
    return {type: SYS_EVENTS.SYS_CHANGED, sys};
}

function onRedirected() {
    return {type: SYS_EVENTS.LOGINOUT_REDIRECT};
}

export {SYS_EVENTS, onSysChanged, onRedirected};
