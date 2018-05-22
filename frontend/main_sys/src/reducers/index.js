/* jslint node: true */
"use strict";

import * as actions from '../actions/index';
import Consts from '../constants';
import userInfoReducer from './login';
import {persistCombineReducers} from 'redux-persist';
import storageSession  from 'redux-persist/lib/storage/session';

let availableSys = {
  availSys: [Consts.SYSTEMS.CR_REVEW, Consts.SYSTEMS.MD_ANALYSIS]
};
let actviveSys = {
  active: ""
};

function availableSysReducer(state = availableSys, action) {
  switch (action.type) {
      // to-do: fetch available systems
    default:
      return state;
  }
}

function actviveSysReducer(state = actviveSys, action) {
  switch (action.type) {
    case actions.SYS_EVENTS.SYS_CHANGED:
      return {active: action.sys};
    default:
      return state;
  }
}

const config = {
  key: 'root',
  storage: storageSession,
  debug: true
};

const systemReducer = persistCombineReducers(config, {
  "SYSTEMS": availableSysReducer,
  "ACTIVE_SYS": actviveSysReducer,
  "USER_PROFILE": userInfoReducer
});

export default systemReducer;