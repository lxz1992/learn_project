import {
    GV,
    URL_STORE
} from '../constants';
import {
    getTeamCrTotalList,
    getdailyResolutionAccumulatedCount,
    crConvertToWeekInfoByDbDefinedDuration,
    addTotalForCountHash
} from './getHomeChartData';
import {
    getHomeTableData
} from './getHomeTableData';
import {
    daysBetween
} from './cr_datetime';
import {
    team2Group
} from '../show/loadFilterSort';
import store from '../store';
import {
    onCrlistChanged,
    onTeamCountChanged
} from '../actions/crlist';
import cmnUtils from '../util/index';

function notMatchcrClassStateFilter(cr, state) {
    let filterFieldMap = {
        crClassFilter: 'Class',
        crStateFilter: 'State'
    };
    for (let filterType in filterFieldMap) {
        if ((state[filterType] === null) || (state[filterType] === undefined)) {
            return false;
        }
        let crFilter = state[filterType];
        let crType = filterFieldMap[filterType];
        let thisFilterValue = cr[crType];
        if (crFilter[thisFilterValue] === undefined) {
            if ((crFilter['Others'] === undefined) || (crFilter['Others'] === 0)) {
                return true;
            }
        } else {
            if (crFilter[thisFilterValue] === 0) {
                return true;
            }
        }
    }
    return false;
}

function checkIfKeywordFilterMatch(checkText, keywordFilters, keywordFilterCombinedType) {
    let keywordHit = false;
    let restKeywordHash = {};
    let returnResult = false;
    let crNeedMatchedKeyword = [];

    if (checkText === undefined) {
        return false;
    }

    if (keywordFilters.length === 0) {
        return true;
    } else {
        crNeedMatchedKeyword = [].concat(keywordFilters);
    }

    for (let i = 0; i < crNeedMatchedKeyword.length; i++) {
        restKeywordHash[crNeedMatchedKeyword[i]] = '';
    }
    for (let i = 0; i < crNeedMatchedKeyword.length; i++) {
        if (crNeedMatchedKeyword[i].indexOf('||') >= 0) {
            let splitOrKeywordList = crNeedMatchedKeyword[i].split('||');
            for (let j = 0; j < splitOrKeywordList.length; j++) {
                if (checkText.indexOf(splitOrKeywordList[j]) >= 0) {
                    keywordHit = true;
                    delete restKeywordHash[crNeedMatchedKeyword[i]];
                }
            }
        } else if (crNeedMatchedKeyword[i].indexOf('&&') >= 0) {
            let splitAndKeywordList = crNeedMatchedKeyword[i].split('&&');
            let splitAndKeywordHash = {};
            for (let j = 0; j < splitAndKeywordList.length; j++) {
                splitAndKeywordHash[splitAndKeywordList[j]] = '';
                if (checkText.indexOf(splitAndKeywordList[j]) >= 0) {
                    delete splitAndKeywordHash[splitAndKeywordList[j]];
                }
            }
            if (Object.keys(splitAndKeywordHash).length === 0) {
                keywordHit = true;
                delete restKeywordHash[crNeedMatchedKeyword[i]];
            }
        }
        if (checkText.indexOf(crNeedMatchedKeyword[i]) >= 0) {
            keywordHit = true;
            delete restKeywordHash[crNeedMatchedKeyword[i]];
        }
    }
    crNeedMatchedKeyword = [];
    for (let restKeyword in restKeywordHash) {
        crNeedMatchedKeyword.push(restKeyword);
    }
    if (keywordFilterCombinedType === '&') {
        if (crNeedMatchedKeyword.length === 0) {
            returnResult = true;
        }
    } else { // GV.keywordFilterCombinedType == '+'
        if (keywordHit) {
            returnResult = true;
        }
    }

    return returnResult;
}

function notMatchKeywordFilter(cr, crkeywordfilter, keywordMergeType, curview) {
    if (curview === 'Home') {
        let matchkeyword = checkIfKeywordFilterMatch(cr['Title'], crkeywordfilter, keywordMergeType);
        return (!matchkeyword);
    } else {
        for (let i in GV.showField[curview]) {
            let field = GV.showField[curview][i];
            let value = cr[field];
            if (value === undefined) {
                value = '';
            }
            let matchkeyword = checkIfKeywordFilterMatch(value.toString(), crkeywordfilter, keywordMergeType);
            if (matchkeyword) {
                return false;
            }

        }
        return true;
    }
}

function notMatchedFilter(cr, state) {
    //console.log(JSON.stringify(cr));
    let curview = state.currentView;
    if (state.openDayMoreThan !== '') {
        if (cr['Open_Days'] < state.openDayMoreThan) {
            return true;
        }
    }

    if ((curview === 'Home') || (curview === 'CR List')) {
        if (state.crInDays !== '') {
            let sYear = parseInt(cr['Submit_Date'].substring(0, 4), 10);
            let sMon = parseInt(cr['Submit_Date'].substring(5, 7), 10);
            let sDay = parseInt(cr['Submit_Date'].substring(8, 10), 10);
            let sDate = new Date(sYear, sMon - 1, sDay);
            let todayDate = new Date();
            let thisCrSubmitDays = daysBetween(sDate, todayDate);
            if (thisCrSubmitDays > state.crInDays) {
                return true;
            }
        }
    }
    let classstatecheck = notMatchcrClassStateFilter(cr, state);
    if (classstatecheck) {
        return classstatecheck;
    }
    let crkeywordfilter = state.keywordFilters;
    let keywordMergeType = state.KeywordMergeType;
    let keywordcheck = notMatchKeywordFilter(cr, crkeywordfilter, keywordMergeType, curview);
    if (keywordcheck) {
        return keywordcheck;
    }
    if (((curview === 'CR Review') || (curview === 'CR Notify')) && (cr.Waived !== '0') && (cr.Waived !== 0) && (cr.Waived !== undefined) && (cr.Waived !== '')) {
        return true;
    } else if ((curview === 'Waived CR') && ((cr.Waived === 0) || (cr.Waived === '0') || (cr.Waived === undefined) || (cr.Waived === ''))) {
        return true;
    }
    return false;
}

function notMatchedTeamGroupFilter(teamname, currTeam, currGroup) {
    if (currTeam !== '') {
        if (teamname !== currTeam) {
            return true;
        }
    }

    var crgroup = team2Group(teamname);

    if (currGroup !== '') {
        if (crgroup !== currGroup) {
            return true;
        }
    }
    return false;
}

function parseResultData(infodata) {
    let result = {};
    let review_info = infodata.results;
    for (let i in review_info) {
        let item_info = review_info[i];
        if (result[item_info.cr_id] !== undefined) {
            result[item_info.cr_id].push(item_info);
        } else {
            result[item_info.cr_id] = [];
            result[item_info.cr_id].push(item_info);
        }

    }
    return result;
}

function isCropenByState(crstate) {
    for (let i in GV.openStateList) {
        let openState = GV.openStateList[i];
        if (crstate === openState) {
            return true;
        }
    }
    return false;
}

function parseReviewInfoComment(review_info_comment, crlist, currView, activity_id, state) {
    //console.log(JSON.stringify(crlist));
    let reiew_cr_list = {};
    let cr_review_info = parseResultData(review_info_comment.info);
    let cr_review_comment = parseResultData(review_info_comment.comments);
    for (let crid in crlist) {
        let cr = JSON.parse(JSON.stringify(crlist[crid]));
        let id = cr.id;
        let review_info = cr_review_info[id];
        if (review_info !== undefined) {
            review_info = review_info[0];
            cr.Waived = review_info.waived;
            cr.Importance = review_info.importance;
            cr.WarRoom = review_info.war_room;
            cr.Progress = review_info.progress;
            cr.Remark = review_info.remark;
            let json_additional_fields = review_info.additional_fields;
            if (typeof(json_additional_fields) === 'string') {
                if (json_additional_fields !== '') {
                    json_additional_fields = JSON.parse(json_additional_fields);
                } else {
                    json_additional_fields = {};
                }
            }
            for (let field in json_additional_fields) {
                cr[field] = json_additional_fields[field];
            }
            
            if (isCropenByState(cr.State)) {
                cr.Analysis = 'Ongoing';
            }
        }

        let review_comment = cr_review_comment[id];
        if (review_comment !== undefined) {
            let comments = '';
            for (let j in review_comment) {
                if (review_comment[j].review_comments !== '') {
                    let datestr = review_comment[j].update_time;
                    if ((datestr !== undefined) && (datestr !== null)) {
                        datestr = datestr.substring(0, 10);
                        datestr = datestr.replace(/-/g, '');
                    }
                    comments += '[' + datestr + ']\n';
                    comments += '[' + review_comment[j].login_name + ']';
                    comments += review_comment[j].review_comments + '\n\n';
                }
            }
            cr.Comment = comments;
        }
        reiew_cr_list[crid] = cr;
    }
    let crToProcessHash = [];
    let teamCrCount = {};
    for (let cr in reiew_cr_list) {
        if (notMatchedFilter(reiew_cr_list[cr], state)) {
            continue;
        }
        let thisTeam = reiew_cr_list[cr]['Assignee_Dept'];
        //if (thisTeam !== '') {
        if (teamCrCount[thisTeam] === undefined) {
            teamCrCount[thisTeam] = 0;
        }
        teamCrCount[thisTeam] += 1;
        //}
        let currTeam = state.currTeam;
        let currGroup = state.currGroup;
        if (notMatchedTeamGroupFilter(thisTeam, currTeam, currGroup)) {
            continue;
        }
        crToProcessHash.push(reiew_cr_list[cr]);
    }
    //console.log(JSON.stringify(teamCrCount));
    store.dispatch(onTeamCountChanged(teamCrCount));
    store.dispatch(onCrlistChanged(crToProcessHash));
}

function getReviewInfoAndParseCR(crlist, currView, activity_id, currDB, state) {
    let review_info_comment = {};
    let url = URL_STORE.CR_REVIEW.CR_REVIEW_INFO;
    if (cmnUtils.isProd()) {
        url += activity_id + '/?cr_db=' + currDB.join('/');
    }
    console.log(url);
    fetch(url, {credentials: 'include'})
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
                        url += activity_id + '/?cr_db=' + currDB.join('/');
                    }
                    fetch(url, {credentials: 'include'})
                        .then(
                            function (response) {
                                if (response.status !== 200) {
                                    alert('there is problem when fetching，status is：' + response.status);
                                    return '';
                                }
                                response.json().then(function (data2) {
                                    //console.log(JSON.stringify(data2));
                                    review_info_comment.comments = data2;
                                    parseReviewInfoComment(review_info_comment, crlist, currView, activity_id, state);
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

function parseAffectedCrInformation(state) {
    let result = {};
    let crdata = state.crlist.cr;
    let currView = state.currentView;
    let currDB = state.currentDB;
    let activity_name = state.currentActivity;
    let activity_id = state.activities.detail[activity_name].activity_id;
    getReviewInfoAndParseCR(crdata, currView, activity_id, currDB, state);
    
}

function isInOpenState(crState) {
    var isInOpenState = true;
    switch (crState) {
        case 'Resolved':
        case 'Verified':
        case 'Closed':
            isInOpenState = false;
            break;
        default:
            // including 'Submitted', 'Assigned', 'Working', 'Reworking'
            break;
    }
    return isInOpenState;
}

function parseGraphCrInformation(state) {
    let result = {};
    let dayTypeHash = {
        'Submit_Date': '',
        'Resolve_Date': '',
        'Verify_Date': '',
        'Close_Date': ''
    };
    let dayCountHash = {};
    let teamCrInfo = {};
    let crlist = state.affectedCrList;
    let currAvtivity = state.currentActivity;
    let allActivity = state.activities.detail;
    let activity_from_date = allActivity[currAvtivity].date_from;
    let activity_to_date = allActivity[currAvtivity].date_to;
    //console.log(JSON.stringify(crlist));
    let dailyResolutionCountHash = {};
    for (let i in crlist) {
        let cr = crlist[i];
        //for (let cr in crdata['cr']) {
        let thisTeam = cr['Assignee_Dept'];
        if (teamCrInfo[thisTeam] === undefined) {
            teamCrInfo[thisTeam] = {
                'Total CR': 0,
                'Open CR': 0
            };
        }

        teamCrInfo[thisTeam]['Total CR'] += 1;

        if (cr['Resolve_Date'].length <= 1) {
            teamCrInfo[thisTeam]['Open CR'] += 1;
        }

        for (let dayType in dayTypeHash) {
            if ((dayType === 'Resolve_Date') && (isInOpenState(cr['State']))) {
                // exclude re-open CRs
                continue;
            }
            let thatDate = cr[dayType];
            if (thatDate === ' ') {
                continue;
            }
            if (thatDate === undefined) {
                continue;
            }
            if (dayCountHash[thatDate] === undefined) {
                dayCountHash[thatDate] = {};
            }
            if (dayCountHash[thatDate][dayType] === undefined) {
                dayCountHash[thatDate][dayType] = 0;
            }
            dayCountHash[thatDate][dayType] += 1;

            if (dayType === 'Resolve_Date') {
                if (dailyResolutionCountHash[thatDate] === undefined) {
                    dailyResolutionCountHash[thatDate] = {};
                    for (let i = 0; i < GV.resolutionList.length; i++) {
                        let resol = GV.resolutionList[i];
                        dailyResolutionCountHash[thatDate][resol] = 0;
                    }
                }
                let thisCrResolution = cr['Resolution'];
                if (thisCrResolution !== '') {
                    dailyResolutionCountHash[thatDate][thisCrResolution] += 1;
                }
            }

            if ((dayType === 'Resolve_Date') && (cr['Resolution'] === 'Completed')) {
                if ((cr['Class'] === 'Bug') || (cr['Class'] === 'Change feature')) {
                    if (dayCountHash[thatDate]['Effective Check-in'] === undefined) {
                        dayCountHash[thatDate]['Effective Check-in'] = 1;
                    } else {
                        dayCountHash[thatDate]['Effective Check-in'] += 1;
                    }
                }
            }
        }
    }

    let homeTableData = getHomeTableData(crlist, state);
    //console.log(JSON.stringify(homeTableData));
    let teamCrTotalList = getTeamCrTotalList(teamCrInfo);
    let dailyResolutionAccumulatedCountHash = getdailyResolutionAccumulatedCount(dailyResolutionCountHash);
    let dayList = [];
    for (let crDate in dayCountHash) {
        dayList.push(crDate);
    }
    dayList.sort();
    let weekList = [];
    let weekCountHash = {};
    if ((activity_from_date !== null) && (activity_from_date !== '') && (activity_to_date !== null) && (activity_to_date !== null))
    {
        let weekResult = crConvertToWeekInfoByDbDefinedDuration(dayList, dayCountHash, activity_from_date, activity_to_date);
        weekList = weekResult.weekList;
        weekCountHash = weekResult.weekCountHash;
    }
    //console.log(JSON.stringify(teamCrTotalList));
    dayCountHash = addTotalForCountHash(dayCountHash);

    result.dayList = dayList;
    result.dayCountHash = dayCountHash;
    result.weekList = weekList;
    result.weekCountHash = weekCountHash;
    result.teamlist = teamCrTotalList.teamlist;
    result.teamcrlist = teamCrTotalList.teamcrlist;
    result.teamcrinfo = teamCrInfo;
    result.daylistforresolution = dailyResolutionAccumulatedCountHash.daylistforresolution;
    result.dailyresolutioncount = dailyResolutionAccumulatedCountHash.dailyresolutioncount;
    result.homeSummaryData = homeTableData.summaryCountData;
    result.homeClassStateData = homeTableData.ClassStateCountData;
    result.homeResolutioneData = homeTableData.ResolutionCountData;

    //console.log(JSON.stringify(result));
    return result;
}

export {
    parseAffectedCrInformation,
    parseGraphCrInformation
};