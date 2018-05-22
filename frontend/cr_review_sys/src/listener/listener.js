import 'jquery';
import {
    onViewChanged,
    onActivityChanged

} from '../actions/index';
import store from '../store';
import './filter_listener';
import {
    activityConfig
} from '../show/activityConfig';

const jq = jQuery.noConflict();

jq(document).on('click', '.cr-sidebar .activity-item', (e) => {
    let activity = jq(e.currentTarget).text();
    store.dispatch(onActivityChanged(activity));

});

jq('[data-toggle="curView"').click((e) => {
    let state = store.getState();
    if (state.activityCategory.isFetching || state.crlist.isFetching || (state.currentActivity === 'default-activity') ||
        (state.currentActivityCategory.category_id === undefined)) {} else {
        let title = getItemDataTitle(e);
        console.log("change view: " + title + '  ' + new Date());
        store.dispatch(onViewChanged(title));
    }
});

function getItemDataTitle(e) {
    let self = e.currentTarget;
    return jq(self).data('title');
}

jq(document).on('click', '.cr-sidebar .config-activity-item', (e) => {
    let state = store.getState();
    let loginuser = state.loginUser.user.id;
    if (loginuser === undefined) {
        loginuser = '';
    }
    if (loginuser === '') {
        alert('You must login the system before you can use activity config!');
    }else {
        let activityid = jq(e.currentTarget).attr('data-value');
        activityConfig(activityid);
    }
});