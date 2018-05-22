import '../actions/index';
import {
    SYS_EVENTS
} from '../actions/index';


let defaultState = {
    cr: {
        'default-state': ''
    },
    isFetching: false,
    status: "success",
    message: "",
    code: 0,
    ready: false
};

function crListReducer(state = defaultState, action) {
    switch (action.type) {
        case SYS_EVENTS.CR_LIST_REQ:
            return {
                ...state,
                isFetching: true
            };
        case SYS_EVENTS.CR_LIST_RESP:
            return ((action['code']) ? {
                ...state,
                code: action['code'],
                message: action['message'],
                isFetching: false,
                status: 'fail',
                ready: false
            } : {
                ...state,
                isFetching: false,
                cr: action["cr"],
                //updatedAt: action["updatedAt"],
                code: 0,
                message: "",
                ready: true
            });

        default:
            return state;
    }
}

function affectedCrListReducer(state = [], action) {
    switch (action.type) {
        case SYS_EVENTS.AFFECTEDCRLIST:
            return action.affectedCrList;
        default:
            return state;
    }
}

function TeamCRCountReducer(state = {}, action) {
    switch (action.type) {
        case SYS_EVENTS.TEAMCRCOUNT:
            return action.teamcrcount;
        default:
            return state;
    }
}

export {
    crListReducer,
    affectedCrListReducer,
    TeamCRCountReducer
};