/*jslint node: true */
'use strict';

import '../../node_modules/bootstrap/dist/css/bootstrap.min.css';
import '../../lib/font-awesome-4.7.0/css/font-awesome.min.css';
import 'jquery';
import 'bootstrap';
import '../assets/css/main.css';
import {onSysChanged, onRedirected, SYS_EVENTS} from './actions/index';
import onLogin from './actions/login';
import storeWithPersist from './store';
import isEqual from 'is-equal';
import watch from 'redux-watch';
import Consts from './constants';
import cmnUtils from './util/index';
import onLogout from './actions/logout';
import deafultUserImg from '../../assets/img/icons8-contacts-50.png';
import onGetMe from './actions/getme';

const jq = jQuery.noConflict();
let store = storeWithPersist().store;

let switchLoginView = function () {
    jq(".dyn-body").hide();
    jq("#login-view").show();
};

jq("#btn-login-view").click(() => {
    switchLoginView();
});

let login = function () {
    let parms = cmnUtils.getQueryParams("next");
    let user = jq("#login-username").val() || jq("#login-dlg-username").val();
    let pwd = jq("#login-password").val() || jq("#login-dlg-password").val();
    store.dispatch(onLogin(user, pwd, parms));
};

let logout = function () {
    store.dispatch(onLogout(Consts.URL_STORE.MAIN_LOGOUT_REDIRECT));
};

jq(".btn-signin").click(login);

jq("#btn-logout").click(logout);

jq(document).on("redirect-url", (event, next) => {
    console.log("url redirection : " + next);
    if (next) {
        let decNext = decodeURIComponent(next);
        window.location.href = decNext;
    } else {
        window
            .location
            .reload();
    }
});

jq(document).on(Consts.JQUERY_EVENT.OAUTH_CHECK, () => {    
    let tokenInfoStr = cmnUtils.getOauthToken();

    // introspect token
    if (tokenInfoStr) {
        let tokenInfo = JSON.parse(tokenInfoStr);
        let formBody = `token=${tokenInfo.access_token}`;
        console.log(`introspect: ${formBody}`);
        fetch(`${Consts.URL_STORE.OAUTH_INTROSPECT}?${formBody}`, {
                headers: new Headers({
                    "Authorization": "Bearer " + tokenInfo.access_token
                })
            })
            .then(cmnUtils.handleResult)
            .then((introToken) => {
                if (!introToken.active) {
                    cmnUtils.showOauthWindow();
                } else {
                    console.log("reuse token");
                }
            })
            .catch((error) => {
                console.log("fail to introspect token: " + error);
                cmnUtils.showOauthWindow();
            });
    } else {
        cmnUtils.showOauthWindow();
    }
});

jq(document).ready(() => {
    store.dispatch(onGetMe());
});

let updateUserProfile = (newVal, oldVal) => {
    console.log(JSON.stringify(newVal));
    let loginSucc = newVal.code === Consts.STATUS_CODE.S_PASS && newVal.type === SYS_EVENTS.LOGGEDIN;
    let sessionReuse = newVal.code === Consts.STATUS_CODE.S_PASS && newVal.type === SYS_EVENTS.GOTTEN_ME;
    let logoutSucc = newVal.code === Consts.STATUS_CODE.S_PASS && newVal.type === SYS_EVENTS.LOGGEDOUT;
    let notRun = newVal.code === Consts.STATUS_CODE.S_NOTRUN; // the default state

    if (notRun) { //default state
        return;
    }

    jq("#user-profile-name").html(`${newVal.user.first_name} ${newVal.user.last_name}`);
    if (newVal.user.id !== 'default') {
        jq("#user-profile-icon").attr('src', `http://webrs.mediatek.inc/peoplepic/small/${newVal.user.id.replace('mtk', '')}.jpg`);
    } else {
        console.log(deafultUserImg);
        jq("#user-profile-icon").attr('src', deafultUserImg);
    }

    if (oldVal.code !== Consts.STATUS_CODE.S_PASS && (loginSucc || sessionReuse)) {
        jq(document).trigger(Consts.JQUERY_EVENT.OAUTH_CHECK);
    }

    if (loginSucc || sessionReuse) {
        jq("#system-logout-li").show();
        jq("#system-login-li").hide();
        jq("#login-error-msg").hide();
        jq(".dyn-body").show();
        jq("#login-view").hide();
        
    } else if (logoutSucc) {
        jq("#system-logout-li").hide();
        jq("#system-login-li").show();
        // if (jq("#user-profile-icon").attr('src').indexOf('webrs.mediatek.inc') !== -1) {
            
        // }
    } else {
        console.log("login/out failed");
        if (jq("#login-view, #login-view-alone").is(":visible")) {
            console.log("in login page");
            jq("#login-error-msg, #login-alone-error-msg").show();
            jq("#login-error-msg, #login-alone-error-msg").html(newVal.msg);
        } else {
            console.error(newVal.msg);
        }
    }

    if (newVal.next && (loginSucc || logoutSucc)) {
        console.log(`logout redirect to ${newVal.next}`);
        store.dispatch(onRedirected());
        jq(document).trigger(Consts.JQUERY_EVENT.REDIRECT_URL, newVal.next);
    }

};

let subscribeReducer = (reducerPath, evenhandler, ...params) => {
    let w = watch(store.getState, reducerPath, isEqual);
    store.subscribe(w((newVal, oldVal, objectPath) => {
        evenhandler(newVal, oldVal, objectPath, ...params);
    }));
};

subscribeReducer(Consts.REDUCER_NAME.USER_PROFILE, updateUserProfile);
// subscribeReducer(REDUCER_NAME.syncStatus, update_src_view, jq);
// store.subscribe(() => {     updateUserProfile(store.getState().USER_PROFILE);
//     // console.log(JSON.stringify(store.getState(), null, 2)); });