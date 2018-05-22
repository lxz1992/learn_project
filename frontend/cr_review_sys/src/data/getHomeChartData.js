import {
    GV
} from '../constants';
import {
    crGetYearWeekListByDate,
    crGetYearFromDate,
    crGetWeekOfYearFromDate,
    sprintf
} from './cr_datetime';

function getTeamCrTotalList(teamCrInfo) {
    let teamCrList = [];
    let teamCrTotalList = [];
    let teamInfo = {};
    for (let team in teamCrInfo) {
        teamCrList.push([team, teamCrInfo[team]['Total CR']]);
    }
    teamCrList.sort(function (a, b) {
        return b[1] - a[1];
    });
    let teamList = [];
    for (let i = 0; i < teamCrList.length; i++) {
        teamList.push(teamCrList[i][0]);
    }
    for (let i = 0; i < teamList.length; i++) {
        let team = teamList[i];
        let teamTotalCrCount = teamCrInfo[team]['Total CR'];
        let teamOpenCrCount = teamCrInfo[team]['Open CR'];
        teamCrTotalList.push([teamTotalCrCount, teamOpenCrCount]);
    }
    //console.log(teamCrTotalList);
    teamInfo['teamlist'] = teamList;
    teamInfo['teamcrlist'] = teamCrTotalList;
    return teamInfo;
}

function getdailyResolutionAccumulatedCount(dailyResolutionCountHash) {
    let dayListForResolution = [];
    let dailyResolutionAccumulatedCountHash = {};
    for (let crDate in dailyResolutionCountHash) {
        dayListForResolution.push(crDate);
    }
    dayListForResolution.sort();
    let totalResolutionCountHash = {};
    for (let i = 0; i < GV.resolutionList.length; i++) {
        let resol = GV.resolutionList[i];
        totalResolutionCountHash[resol] = 0;
    }
    let accumulatedTotal = 0;
    for (let i = 0; i < dayListForResolution.length; i++) {
        let thatDate = dayListForResolution[i];
        dailyResolutionAccumulatedCountHash[thatDate] = {};
        let dailyTotal = 0;
        for (let resolution in dailyResolutionCountHash[thatDate]) {
            if (!(isNaN(dailyResolutionCountHash[thatDate][resolution]))) {
                dailyTotal += dailyResolutionCountHash[thatDate][resolution];
                totalResolutionCountHash[resolution] += dailyResolutionCountHash[thatDate][resolution];
                dailyResolutionAccumulatedCountHash[thatDate][resolution] = totalResolutionCountHash[resolution];
            }
        }
        accumulatedTotal += dailyTotal;
        dailyResolutionAccumulatedCountHash[thatDate]['Total Resolved'] = accumulatedTotal;
    }
    let result = {
        'daylistforresolution': dayListForResolution,
        'dailyresolutioncount': dailyResolutionAccumulatedCountHash
    };
    return result;
}

function crConvertToWeekInfoByDbDefinedDuration(dayList, dayCountHash, activityStartDate, activityEndDate) {
    //console.log('activityStartDate = ', activityStartDate);
    //console.log('activityEndDate = ', activityEndDate);

    let weekList = crGetYearWeekListByDate(activityStartDate, activityEndDate);
    return crConvertToWeekInfo(weekList, dayList, dayCountHash);
}

function crConvertToWeekInfo(weekList, dayList, dayCountHash) {
    let weekResult = {
        'weekList': [],
        'weekCountHash': {}
    };
    let weekCountHash = {};
    // initalize weekCountHash

    for (let i = 0; i < weekList.length; i++) {
        let yearWeekText = weekList[i];
        weekCountHash[yearWeekText] = {};
        for (let analysisField in GV.crStatisticFieldHash) {
            weekCountHash[yearWeekText][analysisField] = 0;
            weekCountHash[yearWeekText]['Total ' + analysisField] = 0;
        }
        weekCountHash[yearWeekText]['Total Open'] = 0;
    }
    let prevWeek = '';
    for (let i = 0; i < dayList.length; i++) {
        let thatDate = dayList[i];
        let thatYear = crGetYearFromDate(thatDate);
        let thatWeek = crGetWeekOfYearFromDate(thatDate);
        if (thatWeek === 53) {
            thatYear = '' + (parseInt(thatYear) + 1);
            thatWeek = 1;
        }
        let yearWeekText = sprintf('W%s.%02d', String(thatYear).substring(2, 4), thatWeek);
        if ($.inArray(yearWeekText, weekList) < 0) {
            continue;
        }
        prevWeek = thatWeek;
        if ($.inArray(yearWeekText, weekList) >= 0) {
            for (let analysisField in dayCountHash[thatDate]) {
                weekCountHash[yearWeekText][analysisField] += dayCountHash[thatDate][analysisField];
            }
        }
    }
    for (let i = 0; i < weekList.length; i++) {
        let yearWeekText = weekList[i];
        //if (i <= $.inArray(thisYearWeek, weekList)) {
        let breakNext = false;
        for (let j = 0; j < weekList.length; j++) {
            if (breakNext) {
                break;
            }
            let currWeekText = weekList[j];
            if (currWeekText === yearWeekText) {
                breakNext = true;
            }
            for (let analysisField in GV.crStatisticFieldHash) {
                weekCountHash[yearWeekText]['Total ' + analysisField] += weekCountHash[currWeekText][analysisField];
            }
        }
        weekCountHash[yearWeekText]['Total Open'] = weekCountHash[yearWeekText]['Total Submit_Date'] - weekCountHash[yearWeekText]['Total Resolve_Date'];
        //} else {
        //    for (let analysisField in GV.crStatisticFieldHash) {
        //        weekCountHash[yearWeekText][analysisField] = null;
        //        weekCountHash[yearWeekText]['Total ' + analysisField] = null;
        //    }
        //    weekCountHash[yearWeekText]['Total Open'] = null;
        //}
    }
    weekResult['weekList'] = weekList;
    weekResult['weekCountHash'] = weekCountHash;

    return weekResult;
}

function addTotalForCountHash(dayCountHash) {
    let newDateCountHash = $.extend(true, {}, dayCountHash);
    let dateList = [];
    for (let date in dayCountHash) {
        dateList.push(date);
    }
    dateList.sort();

    let myTotalCount = {};
    for (let analysisField in GV.crStatisticFieldHash) {
        myTotalCount['Total ' + analysisField] = 0;
    }

    for (let i = 0; i < dateList.length; i++) {
        let date = dateList[i];
        for (let analysisField in GV.crStatisticFieldHash) {
            if (newDateCountHash[date][analysisField] === undefined) {
                newDateCountHash[date][analysisField] = 0;
            }
            myTotalCount['Total ' + analysisField] += newDateCountHash[date][analysisField];
            newDateCountHash[date]['Total ' + analysisField] = myTotalCount['Total ' + analysisField];
        }
        newDateCountHash[date]['Total Open'] = newDateCountHash[date]['Total Submit_Date'] - newDateCountHash[date]['Total Resolve_Date'];
    }
    return newDateCountHash;
}


export {
    getTeamCrTotalList,
    getdailyResolutionAccumulatedCount,
    crConvertToWeekInfoByDbDefinedDuration,
    addTotalForCountHash
};