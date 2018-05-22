import "../../../node_modules/chosen-js/chosen.css";
import '../../../node_modules/jsoneditor/dist/jsoneditor.css';
import chosen from "../../../node_modules/chosen-js/chosen.jquery.js";
import JSONEditor from 'jsoneditor';
import cmnUtils from '../util/index';
import Cookies from 'js-cookie';

import {
    URL_STORE,
    CRTRACKINGOPTION
} from '../constants';
import {
    crGetTodayText
} from '../data/cr_datetime';
import {
    parseAffectedCrInformation
} from '../data/parsecrdata';
import store from '../store';

const jq = jQuery.noConflict();
let jsoneditor_additionalfield_def = {};
let jsoneditor_options = {
    mode: 'tree',
    modes: ['code', 'form', 'text', 'tree', 'view'], // allowed modes};
    onError: function (err) {
        alert(err.toString());
    }
};

function checkinputStatus() {
    let status = '';
    try {
        jsoneditor_additionalfield_def.get();
    } catch (err) {
        status += "User Defined Fields has invalid style: " + err;
    }
    return status;
}

function submitToServer(submitinfo) {
    let url = URL_STORE.CR_REVIEW.CR_REVIEW_SUBMIT;
    let csrftoken = Cookies.get('csrftoken');
    jq.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!cmnUtils.csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
    // console.log(url);
    jq.ajax({
        type: "POST",
        url: url,
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify(submitinfo),
        dataType: "json",
        success: function (message) {
            if (message > 0) {
                alert("submit sucess");
            }
            let state = store.getState();
            parseAffectedCrInformation(state);
        },
        error: function (message) {
            alert('fail to submit:' + JSON.stringify(message));
        },
        xhrFields: {
            withCredentials: true
        }
    });
}

function getSubmitInformation(review_info_comment) {
    let crid = jq("#selected-cr-id").html();
    let activity_id = jq("#activity-id").html();
    let iswaived = 0;
    let issync = 0;
    let remark = '';
    let comments = [];
    let importance = '';
    let warroom = '';
    let progress = '';
    let additional_fields = '';
    let reviewinfo = {};
    reviewinfo.updated_time = null;
    reviewinfo.activity_id = parseInt(activity_id);
    if (review_info_comment.info.results.length >= 1) {
        reviewinfo = review_info_comment.info.results[0];
    }

    if (jq('#iswaived').is(':checked')) {
        iswaived = 1;
    }
    //if (jq('#issynctowits').is(':checked')) {
    //    issync = 1;
    //}
    //if (jq('#isreviewed').is(':checked')) {
    //    reviewinfo.reviewed = 1;
    //}
    additional_fields = JSON.stringify(jsoneditor_additionalfield_def.get());
    remark = jq("#crremark").val();
    if (jq("#newcrreviewcomment").val() !== '') {
        comments.push(jq("#newcrreviewcomment").val());
    }
    importance = jq("#cr_analysis_importance").val();
    warroom = jq("#cr_analysis_warroom").val();
    progress = jq("#cr_analysis_progress").val();
    //let todayText = crGetTodayText();
    //todayText = todayText.replace(/-/g, '');
    //var reg = new RegExp("\\n\\[" + todayText + "\\] Review Comments:\\n\\[user\\]$", "mg");
    //comments = comments.replace(reg, '');

    reviewinfo.cr_id = crid;
    reviewinfo.waived = iswaived;
    reviewinfo.importance = importance;
    reviewinfo.war_room = warroom;
    reviewinfo.progress = progress;
    reviewinfo.remark = remark;
    //reviewinfo.sync_to_wits = issync;
    reviewinfo.additional_fields = additional_fields;
    reviewinfo.login_name = review_info_comment.user;
    reviewinfo.review_comments = comments;
    console.log(JSON.stringify(reviewinfo));
    return reviewinfo;
}

function initTrackingSeletion(type, initValue) {
    let container = 'cr_analysis_' + type;
    jq('#' + container).empty();
    let option_list = CRTRACKINGOPTION[type];
    let option_html = '';
    for (let key in option_list) {
        let value_text = key + '-' + option_list[key];
        option_html += "<option value='" + value_text + "'>" + value_text + "</option>";
    }
    //console.log(option_html);
    jq('#' + container).append(option_html);
    jq('#' + container).trigger("chosen:updated");
    if ((initValue !== undefined) && (initValue !== '')) {
        jq("#" + container + " [value='" + initValue + "']").attr('selected', 'selected');
        jq('#' + container).trigger("chosen:updated");
    }
}

function initUserDefinedFields(userdefinedfields) {
    let container = document.getElementById('cr_user_defined_additional_fields');
    jsoneditor_additionalfield_def = new JSONEditor(container, jsoneditor_options);
    if ((userdefinedfields !== undefined) && (userdefinedfields !== '')) {
        jsoneditor_additionalfield_def.set(userdefinedfields);
    }
}

function parseReviewInfoComment(crid, activity_id, review_info_comment) {
    let review_info_data = review_info_comment.info;
    let review_comment_data = review_info_comment.comments;
    jq('#selected-cr-id').html(crid);
    jq('#activity-id').html(activity_id.toString());
    jq('#labelNewComment').html('New Review Comments <font color="red">(Write your comment here)</font>:');
    let userdefinedfields = {};
    //console.log(review_info_data.results.length);
    if ((review_info_data.results === undefined) || (review_info_data.results.length < 1)) {
        review_info_data.results = [];
        let initReviewInfo = {
            //"sync_to_wits": null,
            "waived": "",
            "importance": "",
            "war_room": "",
            "progress": "",
            "remark": "",
            "updated_time": null,
            "activity_id": activity_id,
            //"reviewed": null,
            "additional_fields": ""
        };
        review_info_data.results.push(initReviewInfo);
    }
    let review_info = review_info_data.results[0];
    if (typeof (review_info.additional_fields) === 'string') {
        if (review_info.additional_fields !== '') {
            userdefinedfields = JSON.parse(review_info.additional_fields);
        }
    }
    let crimportance = review_info.importance;
    let crwarroom = review_info.war_room;
    let crprogress = review_info.progress;
    let crremark = review_info.remark;
    let iswaived = 0;
    //let issync = 0;
    //let isreviewed = review_info.reviewed;
    iswaived = review_info.waived;
    //issync = review_info.sync_to_wits;
    let crcomments = '';
    let review_comment = review_comment_data.results;
    if (review_comment !== undefined) {
        for (let j in review_comment) {
            if (review_comment[j].review_comments !== '') {
                let datestr = review_comment[j].update_time;
                if ((datestr !== undefined) && (datestr !== null)) {
                    datestr = datestr.substring(0, 10);
                    datestr = datestr.replace(/-/g, '');
                }
                crcomments += '[' + datestr + ']\n';
                crcomments += '[' + review_comment[j].login_name + ']';
                crcomments += review_comment[j].review_comments + '\n\n';
            }
        }
    }

    //let todayText = crGetTodayText();
    //todayText = todayText.replace(/-/g, '');
    //crcomments = crcomments + '\n[' + todayText + '] Review Comments:\n[user]';
    jq('#crreviewcomment').val(crcomments);
    jq('#newcrreviewcomment').val('');
    initTrackingSeletion('importance', crimportance);
    initTrackingSeletion('warroom', crwarroom);
    initTrackingSeletion('progress', crprogress);
    jq('#crremark').val('');
    if (crremark !== undefined) {
        jq('#crremark').val(crremark);
    }

    if ((iswaived === 1) || (iswaived === '1')) {
        jq("#iswaived").attr("checked", true);
    } else {
        jq("#iswaived").attr("checked", false);
    }
    /*if ((issync === 1) || (issync === '1')) {
        jq("#issynctowits").attr("checked", true);
    } else {
        jq("#issynctowits").attr("checked", false);
    }
    if ((isreviewed === 1) || (isreviewed === '1')) {
        jq("#isreviewed").attr("checked", true);
    } else {
        jq("#isreviewed").attr("checked", false);
    }*/

    initUserDefinedFields(userdefinedfields);

}

function initCrInfo(cr, activity_id, review_info_comment) {
    let crid = cr.id;
    //let crid_list = [];
    //crid_list.push(crid);

    let url = URL_STORE.CR_REVIEW.CR_REVIEW_INFO;
    if (cmnUtils.isProd()) {
        url += activity_id + '/?cr_id=' + crid;
    }
    console.log(url);
    fetch(url, {
            credentials: 'include'
        })
        .then(
            function (response) {
                if (response.status !== 200) {
                    alert('there is problem when fetching，status is：' + response.status);
                    return '';
                }
                response.json().then(function (data) {
                    //console.log(JSON.stringify(data));
                    review_info_comment.info = data;
                    url = URL_STORE.CR_REVIEW.CR_REVIEW_COMMENT;
                    if (cmnUtils.isProd()) {
                        url += activity_id + '/?cr_id=' + crid;
                    }
                    fetch(url, {
                            credentials: 'include'
                        })
                        .then(
                            function (response) {
                                if (response.status !== 200) {
                                    alert('there is problem when fetching，status is：' + response.status);
                                    return '';
                                }
                                response.json().then(function (data2) {
                                    //console.log(JSON.stringify(data2));
                                    review_info_comment.comments = data2;
                                    parseReviewInfoComment(crid, activity_id, review_info_comment);
                                });
                            }
                        )
                        .catch(function (err) {
                            alert('Fetch error:' + err);
                            return '';
                        });
                });
            }
        )
        .catch(function (err) {
            alert('Fetch error:' + err);
            return '';
        });
}


function showCrReviewWindow(cr, rowobj, activity_id, currUser) {
    //console.log(JSON.stringify(cr));
    let review_info_comment = {};
    review_info_comment.user = currUser;
    jq(function () {
        jq('#crReviewModal').modal({
            keyboard: true
        });
    });

    jq('#crReviewModal').one('shown.bs.modal', function (e) {
        jq(".chosen-select").chosen({
            width: "95%"
        });
        initCrInfo(cr, activity_id, review_info_comment);
    });
    jq('#crReviewModal').one('hide.bs.modal', function (e) {
        jsoneditor_additionalfield_def.destroy();
    });
    jq('#crReviewSubmit').one('click', function () {
        let status = checkinputStatus();
        let submitinfo = {};
        if (status !== '') {
            alert(status);
        } else {
            submitinfo = getSubmitInformation(review_info_comment);
            submitToServer(submitinfo);
        }
        jq('#crReviewModal').modal('hide');
    });
}

export {
    showCrReviewWindow
};