import store from '../store';
import {
    GV
} from '../constants';

const jq = jQuery.noConflict();

function loadFilterSort() {
    let state = store.getState();
    //console.log(JSON.stringify(state));
    let activity = state.currentActivity;
    if (activity === 'default-activity') {
        activity = state.activities["default"];
    }
    //console.log(JSON.stringify("curactivity:" + activity));
    let curview = state.currentView;
    //console.log(JSON.stringify("load filter curview:" + curview));
    jq('#crKeywordLabel').html('Keyword:');
    if ((curview !== 'Home') && (curview !== 'CR List')) {
        jq('.home-list').hide();
        jq('#crOpenDayLabel').html('Open');
        jq('.no-list').show();
        setCommentsSelect(state.currCommentView);
    } else {
        jq('.home-list').show();
        jq('#crOpenDayLabel').html('Submit');
        jq('.no-list').hide();
    }
    if (curview === 'Home') {
        jq('.nohome').hide();
        jq('#crKeywordLabel').html('CR Title Keyword:');
    } else {
        jq('.nohome').show();
        jq('.all-class').hide();
        jq('.all-state').hide();
        if (activity.indexOf('_Bug') >= 0) {
            jq('.bug').show();
            jq('.all-state').show();
        } else if (activity.indexOf('_NonBug') >= 0) {
            jq('.nobug').show();
            jq('.all-state').show();
        } else if ((activity.indexOf('Check-in') >= 0) | (activity.indexOf('Patch') >= 0)) {
            jq('.patch').show();
        } else {
            jq('.all-class').show();
            jq('.all-state').show();
        }
        setShowFilter(state);
        setCRFilter(state);
    }
}

function setShowFilter(state) {
    if (state.crTimeTracking) {
        jq("#timeCheckbox").attr("checked", true);
    } else {
        jq("#timeCheckbox").attr("checked", false);
    }
    if (state.showAnalysisField) {
        jq("#crAnalysisCheckbox").attr("checked", true);
    } else {
        jq("#crAnalysisCheckbox").attr("checked", false);
    }
    if (state.showRemarkField) {
        jq("#crRemarkCheckbox").attr("checked", true);
    } else {
        jq("#crRemarkCheckbox").attr("checked", false);
    }
    if (state.showMpTrackingField) {
        jq("#mpTrackingCheckbox").attr("checked", true);
    } else {
        jq("#mpTrackingCheckbox").attr("checked", false);
    }
}

function setCommentsSelect(commentview) {
    let adom = document.getElementsByName('commentViewRadio');
    for (let i = 0; i < adom.length; i++) {
        if (jq(adom[i]).attr('value') === commentview) {
            adom[i].checked = true;
        } else {
            adom[i].checked = false;
        }
    }
}

function setCRFilter(state) {
    let crclassfilter = state.crClassFilter;
    let crstatefilter = state.crStateFilter;
    if ((crclassfilter === null) | (crstatefilter === null)) {
        return;
    }
    jq('.crClassCheckbox').each(function () {
        let crFilterTypeVal = jq(this).val();
        if (crclassfilter[crFilterTypeVal]) {
            jq(this).prop('checked', true);
        } else {
            jq(this).prop('checked', false);
        }
    });

    jq('.crStateCheckbox').each(function () {
        let crFilterTypeVal = jq(this).val();
        if (crstatefilter[crFilterTypeVal]) {
            jq(this).prop('checked', true);
        } else {
            jq(this).prop('checked', false);
        }
    });
}

function refreshGroupTeamFilter() {
    console.log('refresh group team list ....');
    let state = store.getState();
    let curGroup = state.currGroup;
    let curTeam = state.currTeam;
    let teamcrcount = state.teamCrCount;
    let groupCrCount = getGroupCrCount(teamcrcount);
    loadGroupList(groupCrCount, curGroup);
    loadTeamList(teamcrcount, curGroup, curTeam, groupCrCount);
}

function team2Group(crTeam) {
    for (let group in GV.groupKeywordHash) {
        for (let i = 0; i < GV.groupKeywordHash[group].length; i++) {
            let groupKeyword = GV.groupKeywordHash[group][i];
            if (crTeam.indexOf(groupKeyword) >= 0) {
                return group;
            }
        }
    }
    return 'other';
}

function getGroupCrCount(teamcrcount) {
    let groupCrCount = {};
    for (let crTeam in teamcrcount) {
        let crGroup = team2Group(crTeam);
        if (groupCrCount[crGroup] === undefined) {
            groupCrCount[crGroup] = 0;
        }
        groupCrCount[crGroup] += teamcrcount[crTeam];
    }
    return groupCrCount;
}

function loadGroupList(groupCrCount, curGroup) {
    let groupSelDom = '';
    let allGroupCrCount = 0;
    let groupCount = 0;
    for (let crGroup in groupCrCount) {
        groupCount += 1;
        allGroupCrCount += groupCrCount[crGroup];
    }

    let selectedFlavor = '';
    let selectedClassFlavor = '';
    if (curGroup === '') {
        selectedFlavor = ' selected ';
        selectedClassFlavor = ' bgYellow ';
    }
    groupSelDom += '<option value="" class="groupSelectClass' + selectedClassFlavor + '"' + selectedFlavor + '> ' + groupCount + ' Groups (' + allGroupCrCount + ' CRs)</option>';
    let groupSelOption = [];
    for (let group in groupCrCount) {
        if (group === '') {
            continue;
        }
        let groupCount = groupCrCount[group];
        selectedFlavor = '';
        selectedClassFlavor = '';
        if (group === curGroup) {
            selectedFlavor = 'selected';
            selectedClassFlavor = 'bgLightYellow';
        }
        groupSelOption.push('<option value="' + group + '" class="groupSelectClass ' + selectedClassFlavor + '"' + selectedFlavor + '>' + group + ' (' + groupCount + ')</option>');
    }
    groupSelOption.sort();
    groupSelDom += groupSelOption;
    jq("#selectGroup").empty();
    //groupSelDom += '</select>';
    jq('#selectGroup').append(groupSelDom);

}

function loadTeamList(teamcrcount, curGroup, curTeam, groupCrCount) {
    console.log('current selected team' + curTeam);
    let teamSelDom = '';
    let selectedFlavor = '';
    let selectedClassFlavor = '';
    let findcurTeam = 0;
    if (curTeam === '') {
        selectedFlavor = ' selected ';
        selectedClassFlavor = ' bgYellow ';
    }
    let teamCount = 0;
    let allCrCount = 0;
    if (curTeam === '') {
        findcurTeam = 1;
    }
    for (let team in teamcrcount) {
        if (curGroup === '') {
            teamCount += 1;
        } else {
            if (team2Group(team) === curGroup) {
                teamCount += 1;
            }
        }
        allCrCount += teamcrcount[team];
    }
    let teamGroupFlavor = '';
    if (curGroup !== '') {
        teamGroupFlavor = curGroup;
        allCrCount = groupCrCount[curGroup];
    }
    teamSelDom += '<option value="" class="teamSelectClass' + selectedClassFlavor + '"' + selectedFlavor + '> ' + teamCount + ' <span id="teamGroupType"></span> ' + teamGroupFlavor + ' Teams (' + allCrCount + ' CRs)</option>';
    let teamSelOption = [];
    for (let team in teamcrcount) {
        if (team === '') {
            continue;
        }
        let teamCount = teamcrcount[team];
        selectedFlavor = '';
        selectedClassFlavor = '';

        if (curGroup === '') {
            teamSelOption.push('<option value="' + team + '" class="teamSelectClass ' + selectedClassFlavor + '"' + selectedFlavor + '>' + team + ' (' + teamCount + ')</option>');
        } else {
            if (assignedTeamGroupShouldBeFiltered(team, curGroup)) {} else {
                if (team === curTeam) {
                    selectedFlavor = 'selected';
                    selectedClassFlavor = 'bgLightYellow';
                    findcurTeam = 1;
                }
                console.log('current selected team' + team);
                teamSelOption.push('<option value="' + team + '" class="teamSelectClass ' + selectedClassFlavor + '"' + selectedFlavor + '>' + team + ' (' + teamCount + ')</option>');

            }
        }

    }
    console.log('current selected team ' + findcurTeam);
    teamSelOption.sort();
    teamSelDom += teamSelOption;
    jq("#selectTeam").empty();
    //groupSelDom += '</select>';
    jq('#selectTeam').append(teamSelDom);
    if (!findcurTeam) {
        console.log('not found selected team' + curTeam);
        jq('#selectTeam').trigger("change");
    }
}

function assignedTeamGroupShouldBeFiltered(team, curGroup) {
    let hitAssignedTeam = false;
    let inverseSelection = false;
    if (curGroup !== '') {
        if (curGroup.toLowerCase() === 'other') {
            inverseSelection = true;
            let teamKeywordList = [];
            for (let devAssignedToGroupKey in GV.groupKeywordHash) {
                teamKeywordList = jq.merge(teamKeywordList, GV.groupKeywordHash[devAssignedToGroupKey]);
            }
            for (let i = 0; i < teamKeywordList.length; i++) {
                let teamKeyword = teamKeywordList[i];
                if (team.indexOf(teamKeyword) >= 0) {
                    hitAssignedTeam = true;
                    break;
                }
            }
        } else {
            let teamKeywordList = GV.groupKeywordHash[curGroup];
            if (teamKeywordList !== undefined) {
                for (let i = 0; i < teamKeywordList.length; i++) {
                    let teamKeyword = teamKeywordList[i].toLowerCase();
                    if (team.indexOf(teamKeyword) >= 0) {
                        hitAssignedTeam = true;
                        break;
                    }
                }
            }
        }
    } else {
        return false;
    }

    if (inverseSelection) {
        if (hitAssignedTeam) {
            return true;
        }
        return false;
    }

    if (hitAssignedTeam) {
        return false;
    }
    return true;
}


export {
    loadFilterSort,
    refreshGroupTeamFilter,
    team2Group
};