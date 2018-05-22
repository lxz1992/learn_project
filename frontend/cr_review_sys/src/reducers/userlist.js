import '../actions/index';
import {
    SYS_EVENTS
} from '../actions/index';


let defaultState = {
    user_list: [],
    isFetching: false,
    didInvalidate: false,
    status: "success",
    message: "",
    code: 0
};

function userListReducer(state = defaultState, action) {
    switch (action.type) {
        case SYS_EVENTS.USER_LIST_REQ:
            return {
                ...state,
                isFetching: true,
                didInvalidate: false
            };
        case SYS_EVENTS.USER_LIST_RESP:
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
                user_list: action["user_list"],
                receivedAt: action["receivedAt"],
                updatedAt: action["updatedAt"],
                code: 0,
                message: ""
            });

        default:
            return state;
    }
}

let defaultUserState = {
    user: [],
    isFetching: false,
    didInvalidate: false,
    status: "success",
    message: "",
    code: 0
};

function loginUserReducer(state = defaultUserState, action) {
    switch (action.type) {
        case SYS_EVENTS.CURRENTUSER_LIST_REQ:
            return {
                ...state,
                isFetching: true,
                didInvalidate: false
            };
        case SYS_EVENTS.CURRENTUSER_LIST_RESP:
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
                user: action["user"],
                code: 0,
                message: ""
            });

        default:
            return state;
    }
}

export {
    userListReducer,
    loginUserReducer
};