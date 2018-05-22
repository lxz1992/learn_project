/* jslint node: true */
"use strict";

function updateSyncRelatedView(newVal, oldVal, objectPath, jq) {
    let state = newVal;
    jq('#btnUpdate').attr('disabled', state.isSyncing);
    let updating = 'update';
    let refreshing = 'glyphicon-refresh-animate';
    if (state.isSyncing) {
        updating = 'updating...';
        jq('#btnUpdate').addClass('disabled');
        jq('#md_icon_update_btn').addClass(refreshing);
    } else {
        jq('#btnUpdate').removeClass('disabled');
        jq('#md_icon_update_btn').removeClass(refreshing);
    }
    jq('#md_span_btn_update_txt').text(updating);
    jq('#lastestUpdate').html(state.latestSyncTime);
    jq('#spanMdSyncError').html(((state.errorMsg)
        ? `Fail to update source: ${state.errorMsg}`
        : ''));
}

export default updateSyncRelatedView;