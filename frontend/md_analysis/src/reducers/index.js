/* jslint node: true */
"use strict";

import { combineReducers } from 'redux';
import * as actions from '../actions/index';
import { MD_VIEW } from '../constants';
import { dataReducer, optionReducer, graphReducer } from './mddata';
import { syncStatusReducer } from './update_src_reducer';



function view(state = MD_VIEW.STATISTICS, action) {
  // redux:  function (state, action)
  switch (action.type) {
    case actions.SYS_EVENTS.VIEW_CHANGED:
      return action.view;
    default:
      return state;
  }
}

const mdReviewReducer = combineReducers({
  currentView: view,
  data: dataReducer,
  option: optionReducer,
  graphdata: graphReducer,
  syncStatus: syncStatusReducer
});

export default mdReviewReducer;