/*jslint node: true */
'use strict';

export function isProduction() {
    return process.env.NODE_ENV === "production";
}

export const OAUTH_CLIENT_ID = '2pPfAdi4Z6AMe5ySihP41LrFlAggb5rtVws5EMLl';
export const OAUTH_RQST_SOCPE = 'wcx_sp_alps_read+wcx_fp_moly_read+introspection';
export const OAUTH_GRANT_TYPE = 'code';
export const OAUTH_REDIRECT_URI = encodeURIComponent(((isProduction())
    ? "http://172.21.66.2:30000/o/oauth_redirect/"
    : "http://localhost:8080/"));

let Consts = {
    "JQUERY_EVENT": {
        "REDIRECT_URL": "redirect-url",
        "OAUTH_CHECK": "oauth-check"
    },
    "REDUCER_NAME": {
        "SYSTEMS": "SYSTEMS",
        "SYS_INFO": "SYS_INFO",
        "USER_PROFILE": "USER_PROFILE"
    },
    "SYSTEMS": {
        "MD_ANALYSIS": "MD Analysis",
        "CR_REVEW": "CR Revew"
    },
    URL_STORE: ((isProduction())
        ? {
            MAIN_GETME: '/me/',
            MAIN_LOGIN: `/login/`,
            MAIN_LOGOUT: '/logout/',
            MAIN_LOGOUT_REDIRECT: '/',
            OAUTH_AUTH: `/o/authorize?client_id=${OAUTH_CLIENT_ID}&scope=${OAUTH_RQST_SOCPE}&redirect_uri=${OAUTH_REDIRECT_URI}&response_type=${OAUTH_GRANT_TYPE}`,
            OAUTH_TOKEN: '/o/token/',
            OAUTH_INTROSPECT: '/o/introspect/'
        }
        : {
            MAIN_GETME: '/main_sys/assets/json/login.json',
            MAIN_LOGIN: `/main_sys/assets/json/login.json`,
            MAIN_LOGOUT: `/main_sys/assets/json/logout.json`,
            MAIN_LOGOUT_REDIRECT: '/home.html',
            OAUTH_AUTH: `login.html?client_id=${OAUTH_CLIENT_ID}&scope=${OAUTH_RQST_SOCPE}&redirect_uri=${OAUTH_REDIRECT_URI}&response_type=${OAUTH_GRANT_TYPE}`,
            OAUTH_TOKEN: '/o/token/',
            OAUTH_INTROSPECT: '/o/introspect/'
        }),
    STATUS_CODE: {
        S_LOGOUT: 3,
        S_LOGIN: 2,
        S_NOTRUN: 1,
        S_PASS: 0,
        E_UNKNOWN: -1
    }
};

export default Consts;