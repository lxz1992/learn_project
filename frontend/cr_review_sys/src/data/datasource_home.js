import 'jquery';
import 'datatables.net';
import {
    GV
} from '../constants';
import {
    loadCrDailyCountChart,
    loadCrWeeklyCountChart,
    loadCountByTeamChart
} from '../show/cr_chart';
import {
    loadSummaryTable,
    loadClassStateTable,
    loadResolutionTable,
    loadCrDailyWeeklyCountTable,
    loadDAILYOPENCRTable,
    loadDAILYACCUMULATEDCRTable,
    loadDAILYEFFECTIVECHECKINTable
} from '../show/homeTables';

const jq = jQuery.noConflict();

function refreshHomePage(crdata) {
    console.log('== refreshHomePage');
    let summaryData = crdata.homeSummaryData;
    loadSummaryTable(summaryData);
    let classStateData = crdata.homeClassStateData;
    loadClassStateTable(classStateData);
    let resolutionData = crdata.homeResolutioneData;
    //console.log(JSON.stringify(crdata));
    loadResolutionTable(resolutionData);

    let dayList = crdata.dayList;
    let dayCountHash = crdata.dayCountHash;
    let weekList = crdata.weekList;
    let weekCountHash = crdata.weekCountHash;
    //console.log(JSON.stringify(weekList));
    //console.log(JSON.stringify(weekCountHash));
    loadCrDailyWeeklyCountTable(dayList, dayCountHash, weekList, weekCountHash);
    loadDAILYOPENCRTable(dayList, dayCountHash);
    loadDAILYACCUMULATEDCRTable(dayList, dayCountHash);
    loadDAILYEFFECTIVECHECKINTable(dayList, dayCountHash, weekList, weekCountHash);
    let analysisFieldList = ['Submit_Date', 'Resolve_Date', 'Total Submit_Date', 'Total Resolve_Date', 'Total Open'];
    let option_type = {
        0: 'column',
        1: 'column',
        2: 'spline',
        3: 'spline',
        4: 'spline'
    };
    let option_color = {
        0: 'gray',
        1: '#6abe25',
        2: 'gray',
        3: '#6abe25',
        4: '#d72185'
    };
    loadCrDailyCountChart('Daily CR Trend', 'plotChartCrDailyCountContainer', dayList, dayCountHash, analysisFieldList, ['Daily Submitted', 'Daily Resolved', 'Total Submitted', 'Total Resolved', 'Total Open'], {
        'weekly-or-daily': 'daily',
        'type': option_type,
        'color': option_color
    });
    loadCrWeeklyCountChart('Weekly CR Trend', 'plotChartCrWeekCountContainer', weekList, weekCountHash, analysisFieldList, ['Weekly Submitted', 'Weekly Resolved', 'Total Submitted', 'Total Resolved', 'Total Open'], {
        'weekly-or-daily': 'weekly',
        'type': option_type,
        'color': option_color
    });
    loadCrWeeklyCountChart('Weekly Effective Check-in', 'plotChartCrWeekCheckinContainer', weekList, weekCountHash, ['Resolve_Date', 'Effective Check-in', 'Total Submit_Date', 'Total Resolve_Date', 'Total Effective Check-in'], ['Weekly Resolved', 'Weekly Effective Check-in', 'Total CRs', 'Total Resolved', 'Total Effective Check-in'], {
        'weekly-or-daily': 'weekly',
        'type': option_type,
        'color': option_color
    });
    let teamList = crdata.teamlist;
    let teamCrTotalList = crdata.teamcrlist;
    let teamcrinfo = crdata.teamcrinfo;
    let plotOption = {
        'xlabel': 'Teams',
        'type': {
            0: 'column',
            1: 'column'
        },
        'color': {
            0: 'gray',
            1: 'red'
        }
    };
    loadCountByTeamChart('CR Count by Team', 'plotChartCrByTeamContainer', teamList, teamCrTotalList, plotOption, teamcrinfo);

    let dayListForResolution = crdata.daylistforresolution;
    let dailyResolutionAccumulatedCountHash = crdata.dailyresolutioncount;
    analysisFieldList = jq.merge(jq.merge([], GV.resolutionList), ['Total Resolved']);
    plotOption = {
        'weekly-or-daily': 'daily',
        'stacking': 'normal',
        'splineLabels': false,
        'type': {
            0: 'column',
            1: 'column',
            2: 'column',
            3: 'column',
            4: 'spline'
        },
        'color': {
            0: '#6abe25',
            1: '#d72185',
            2: 'gray',
            3: '#f7b101',
            4: '#555555'
        }
    };
    loadCrDailyCountChart('Daily Accumulated Resolution Trend', 'plotChartDailyResolutionContainer', dayListForResolution, dailyResolutionAccumulatedCountHash,
        analysisFieldList, analysisFieldList, plotOption);
    console.log('refresh home page done');

}




export default refreshHomePage;