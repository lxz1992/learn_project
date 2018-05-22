/*jslint node: true */
"use strict";
import Consts, {isProduction} from '../constants';

export const TOEKN_KEY = "OAUTH_TOKEN_KEY";

let cmnUtils = {
    isProd: () => {
        return isProduction();
    },
    sleep: function (delayMs) {
        return new Promise(resolve => setTimeout(resolve, delayMs));
    },
    getQueryParams: function (name, url) {
        if (!url) 
            url = location.href;
        name = name
            .replace(/[\[]/, "\\\[")
            .replace(/[\]]/, "\\\]");
        var regexS = "[\\?&]" + name + "=([^&#]*)";
        var regex = new RegExp(regexS);
        var results = regex.exec(url);
        return results == null
            ? null
            : results[1];
    },
    legalURL: function (strUrl) {
        return encodeURIComponent(strUrl);
    },
    handleResult: function (response) {
        if (response.status === 200 || response.status === 0) {
            return Promise.resolve(response.json());
        } else {
            return Promise.reject(new Error(`Status: ${response.status}\nMessage: ${response.statusText}`));
        }
    },
    showOauthWindow: function () {
        let w = 600;
        let h = 400;
        var dualScreenLeft = window.screenLeft != undefined
            ? window.screenLeft
            : window.screenX;
        var dualScreenTop = window.screenTop != undefined
            ? window.screenTop
            : window.screenY;

        var width = window.innerWidth
            ? window.innerWidth
            : document.documentElement.clientWidth
                ? document.documentElement.clientWidth
                : screen.width;
        var height = window.innerHeight
            ? window.innerHeight
            : document.documentElement.clientHeight
                ? document.documentElement.clientHeight
                : screen.height;

        var left = ((width / 2) - (w / 2)) + dualScreenLeft;
        var top = ((height / 2) - (h / 2)) + dualScreenTop;
        let config = (isProduction())
            ? `width=${w},height=${h},location=no,resizable=no,left=${left},top=${top}`
            : `width=${w},height=${h},left=${left},top=${top}`;
        console.log("show window: " + config);
        window.open(Consts.URL_STORE.OAUTH_AUTH, "Authorization", config);
    },
    getOauthToken: function () {
        return window
            .localStorage
            .getItem(TOEKN_KEY);
    },
    setOauthToken: function (tk) {
        window
            .localStorage
            .setItem(TOEKN_KEY, tk);
    },
    oauthFetch: function (url) {
        let tokenInfoStr = this.getOauthToken();
        let token = JSON.parse(tokenInfoStr);
        let options = (isProduction())
            ? {
                headers: new Headers({
                    "Authorization": "Bearer " + token.access_token
                }),
                credentials: 'include'
            }
            : {};
        return fetch(url, options);
    },
    isEmptyObj: function (obj) {
        return Object
            .keys(obj)
            .length === 0;
    }
};

export default cmnUtils;