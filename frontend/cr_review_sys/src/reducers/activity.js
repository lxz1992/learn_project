import '../actions/index';
import {
    SYS_EVENTS
} from '../actions/index';


let defaultState = {
    default: "",
    onGoing: [],
    finished: [],
    detail: {},
    isFetching: false,
    didInvalidate: false,
    status: "success",
    message: "",
    code: 0
};

function activitiesReducer(state = defaultState, action) {
    switch (action.type) {
        case SYS_EVENTS.ACTIOON_LIST_REQ:
            return {
                ...state,
                isFetching: true,
                didInvalidate: false
            };
        case SYS_EVENTS.ACTIOON_LIST_RESP:
            return ((action['code']) ? {
                ...state,
                code: action['code'],
                message: action['message'],
                isFetching: false,
                didInvalidate: false
            } : {
                ...state,
                isFetching: false,
                didInvalidate: false,
                default: action["default"],
                onGoing: action["onGoing"],
                finished: action["finished"],
                detail: action["detail"],
                receivedAt: action["receivedAt"],
                //updatedAt: action["updatedAt"],
                code: 0,
                message: ""
            });

        default:
            return state;
    }
}

let defaultCategoryState = {
    detail: {},
    isFetching: false,
    didInvalidate: false,
    status: "success",
    message: "",
    code: 0
};

function activityCategoryReducer(state = defaultCategoryState, action) {
    switch (action.type) {
        case SYS_EVENTS.ACTIVITYCATEGORY_LIST_REQ:
            return {
                ...state,
                isFetching: true,
                didInvalidate: false
            };
        case SYS_EVENTS.ACTIVITYCATEGORY_LIST_RESP:
            return ((action['code']) ? {
                ...state,
                code: action['code'],
                message: action['message'],
                isFetching: false,
                didInvalidate: false
            } : {
                ...state,
                isFetching: false,
                didInvalidate: false,
                detail: action["detail"],
                code: 0,
                message: ""
            });

        default:
            return state;
    }
}

export {
    activitiesReducer,
    activityCategoryReducer
};