/*jslint node: true */
"use strict";

let cmnUtils = {
    isProd: () => {
        return (process.env.NODE_ENV === "production");
    },
    sleep: function (delayMs) {
        return new Promise(resolve => setTimeout(resolve, delayMs));
    },
    capitalizeFirstLetter: function (str) {
        return str
            .charAt(0)
            .toUpperCase() + str.slice(1);
    },
    checkPropIgnoreCase: function (obj, prop) {
        let propStr = prop.toString();
        return obj.hasOwnProperty(propStr) || obj.hasOwnProperty(this.capitalizeFirstLetter(propStr)) || obj.hasOwnProperty(propStr.toLowerCase() || obj.hasOwnProperty(propStr.toUpperCase()));
    },
    csrfSafeMethod: function (method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
};

export default cmnUtils;