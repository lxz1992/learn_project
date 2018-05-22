import "../../../node_modules/chosen-js/chosen.css";
import '../../../node_modules/jsoneditor/dist/jsoneditor.css';
import chosen from "../../../node_modules/chosen-js/chosen.jquery.js";
import  JSONEditor  from  "jsoneditor";
import cmnUtils from '../util/index';
import Cookies from 'js-cookie';
import store from '../store';
import {
    fetchActivityCategory
} from '../actions/activity';

import {
    URL_STORE,
    CR_DB,
    CONFIG_ADDITIONAL_LIST
} from '../constants';
import {
    crGetTodayText
} from '../data/cr_datetime';

const jq = jQuery.noConflict();
let activityinfo = {};
let jsoneditor_query_def = null;
let jsoneditor_witsfield_def = null;
let jsoneditor_todofield_def = null;
let jsoneditor_options = {
    mode: 'tree',
    modes: ['code', 'form', 'text', 'tree', 'view'], // allowed modes};
    onError: function (err) {
        alert(err.toString());
    }
};

jq("#configCancel").click(function () {
    jsoneditor_query_def.destroy();
    jsoneditor_witsfield_def.destroy();
    jsoneditor_todofield_def.destroy();
    jsoneditor_query_def = null;
    jsoneditor_witsfield_def = null;
    jsoneditor_todofield_def = null;
    jq('#activity-config-div').hide();
    jq('.cr_review_form').show();
});

jq("#configSubmit").click(function () {
    let status = checkinputStatus();
    if (status !== '') {
        alert(status);
    } else {
        getSubmitInformation();
        //jq('#activity-config-div').hide();
        //jq('.cr_review_form').show();
        submitToServer();
    }

});

function checkinputStatus() {
    let status = '';
    if (isNaN(jq('#config-bug-day').val())) {
        status = 'The definition of Max Assign Day for Bug must be number.\n';
    }
    if (isNaN(jq('#config-others-day').val())) {
        status += 'The definition of Max Assign Day for Others must be number.\n';
    }
    try {
        jsoneditor_query_def.get();
    } catch (err) {
        status += "QueryDefine has invalid style: " + err;
    }
    try {
        jsoneditor_witsfield_def.get();
    } catch (err) {
        status += "User Defined Fields from Wits has invalid style: " + err;
    }
    try {
        jsoneditor_todofield_def.get();
    } catch (err) {
        status += "User Defined Fields in My Todo has invalid style: " + err;
    }
    return status;
}

function submitToServer() {
    let url = URL_STORE.CR_REVIEW.ADMIN_CONFIG_SUBMIT;
    /* workaround for full object uploading
    if (cmnUtils.isProd()) {
        let activity_id = jq('#selected-activity-id').text();
        let m = /ID:(\d+)/g.exec(activity_id);
        console.log(`extract activity id: < ${m[1]} > `);
        url += `{m[1]}/`;
    }
    */
    let csrftoken = Cookies.get('csrftoken');
    jq.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!cmnUtils.csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
    jq.ajax({
        type: "POST",
        url: url,
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify(activityinfo),
        dataType: "json",
        success: function (message) {
            if (message > 0) {
                alert("submit sucess");
            }
            store.dispatch(fetchActivityCategory());
            jq("#configCancel").click();
        },
        error: function (message) {
            alert('fail to submit:' + JSON.stringify(message));
        },
        xhrFields: {
            withCredentials: true
        }
    });
}

function getSubmitInformation() {
    activityinfo.date_from = jq("#config-date-from").val();
    activityinfo.date_to = jq("#config-date-to").val();
    activityinfo.db_scope = jq("#config-db-list").val();
    if (jq('#activityactive').is(':checked')) {
        activityinfo.active = 1;
    } else {
        activityinfo.active = 0;
    }
    activityinfo.db_scope = JSON.stringify(jsoneditor_query_def.get());
    //activityinfo.query_def = jq('#config-query-def').val();
    activityinfo.owner = jq("#config-owner-list").val().join();
    activityinfo.days_of_bug = jq('#config-bug-day').val();
    activityinfo.days_of_others = jq('#config-others-day').val();
    activityinfo.additional_mail_to = jq("#config-mailto-list").val().join();
    activityinfo.additional_mail_cc = jq("#config-ccto-list").val().join();
    if (jq('#istoassignee').is(':checked')) {
        activityinfo.mail_to_assignee = 1;
    } else {
        activityinfo.mail_to_assignee = 0;
    }
    if (jq('#istomanager').is(':checked')) {
        activityinfo.mail_to_manager = 1;
    } else {
        activityinfo.mail_to_manager = 0;
    }
    //activityinfo.user_defined_field = jq("#config-note").val();
    activityinfo.user_defined_fields1 = JSON.stringify(jsoneditor_witsfield_def.get());
    activityinfo.user_defined_fields2 = JSON.stringify(jsoneditor_todofield_def.get());
    activityinfo.mail_trigger_time = jq("#trigger_schedule").val();
    let additional_info = {
        'Time': 0,
        'Analysis': 0,
        'Tracking': 0,
        'Remark': 0,
        'Comments': 0
    };
    for (let showinfo in CONFIG_ADDITIONAL_LIST) {
        let lowinfo = CONFIG_ADDITIONAL_LIST[showinfo];
        let obj_id = 'config-notify-' + lowinfo;
        if (jq('#' + obj_id).is(':checked')) {
            additional_info[showinfo] = 1;
        }
    }
    if (typeof(activityinfo.additional_mail_fields) === 'string') {
        activityinfo.additional_mail_fields = JSON.parse(activityinfo.additional_mail_fields);
    }
    for (let showinfo in activityinfo.additional_mail_fields) {
        if (additional_info[showinfo] === undefined) {
            delete activityinfo.additional_mail_fields[showinfo];
        }
    }
    if (jq('#config-notify-others').is(':checked')) {
        let notify_other_fields = jq("#notify_additional_other_field").val();
        let defined_fields = notify_other_fields.split(',');
        for (let i in defined_fields) {
            let field = defined_fields[i];
            additional_info[field] = 1;
        }
    }
    activityinfo.additional_mail_fields = JSON.stringify(additional_info);
    console.log(JSON.stringify(activityinfo));
}

function initUserList() {
    let state = store.getState();
    let userinfo = state.allusers;
    if ((!(userinfo.isFetching)) && (!(userinfo.code)) && (userinfo.message === '')) {
        let user_html = '';
        let user_list = userinfo.user_list;
        jq('#config-mailto-list').empty();
        jq('#config-ccto-list').empty();
        jq('#config-owner-list').empty();
        //jq('#config-mailto-list').chosen("destroy");
        //jq('#config-ccto-list').chosen("destroy");
        //jq('#config-owner-list').chosen("destroy");
        for (let i = 0; i < user_list.length; i++) {
            user_html += "<option value='" + user_list[i].login_name + "'>" + user_list[i].full_name + "</option>";
        }
        //console.log(user_html);
        jq('#config-mailto-list').append(user_html);
        jq('#config-mailto-list').trigger("chosen:updated");
        jq('#config-ccto-list').append(user_html);
        jq('#config-ccto-list').trigger("chosen:updated");
        jq('#config-owner-list').append(user_html);
        jq('#config-owner-list').trigger("chosen:updated");
        if (activityinfo.additional_mail_to !== undefined) {
            let mail_to_str = activityinfo.additional_mail_to;
            let mail_to_list = mail_to_str.split(',');
            let length = mail_to_list.length;
            let value = '';
            for (let i = 0; i < length; i++) {
                value = mail_to_list[i];
                jq("#config-mailto-list" + " [value='" + value + "']").attr('selected', 'selected');
            }
            jq('#config-mailto-list').trigger("chosen:updated");
        }

        if (activityinfo.additional_mail_cc !== undefined) {
            let mail_to_str = activityinfo.additional_mail_cc;
            let mail_to_list = mail_to_str.split(',');
            let length = mail_to_list.length;
            let value = '';
            for (let i = 0; i < length; i++) {
                value = mail_to_list[i];
                jq("#config-ccto-list" + " [value='" + value + "']").attr('selected', 'selected');
            }
            jq('#config-ccto-list').trigger("chosen:updated");
        }

        if (activityinfo.owner !== undefined) {
            let owner_str = activityinfo.owner;
            let owner_list = owner_str.split(',');
            let length = owner_list.length;
            let value = '';
            for (let i = 0; i < length; i++) {
                value = owner_list[i];
                jq("#config-owner-list" + " [value='" + value + "']").attr('selected', 'selected');
            }
            jq('#config-owner-list').trigger("chosen:updated");
        }
    }
}
/*
function initDBScope() {
    let db_html = '';
    jq('#config-db-list').empty();
    //jq('#config-db-list').chosen("destroy");
    for (let dbname in CR_DB) {
        db_html += "<option value='" + CR_DB[dbname] + "'>" + CR_DB[dbname] + "</option>";
    }
    //console.log(user_html);
    jq('#config-db-list').append(db_html);
    jq('#config-db-list').trigger("chosen:updated");
    if (activityinfo.db_scope !== undefined) {
        let db_list = activityinfo.db_scope;
        let length = db_list.length;
        let value = '';
        for (let i = 0; i < length; i++) {
            value = db_list[i];
            jq("#config-db-list" + " [value='" + value + "']").attr('selected', 'selected');
        }
        jq('#config-db-list').trigger("chosen:updated");
    }

}*/

function initQueryDef() {
    //console.log('jsoneditor_query_def is defined:' + JSON.stringify(jsoneditor_query_def));
    let container = document.getElementById('config-query-def');
    if (jsoneditor_query_def === null) {
        jsoneditor_query_def = new JSONEditor(container, jsoneditor_options);
    }
    if ((activityinfo.db_scope !== undefined) && (activityinfo.db_scope !== '') && (activityinfo.db_scope !== null)) {
        let defined_json = activityinfo.db_scope;
        if (typeof(defined_json) === 'string') {
            defined_json = JSON.parse(defined_json);
        }
        jsoneditor_query_def.set(defined_json);
    } else {
        jsoneditor_query_def.set({});
    }
}

function initFieldFromWits() {
    let container = document.getElementById('config-wits-field');
    if (jsoneditor_witsfield_def === null) {
        jsoneditor_witsfield_def = new JSONEditor(container, jsoneditor_options);
    }
    //jsoneditor_witsfield_def = new JSONEditor(container, jsoneditor_options);
    if ((activityinfo.user_defined_fields1 !== undefined) && (activityinfo.user_defined_fields1 !== '') && (activityinfo.user_defined_fields1 !== null)) {
        let defined_json = activityinfo.user_defined_fields1;
        if (typeof(defined_json) === 'string') {
            console.log(`output user defined: ${defined_json}`);
            defined_json = JSON.parse(defined_json);
        }
        jsoneditor_witsfield_def.set(defined_json);
    } else {
        jsoneditor_witsfield_def.set({});
    }
}

function initFieldInTodo() {
    let container = document.getElementById('config-todo-field');
    if (jsoneditor_todofield_def === null) {
        jsoneditor_todofield_def = new JSONEditor(container, jsoneditor_options);
    }
    //jsoneditor_todofield_def = new JSONEditor(container, jsoneditor_options);
    if ((activityinfo.user_defined_fields2 !== undefined) && (activityinfo.user_defined_fields2 !== '') && (activityinfo.user_defined_fields2 !== null)) {
        let defined_json = activityinfo.user_defined_fields2;
        if (typeof(defined_json) === 'string') {
            defined_json = JSON.parse(defined_json);
        }
        jsoneditor_todofield_def.set(defined_json);
    } else {
        jsoneditor_todofield_def.set({});
    }
}

function initNotifyAdditionalInfo() {
    let htmlStr = '';
    for (let showinfo in CONFIG_ADDITIONAL_LIST) {
        let info = CONFIG_ADDITIONAL_LIST[showinfo];
        //console.log(info + '---' + showinfo);
        htmlStr += '<div class="form-check form-check-inline col-sm-2 col-md-2">';
        htmlStr += '<input class="form-check-input" type="checkbox" id="config-notify-' + info + '" value="' + showinfo + '">';
        htmlStr += '<label class="form-check-label" for="config-notify-' + info + '">' + showinfo + '</label>';
        htmlStr += '</div>';
    }
    //console.log(htmlStr);
    if (htmlStr !== '') {
        jq('#config-notify-additional-info').html(htmlStr);
    }
    let notify_other_fields = '';
    if ((activityinfo.additional_mail_fields !== undefined) && (activityinfo.additional_mail_fields !== '') && (activityinfo.additional_mail_fields !== '')) {
        if (typeof(activityinfo.additional_mail_fields) === 'string') {
            activityinfo.additional_mail_fields = JSON.parse(activityinfo.additional_mail_fields);
        }
        //console.log(JSON.stringify(activityinfo.additional_mail_fields))
        for (let info in activityinfo.additional_mail_fields) {
            if (CONFIG_ADDITIONAL_LIST[info] !== undefined) {
                let lowinfo = CONFIG_ADDITIONAL_LIST[info];
                let obj_id = 'config-notify-' + lowinfo;
                if (activityinfo.additional_mail_fields[info] == 1) {
                    jq("#" + obj_id).attr("checked", true);
                } else {
                    jq("#" + obj_id).attr("checked", false);
                }
            } else {
                if ((activityinfo.additional_mail_fields[info] !== undefined) && (activityinfo.additional_mail_fields[info])) {
                    if (notify_other_fields === '') {
                        notify_other_fields = info;
                    } else {
                        notify_other_fields += ',' + info;
                    }
                }
            }
        }
    }
    jq("#notify_additional_other_field").val(notify_other_fields);
    if (jq('#config-notify-others').is(':checked')) {
        jq("#notify_additional_other_field").removeAttr("readOnly");
    } else {
        jq("#notify_additional_other_field").attr("readOnly", "readonly");
    }
    jq('#config-notify-others').change(function () {
        if (jq(this).is(':checked')) {
            jq("#notify_additional_other_field").removeAttr("readOnly");
        } else {
            jq("#notify_additional_other_field").attr("readOnly", "readonly");
        }
    });
}

function initActivityInfo() {
    let user_info = {};
    let user_list = [];
    initNotifyAdditionalInfo();
    initUserList();
    //initDBScope();
    initQueryDef();
    initFieldFromWits();
    initFieldInTodo();
    jq('#config-bug-day').val('');
    jq('#config-others-day').val('');
    jq('#config-note').val('');
    jq('#trigger_schedule').val('');
    jq('#config-query-def').val('');
    let activity_show = '';
    if (activityinfo.activity_id !== undefined) {
        activity_show += '<font color="blue">ID:</font>' + activityinfo.activity_id;
    }
    if (activityinfo.activity_name !== undefined) {
        activity_show += '<font color="blue">&nbsp&nbsp&nbsp&nbsp&nbsp&nbspName:</font>' + activityinfo.activity_name;
    }
    if (activityinfo.activity_category_name !== undefined) {
        activity_show += '<font color="blue">&nbsp&nbsp&nbsp&nbsp&nbsp&nbspCategery:</font>' + activityinfo.activity_category_name;
    }
    if (activity_show !== '') {
        jq('#selected-activity-id').html(activity_show);
    }
    if ((activityinfo.date_from !== undefined) && (activityinfo.date_from !== '')) {
        let match = /((\d+)-(\d+)-(\d+)).*/g.exec(activityinfo.date_from);
        // print the log, we don't check if it matched, if not matched we prefer exception than error value.
        console.log(`date from: ${match[1]}`);
        jq("#config-date-from").val(match[1]);
    } else {
        let nowdate = crGetTodayText();
        jq("#config-date-from").val(nowdate);
    }
    if ((activityinfo.date_to !== undefined) && (activityinfo.date_to !== '')) {
        let match = /((\d+)-(\d+)-(\d+)).*/g.exec(activityinfo.date_to);
        // print the log, we don't check if it matched, if not matched we prefer exception than error value.
        console.log(`date to: ${match[1]}`);
        jq("#config-date-from").val();
        jq("#config-date-to").val(match[1]);
    } else {
        let nowdate = crGetTodayText();
        jq("#config-date-to").val(nowdate);
    }
    if ((activityinfo.active !== undefined) && (activityinfo.active)) {
        jq("#activityactive").attr("checked", true);
    } else {
        jq("#activityactive").attr("checked", false);
    }
    //if (activityinfo.query_def !== undefined) {
    //    jq('#config-query-def').val(activityinfo.query_def);
    //}
    if (activityinfo.days_of_bug !== undefined) {
        jq('#config-bug-day').val(activityinfo.days_of_bug);
    }
    if (activityinfo.days_of_others !== undefined) {
        jq('#config-others-day').val(activityinfo.days_of_others);
    }

    if ((activityinfo.mail_to_assignee !== undefined) && (activityinfo.mail_to_assignee)) {
        jq("#istomanager").attr("checked", true);
    } else {
        jq("#istomanager").attr("checked", false);
    }
    if ((activityinfo.mail_to_manager !== undefined) && (activityinfo.mail_to_manager)) {
        jq("#istomanager").attr("checked", true);
    } else {
        jq("#istomanager").attr("checked", false);
    }
    //if (activityinfo.user_defined_field !== undefined) {
    //    jq('#config-note').val(activityinfo.user_defined_field);
    //}
    if (activityinfo.mail_trigger_time !== undefined) {
        jq('#trigger_schedule').val(activityinfo.mail_trigger_time);
    }
}

function loadActivityInfo(activity) {
    jq('#selected-activity-id').html(activity);
    let url = URL_STORE.CR_REVIEW.ACTIVITY_CONFIG;
    if (cmnUtils.isProd()) {
        url += activity + '/';
    }
    console.log(url);
    fetch(url, {credentials: 'include'})
        .then(
            function (response) {
                if (response.status !== 200) {
                    alert('there is problem when fetching，status is：' + response.status);
                    return;
                }
                response.json().then(function (data) {
                    //console.log("return data.......");
                    activityinfo = data;
                    initActivityInfo(data);

                });
            }
        )
        .catch(function (err) {
            alert('Fetch error:' + err);
        });
}

function activityConfig(activity) {

    //console.log(JSON.stringify(state));
    console.log('config activity ID:' + activity);
    jq('.cr_review_form').hide();
    jq('#activity-config-div').show();
    jq(".multi-select").chosen({
        width: "95%"
    });
    loadActivityInfo(activity);
}

export {
    activityConfig
};