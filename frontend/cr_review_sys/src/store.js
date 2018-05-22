import {createStore, applyMiddleware} from 'redux';
import crReviewReducer from './reducers/index';
import thunkMiddleware from 'redux-thunk';
import {
    createLogger
} from 'redux-logger';
import promise from 'redux-promise-middleware';
import cmnUtils from './util/index';

let middlewares = (cmnUtils.isProd())
    ? [promise(), thunkMiddleware]
    : [createLogger(), promise(), thunkMiddleware];

let store = createStore(crReviewReducer, applyMiddleware(...middlewares));

export default store;