import {createStore, applyMiddleware, compose} from 'redux';
import systemReducer from './reducers/index';
import thunkMiddleware from 'redux-thunk';
import {createLogger} from 'redux-logger';
import promise from 'redux-promise-middleware';
import {persistStore} from 'redux-persist';
import cmnUtils from './util/index';

let middlewares = (cmnUtils.isProd())
    ? [promise(), thunkMiddleware]
    : [createLogger(), promise(), thunkMiddleware];

export default() => {
    let store = createStore(systemReducer, applyMiddleware(...middlewares));
    let persistor = persistStore(store);
    return {store, persistor};
};