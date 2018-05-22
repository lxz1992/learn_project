import {MD_DATA, MD_VIEW} from '../constants';
import {SYS_EVENTS} from '../actions/index';
import config from '../config';
import cmnUtils from '../util/index';

function requestData() {
    return {type: SYS_EVENTS.MD_DATA_REQ};
}

function receiveData(dispatch, data, view) {
    // data['error_code'] = 12345; data['error_msg'] = "this is an error";
    // console.log("receiving" + JSON.stringify(data));
    if (view === '') {
        return {
            type: SYS_EVENTS.MD_DATA_RESP,
            code: 1,
            message: data
        };
    }
    let fail_result = {
        type: SYS_EVENTS.MD_DATA_RESP,
        code: 1,
        message: data['message']
    };
    let sucess_result = {
        type: SYS_EVENTS.GETSTATISTICDATA,
        code: 0,
        updateTime: data['updateTime'],
        receivedAt: Date
            .now()
            .toLocaleString(),
        message: ''
    };
    if (data.hasOwnProperty('error_code')) {
        sucess_result['code'] = data['error_code'];
        sucess_result['message'] = data['error_msg'];
    }

    switch (view) {
        case MD_VIEW.STATISTICS:
            sucess_result['type'] = SYS_EVENTS.GETSTATISTICDATA;
            if (cmnUtils.checkPropIgnoreCase(data, 'Country')) {
                sucess_result['country'] = data['Country'];
            } else {
                sucess_result['country'] = {};
            }
            if (cmnUtils.checkPropIgnoreCase(data, 'Customer')) {
                sucess_result['customer'] = data['Customer'];
            } else {
                sucess_result['customer'] = {};
            }
            if (cmnUtils.checkPropIgnoreCase(data, 'Operator')) {
                sucess_result['operator'] = data['Operator'];
            } else {
                sucess_result['operator'] = {};
            }
            dispatch(fetchModemData(MD_VIEW.WWMAP));
            break;
        case MD_VIEW.WWMAP:
            sucess_result['type'] = SYS_EVENTS.GETWWMAPDATA;
            if (cmnUtils.checkPropIgnoreCase(data, 'map')) {
                sucess_result['map'] = data['map'];
            } else {
                sucess_result['map'] = {};
            }
            break;
        case MD_VIEW.RESOLVED_ESERVICES:
            sucess_result['type'] = SYS_EVENTS.GETRESOLVEDDATA;
            if (cmnUtils.checkPropIgnoreCase(data, 'resolved')) {
                sucess_result['resolved'] = data['resolved'];
            } else {
                sucess_result['resolved'] = [];
            }
            break;
        case MD_VIEW.OPEN_ESERVICES:
            sucess_result['type'] = SYS_EVENTS.GETOPENDATA;
            if (cmnUtils.checkPropIgnoreCase(data, 'open')) {
                sucess_result['open'] = data['open'];
            } else {
                sucess_result['open'] = [];
            }
            break;
        case MD_VIEW.OPERATOR_CERTIFICATION:
            sucess_result['type'] = SYS_EVENTS.GETCERTDATA;
            if (cmnUtils.checkPropIgnoreCase(data, 'data')) {
                sucess_result['operator_certification'] = data['data'];
            } else {
                sucess_result['operator_certification'] = [];
            }
            break;
        case MD_VIEW.FTA:
            sucess_result['type'] = SYS_EVENTS.GETFTADATA;
            if (cmnUtils.checkPropIgnoreCase(data, 'data')) {
                sucess_result['fta'] = data['data'];
            } else {
                sucess_result['fta'] = {};
            }
            break;
        case MD_VIEW.CES_SPECIFIC:
        case MD_VIEW.CES_COUNTRY:
            sucess_result['type'] = SYS_EVENTS.GETCESCOUNTRYDATA;
            if (cmnUtils.checkPropIgnoreCase(data, 'Country')) {
                sucess_result['ces_country'] = data['Country'];
            } else {
                sucess_result['ces_country'] = {};
            }
            dispatch(fetchModemData(MD_VIEW.CES_GROUP));
            break;
        case MD_VIEW.CES_GROUP:
            sucess_result['type'] = SYS_EVENTS.GETCESGROUPDATA;
            if (cmnUtils.checkPropIgnoreCase(data, 'group')) {
                sucess_result['ces_group'] = data['group'];
            } else {
                sucess_result['ces_group'] = {};
            }
            break;
        default:
            return {type: SYS_EVENTS.MD_DATA_RESP, code: 1, message: 'Do not support this function now....'};
    }
    //console.log("receiving" + JSON.stringify(sucess_result));
    return ((data.hasOwnProperty('message'))
        ? fail_result
        : sucess_result);

}

function handleResult(response) {
    if (response.status === 200 || response.status === 0) {
        return Promise.resolve(response.json());
    } else {
        return Promise.reject(new Error(`Status: ${response.status}\nMessage: ${response.statusText}`));
    }
}

function fetchModemData(view) {
    // console.log(process.env.NODE_ENV);
    let cfg = config.API;
    let url = '';
    switch (view) {
        case MD_VIEW.STATISTICS:
            url = cfg.STATISTICS;
            break;
        case MD_VIEW.WWMAP:
            url = cfg.WWMAP;
            break;
        case MD_VIEW.RESOLVED_ESERVICES:
            url = cfg.RESOLVED_ESERVICES;
            break;
        case MD_VIEW.OPEN_ESERVICES:
            url = cfg.OPEN_ESERVICES;
            break;
        case MD_VIEW.OPERATOR_CERTIFICATION:
            url = cfg.OPERATOR_CERTIFICATION;
            break;
        case MD_VIEW.FTA:
            url = cfg.FTA;
            break;
        case MD_VIEW.CES_SPECIFIC:
        case MD_VIEW.CES_COUNTRY:
            url = cfg.CES_COUNTRY;
            break;
        case MD_VIEW.CES_GROUP:
            url = cfg.CES_GROUP;
            break;
        default:
            break;
    }
    //console.log(view+ ':' + url);
    return dispatch => {
        dispatch(requestData());
        return fetch(url, {credentials: 'include'})
            .then(response => handleResult(response))
            .then(data => dispatch(receiveData(dispatch, data, view)))
            .catch((reason) => {
                dispatch(receiveData(dispatch, reason, ''));
            });
    };

}

function viewOptionsChanged(data) {
    let Year = {};
    let resolve_sites = [];
    let resolve_customer = {};
    let open_sites = [];
    let key_data;
    let key;
    let mapYear = [];
    let allResolvedCustomer = [];

    let type = MD_DATA.Type;
    for (let x in type) {
        Year[type[x]] = [];
        key_data = data[type[x]];
        for (key in key_data) {
            Year[type[x]].push(key);
        }
    }
    //console.log(JSON.stringify(data.resolved));
    key_data = data.resolved;
    for (key in key_data) {
        resolve_sites.push(key);
        let cutomer_list = ResolveSiteCustomers(key, key_data[key]);
        cutomer_list.unshift('All');
        resolve_customer[key] = cutomer_list;
        allResolvedCustomer = allResolvedCustomer.concat(resolve_customer[key]);
    }
    resolve_sites.unshift('All');
    let u_resolve_customer = unique(allResolvedCustomer);
    u_resolve_customer = u_resolve_customer.sort();
    u_resolve_customer.unshift('All');
    resolve_customer['All'] = u_resolve_customer;
    //console.log(JSON.stringify(resolve_customer));
    key_data = data.open;
    for (key in key_data) {
        open_sites.push(key);
    }

    key_data = data.map.data;
    for (key in key_data) {
        mapYear.push(key);
    }

    return {
        type: SYS_EVENTS.OPTION_INIT,
        code: 0,
        option_type: MD_DATA.Type,
        option_year: Year,
        option_sel: MD_DATA.OptionSel,
        option_resolved_customer: resolve_customer,
        option_resolved_sites: resolve_sites,
        option_open_sites: open_sites,
        option_map_state: MD_DATA.State_big,
        option_map_year: mapYear,
        message: ''
    };
}

function ResolveSiteCustomers(site, data) {
    let key;
    let resolve_customer = [];
    for (key in data) {
        if (key) {
            resolve_customer.push(key);
        }

    }

    let u_resolve_customer = unique(resolve_customer);
    return u_resolve_customer.sort();

}

function unique(arr) {
    let tmp = new Array();
    for (let i in arr) {
        if (tmp.indexOf(arr[i]) === -1) {
            tmp.push(arr[i]);
        }
    }
    return tmp;
}

export {fetchModemData, viewOptionsChanged};