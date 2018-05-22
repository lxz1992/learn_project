import store from '../store';
import refreshHomePage from './datasource_home';
import refreshCRListPage from './datasource_cr_list';
import {
    CR_VIEW
} from '../constants';
import {
    parseGraphCrInformation
} from './parsecrdata';

function refreshPage() {
    let state = store.getState();
    // console.log("refresh data: " + state.currentView + "  " + state.currentDB);
    if (state.currentView === CR_VIEW.HOME) {
        console.log(new Date());
        let crdata = parseGraphCrInformation(state);
        console.log(new Date());
        refreshHomePage(crdata);
        console.log(new Date());
    } else {
        refreshCRListPage(state);
    }
}

export {
    refreshPage
};