import {
    GV,
    VIEWHINT,
    URL_STORE
} from '../constants';

import {
    loadColumnChkBox,
    loadListDataTables
} from '../show/crList.js';
import cmnUtils from '../util/index';
const jq = jQuery.noConflict();

function extTableColumns(allFields, userdefinedWitsFields, userdefinedTodoFields, crFields) {
    let result = {};
    let all_display_name = GV.fieldRename;
    let index = 30;
    if ((userdefinedWitsFields === '') || (userdefinedWitsFields ===null) || (userdefinedWitsFields === undefined)) {
        userdefinedWitsFields = {};
    }
    if ((userdefinedTodoFields === '') || (userdefinedTodoFields ===null) || (userdefinedTodoFields === undefined)) {
        userdefinedTodoFields = {};
    }
    if (typeof(userdefinedWitsFields) === 'string') {
        userdefinedWitsFields = JSON.parse(userdefinedWitsFields);
    }
    if (typeof(userdefinedTodoFields) === 'string') {
        userdefinedTodoFields = JSON.parse(userdefinedTodoFields);
    }
    for (let witfield in userdefinedWitsFields) {
        let defined_fields = userdefinedWitsFields[witfield];
        for (let field_name in defined_fields) {
            allFields[field_name] = index;
            index = index + 1;
            let display_name = defined_fields[field_name];
            if (field_name !== display_name) {
                all_display_name[field_name] = display_name;
            }
        } 
    }
    for (let field_name in userdefinedTodoFields) {
        allFields[field_name] = index;
        index = index + 1;
        let display_name = userdefinedTodoFields[field_name];
        if (field_name !== display_name) {
            all_display_name[field_name] = display_name;
        }
    }
    result.defined_fields = allFields;
    result.display_name = all_display_name;
    //console.log(JSON.stringify(result));
    return result;
}

function extShowFields(crTimeTracking, showAnalysisField, showMpTrackingField, showRemarkField, currView) {
    let showField = GV.showField[currView];
    if (crTimeTracking) {
        showField.push('Submit_DateTimeNum');
        showField.push('Assign_DateTimeNum');
        showField.push('Resolve_DateTimeNum');
    }
    if (showMpTrackingField) {
        showField.push('Importance');
        showField.push('WarRoom');
        showField.push('Progress');
    }
    if (showAnalysisField) {
        showField.push('Analysis');
    }
    if (showRemarkField) {
        showField.push('Remark');
    }
    return showField;
}

function refreshCRListPage(state) {
    console.log('start refresh crlist:' + new Date());
    let crlist = state.affectedCrList;
    jq('#crlist_count').html('Count=' + crlist.length);
    let currView = state.currentView;
    let currAvtivity = state.currentActivity;
    let allActivity = state.activities.detail;
    let userdefinedWitsFields = allActivity[currAvtivity].user_defined_fields1;
    let userdefinedTodoFields = allActivity[currAvtivity].user_defined_fields2;
    let bugDays = allActivity[currAvtivity].days_of_bug;
    let otherDays = allActivity[currAvtivity].days_of_others;
    let activity_id = allActivity[currAvtivity].activity_id;
    let allFields = GV.fieldColumn;
    let crTimeTracking = state.crTimeTracking;
    let showAnalysisField = state.showAnalysisField;
    let showMpTrackingField = state.showMpTrackingField;
    let showRemarkField = state.showRemarkField;
    let oneCrField = crlist[0];
    let currUser = state.loginUser.user.id;
    if (currUser === undefined) {
        currUser = '';
    }
    if (currView === 'CR Notify') {
        let viewhint = VIEWHINT[currView];
        viewhint += '<font color="red"> Open Bug CR(s) assigned > ' + bugDays + ' days and others > ' + otherDays + ' days are red highlighted.</font>';
        jq('#viewHint').html(viewhint);
    }
    allFields = extTableColumns(allFields, userdefinedWitsFields, userdefinedTodoFields, oneCrField);
    let showfields = extShowFields(crTimeTracking, showAnalysisField, showMpTrackingField, showRemarkField, currView);
    loadColumnChkBox(allFields.defined_fields, currView, allFields.display_name);
    //getReviewInfoAndLoadCrList(crlist, allFields.defined_fields, currView, showfields, bugDays, otherDays, activity_id, allFields.display_name, currDB, currUser);
    //loadListDataTables(crlist, allFields, currView, showfields, bugDays, otherDays, activity_id);
    loadListDataTables(crlist, allFields.defined_fields, currView, showfields, bugDays, otherDays, activity_id, allFields.display_name, currUser);
}

export default refreshCRListPage;