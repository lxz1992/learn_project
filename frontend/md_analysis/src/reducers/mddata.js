import '../actions/index';
import {SYS_EVENTS} from '../actions/index';
import {MD_DATA} from '../constants';

let defaultState = {
    resolved: [],
    map: {},
    Country: {},
    Customer: {},
    Operator: {},
    open: [],
    operator_certification: [],
    fta: {},
    ces_country: {},
    ces_group: {},
    updateTime: [],
    isFetching: false,
    didInvalidate: false,
    status: 'success',
    message: '',
    code: 0
};

let defaultOption1 = {
    option_type: MD_DATA.Type,
    option_year: {},
    option_sel: [],
    option_resolved_customer: {},
    option_resolved_sites: [],
    option_open_sites: [],
    option_map_state: [],
    option_map_year: [],
    message: '',
    code: 1
};

let defaultGraph = {
    top10data: [],
    resolvedata: {},
    opendata: {},
    ww_map: [],
    operator_cert_data: {},
    ftadata: {},
    ces_country_data: [],
    ces_group_data: []
};

function dataReducer(state = defaultState, action) {
    switch (action.type) {
        case SYS_EVENTS.MD_DATA_REQ:
            return {
                ...state,
                isFetching: true,
                didInvalidate: false,
                message: ""
            };
        case SYS_EVENTS.MD_DATA_RESP:
            return {
                ...state,
                code: action['code'],
                message: action['message'],
                isFetching: false,
                didInvalidate: false
            };
        case SYS_EVENTS.GETSTATISTICDATA:
            return {
                ...state,
                isFetching: false,
                didInvalidate: false,
                Country: action["country"],
                Customer: action["customer"],
                Operator: action["operator"],
                updateTime: action["updateTime"],
                receivedAt: action["receivedAt"],
                code: action["code"],
                message: action["message"]
            };
        case SYS_EVENTS.GETWWMAPDATA:
            return {
                ...state,
                isFetching: false,
                didInvalidate: false,
                map: action["map"],
                updateTime: action["updateTime"],
                receivedAt: action["receivedAt"],
                code: action["code"],
                message: action["message"]
            };
        case SYS_EVENTS.GETRESOLVEDDATA:
            return {
                ...state,
                isFetching: false,
                didInvalidate: false,
                resolved: action["resolved"],
                updateTime: action["updateTime"],
                receivedAt: action["receivedAt"],
                code: action["code"],
                message: action["message"]
            };
        case SYS_EVENTS.GETOPENDATA:
            return {
                ...state,
                isFetching: false,
                didInvalidate: false,
                open: action["open"],
                updateTime: action["updateTime"],
                receivedAt: action["receivedAt"],
                code: action["code"],
                message: action["message"]
            };
        case SYS_EVENTS.GETCERTDATA:
            return {
                ...state,
                isFetching: false,
                didInvalidate: false,
                operator_certification: action["operator_certification"],
                updateTime: action["updateTime"],
                receivedAt: action["receivedAt"],
                code: action["code"],
                message: action["message"]
            };
        case SYS_EVENTS.GETFTADATA:
            return {
                ...state,
                isFetching: false,
                didInvalidate: false,
                fta: action["fta"],
                updateTime: action["updateTime"],
                receivedAt: action["receivedAt"],
                code: action["code"],
                message: action["message"]
            };
        case SYS_EVENTS.GETCESCOUNTRYDATA:
            return {
                ...state,
                isFetching: false,
                didInvalidate: false,
                ces_country: action["ces_country"],
                updateTime: action["updateTime"],
                receivedAt: action["receivedAt"],
                code: action["code"],
                message: action["message"]
            };
        case SYS_EVENTS.GETCESGROUPDATA:
            return {
                ...state,
                isFetching: false,
                didInvalidate: false,
                ces_group: action["ces_group"],
                updateTime: action["updateTime"],
                receivedAt: action["receivedAt"],
                code: action["code"],
                message: action["message"]
            };
        default:
            return state;
    }
}


function optionReducer(state = defaultOption1, action) {
    switch (action.type) {

        case SYS_EVENTS.OPTION_INIT:
            return {
                ...state,
                isFetching: false,
                didInvalidate: false,
                option_type: action["option_type"],
                option_year: action["option_year"],
                option_sel: action["option_sel"],
                option_resolved_customer: action["option_resolved_customer"],
                option_resolved_sites: action["option_resolved_sites"],
                option_open_sites: action["option_open_sites"],
                option_map_state: action["option_map_state"],
                option_map_year: action["option_map_year"],
                code: 0,
                message: ""
            };

        default:
            return state;
            //break;
    }
}

function graphReducer(state = defaultGraph, action) {
    switch (action.type) {

        case SYS_EVENTS.REFRESH_TOP10_DATA:
            return Object.assign({}, state, {
                top10data: action.graphdata,

            });
        case SYS_EVENTS.REFRESH_RESOLVE_DATA:
            return Object.assign({}, state, {
                resolvedata: action.graphdata,

            });
        case SYS_EVENTS.REFRESH_OPEN_DATA:
            return Object.assign({}, state, {
                opendata: action.graphdata,

            });
        case SYS_EVENTS.REFRESH_MAP_DATA:
            return Object.assign({}, state, {
                ww_map: action.graphdata,

            });
        case SYS_EVENTS.REFRESH_WW_DATA:
            return Object.assign({}, state, {
                top10data: action.top10data,
                ww_map: action.mapdata,
            });
        case SYS_EVENTS.REFRESH_CERT_DATA:
            return Object.assign({}, state, {
                operator_cert_data: action.graphdata,
            });
        case SYS_EVENTS.REFRESH_FTA_DATA:
            return Object.assign({}, state, {
                ftadata: action.graphdata,
            });
        case SYS_EVENTS.REFRESH_CES_COUNTRY_DATA:
            return Object.assign({}, state, {
                ces_country_data: action.graphdata,
            });
        case SYS_EVENTS.REFRESH_CES_GROUP_DATA:
            return Object.assign({}, state, {
                ces_group_data: action.graphdata,
            });
        default:
            return state;
        //break;
    }
}


export {dataReducer, optionReducer, graphReducer};