import 'jquery';
import 'datatables.net';
import {
    COLOR
} from '../constants';
import {
    rotateCRCountData,
    getHomeCrCountByDate,
    getHomeCrCountByWeek
} from '../data/datasource_util';

const jq = jQuery.noConflict();

function loadSummaryTable(summarydata) {
    //console.log(JSON.stringify(summarydata));
    jq(document).find('.cr-content #home-result-summary-table').DataTable({
        paging: false,
        searching: false,
        processing: true,
        info: false,
        ordering: false,
        destroy: true,
        data: summarydata['summary'],
        columns: [{
                data: 'type'
            },
            {
                data: 'total'
            },
            {
                data: 'open'
            },
            {
                data: 'completed'
            }
        ]
    });

}

function loadClassStateTable(data) {
    //console.log(JSON.stringify(data));
    jq(document).find('.cr-content #home-result-class-state-table').DataTable({
        headerCallback: function (thead, data, start, end, display) {
            const stateColorMap = {
                "Class\\State": COLOR.MTK_GRAY,
                "Submitted": COLOR.MTK_RED,
                "Assigned": COLOR.MTK_RED,
                "Working": COLOR.MTK_RED,
                "Reworking": COLOR.MTK_RED,
                "Resolved": COLOR.MTK_GREEN,
                "Verified": COLOR.MTK_GREEN,
                "Closed": COLOR.MTK_GREEN,
                "Sum": COLOR.MTK_ORANGE
            };

            let states = jq(thead).find('th');
            for (let index = 0; index < states.length; index++) {
                let content = states[index].textContent;
                jq(states[index]).css({
                    'background-color': stateColorMap[content],
                    'color': COLOR.MTK_WHITE
                });
            }
        },
        createdRow: function (row, data, index) {
            const classColorMap = {
                'Class\\State': COLOR.MTK_GRAY,
                'Bug': COLOR.MTK_RED,
                'New feature': COLOR.MTK_GREEN,
                'Change feature': COLOR.MTK_GREEN,
                'Question': COLOR.MTK_GREEN,
                'Others': COLOR.MTK_GRAY,
                'Sum': COLOR.MTK_ORANGE
            };

            let clazz = jq(row).find('td:eq(0)');
            jq(clazz).css({
                'background-color': classColorMap[clazz.text()],
                'color': COLOR.MTK_WHITE
            });

            jq(row).find('td:last').css({
                'background-color': COLOR.MTK_LIGHT_ORANGE
            });

            if (data["class"] === "Sum") {
                jq(row).css({
                    'background-color': COLOR.MTK_LIGHT_ORANGE
                });
            }
        },
        paging: false,
        searching: false,
        processing: true,
        info: false,
        ordering: false,
        destroy: true,
        data: data["count"],
        columns: [{
                data: 'class'
            },
            {
                data: 'submitted'
            },
            {
                data: 'assigned'
            },
            {
                data: 'working'
            },
            {
                data: 'reworking'
            },
            {
                data: 'resolved'
            },
            {
                data: 'verified'
            },
            {
                data: 'closed'
            },
            {
                data: 'sum'
            }
        ]
    });
}

function loadResolutionTable(data) {
    let rowsName = {
        'count': 'Count',
        'percent': '%'
    };

    let datakeys = Object.keys(data);
    let checkkey = datakeys[0];
    let rowData = rotateCRCountData(data[checkkey], rowsName, 'Resolution');
    if (jq.fn.DataTable.isDataTable('#home-result-resolution-table')) {
        jq('#home-result-resolution-table').dataTable().fnDestroy();
        jq('#home-result-resolution-table').empty();
    }
    jq(document).find('.cr-content #home-result-resolution-table').DataTable({
        headerCallback: function (thead, data, start, end, display) {
            const stateColorMap = {
                'Sum': COLOR.MTK_ORANGE
            };

            let states = jq(thead).find('th');
            for (let index = 0; index < states.length; index++) {
                let content = states[index].textContent;
                if (stateColorMap[content] !== undefined) {
                    jq(states[index]).css({
                        'background-color': stateColorMap[content],
                        'color': COLOR.MTK_WHITE
                    });
                } else {
                    jq(states[index]).css({
                        'background-color': COLOR.MTK_DARK_GREEN,
                        'color': COLOR.MTK_WHITE
                    });
                }
            }
        },
        createdRow: function (row, data, index) {
            const classColorMap = {
                'Resolution': COLOR.MTK_DARK_GREEN,
                'Count': COLOR.MTK_DARK_GREEN,
                '%': COLOR.MTK_DARK_GREEN
            };

            let clazz = jq(row).find('td:eq(0)');
            jq(clazz).css({
                'background-color': classColorMap[clazz.text()],
                'color': COLOR.MTK_WHITE
            });

            jq(row).find('td:last').css({
                'background-color': COLOR.MTK_LIGHT_ORANGE
            });
        },
        paging: false,
        searching: false,
        processing: true,
        info: false,
        ordering: false,
        destroy: true,
        aaData: rowData.data,
        aoColumns: rowData.columns
    });
}

function loadCRCountTable(rowsName, Title, container, data) {
    //console.log(JSON.stringify(data));
    let rowData = rotateCRCountData(data[Title], rowsName, Title);
    //console.log(JSON.stringify(rowData));
    if (jq.fn.DataTable.isDataTable('#' + container)) {
        jq('#' + container).dataTable().fnDestroy();
        jq('#' + container).empty();
    }
    jq(document).find('.cr-content #' + container).DataTable({
        headerCallback: function (thead, data, start, end, display) {
            let states = jq(thead).find('th');
            for (let index = 0; index < states.length; index++) {
                jq(states[index]).css({
                    'background-color': COLOR.MTK_GRAY,
                    'color': COLOR.MTK_WHITE
                });
            }
        },
        createdRow: function (row, data, index) {
            if (data["type"] === "%") {
                jq(row).css({
                    'color': COLOR.MTK_GRAY_RED
                });
            }
        },

        paging: false,
        searching: false,
        processing: true,
        info: false,
        ordering: false,
        destroy: true,
        aaData: rowData.data,
        aoColumns: rowData.columns
    });

}


function loadCrDailyWeeklyCountTable(dayList, dayCountHash, weekList, weekCountHash) {
    let rowName = ['total', 'submit', 'resolve'];
    let rowNameCrFieldHash = {
        'total': 'Submit_Date',
        'submit': 'Submit_Date',
        'resolve': 'Resolve_Date'
    };
    let rowNameCountTypeHash = {
        'total': 'accumulated',
        'submit': 'daily',
        'resolve': 'daily'
    };
    let rowInfo = {
        'name': rowName,
        'field': rowNameCrFieldHash,
        'type': rowNameCountTypeHash
    };
    let crDailyCountData = getHomeCrCountByDate(dayList, dayCountHash, rowInfo);
    let crWeeklyCountData = getHomeCrCountByWeek(weekList, weekCountHash, rowInfo);
    let CRCountRowName = {
        'total': 'Total',
        'submit': 'Submit',
        'resolve': 'Resolve'
    };
    //console.log(JSON.stringify(crWeeklyCountData));
    loadCRCountTable(CRCountRowName, 'Date', 'home-result-daily-cr-table', crDailyCountData);
    loadCRCountTable(CRCountRowName, 'Week', 'home-result-week-cr-table', crWeeklyCountData);
}


function loadDAILYOPENCRTable(dayList, dayCountHash) {
    let rowName = ['non-resolved', 'resolved'];
    let rowNameCrFieldHash = {
        'non-resolved': 'Submit_Date-Resolve_Date',
        'resolved': 'Resolve_Date-Close_Date'
    };
    let rowNameCountTypeHash = {
        'non-resolved': 'accumulated',
        'resolved': 'accumulated'
    };
    let rowInfo = {
        'name': rowName,
        'field': rowNameCrFieldHash,
        'type': rowNameCountTypeHash
    };
    let DailyOpenCountData = getHomeCrCountByDate(dayList, dayCountHash, rowInfo);

    let DAILYOPENCRRowName = {
        'non-resolved': 'Non Resolved<br /><font color="#FF0000" size="1px">(To be Resolved)</font>',
        'resolved': 'Resolved<br /><font color="#FF0000" size="1px">(To be Verified/Closed)</font>'
    };

    loadCRCountTable(DAILYOPENCRRowName, 'Date', 'home-result-daily-open-cr-table', DailyOpenCountData);
}

function loadDAILYACCUMULATEDCRTable(dayList, dayCountHash) {

    let rowName = ['total', 'resolved', 'percent'];
    let rowNameCrFieldHash = {
        'total': 'Submit_Date',
        'resolved': 'Resolve_Date',
        'percent': 'resolved/total'
    };
    let rowNameCountTypeHash = {
        'total': 'accumulated',
        'resolved': 'accumulated',
        'percent': 'percent'
    };
    let rowInfo = {
        'name': rowName,
        'field': rowNameCrFieldHash,
        'type': rowNameCountTypeHash
    };
    let DailyACCUMULATEDCRData = getHomeCrCountByDate(dayList, dayCountHash, rowInfo);
    let ACCUMULATEDCRRowName = {
        'total': 'Total',
        'resolved': 'Resolved',
        'percent': '%'
    };

    loadCRCountTable(ACCUMULATEDCRRowName, 'Date', 'home-result-daily-accumulated-cr-table', DailyACCUMULATEDCRData);
}

function loadDAILYEFFECTIVECHECKINTable(dayList, dayCountHash, weekList, weekCountHash) {
    let rowName = ['resolved', 'effective', 'accumulated', 'percent'];
    let rowNameCrFieldHash = {
        'resolved': 'Resolve_Date',
        'effective': 'Effective Check-in',
        'accumulated': 'Effective Check-in',
        'percent': 'accumulated/resolved'
    };
    let rowNameCountTypeHash = {
        'resolved': 'accumulated',
        'effectiven': 'daily',
        'accumulated': 'accumulated',
        'percent': 'percent'
    };
    let rowInfo = {
        'name': rowName,
        'field': rowNameCrFieldHash,
        'type': rowNameCountTypeHash
    };
    let effectiveCheckinData = getHomeCrCountByDate(dayList, dayCountHash, rowInfo);
    let effectiveWeekCheckinData = getHomeCrCountByWeek(weekList, weekCountHash, rowInfo);
    let EFFECTIVECHECKINRowName = {
        'resolved': 'Resolved',
        'effective': 'Effective Check-in',
        'accumulated': 'Accumulated Check-in',
        'percent': '%'
    };
    //console.log(JSON.stringify(effectiveWeekCheckinData));
    loadCRCountTable(EFFECTIVECHECKINRowName, 'Date', 'home-result-daily-checkin-table', effectiveCheckinData);
    loadCRCountTable(EFFECTIVECHECKINRowName, 'Week', 'home-result-week-checkin-table', effectiveWeekCheckinData);
}

export {
    loadSummaryTable,
    loadClassStateTable,
    loadResolutionTable,
    loadCrDailyWeeklyCountTable,
    loadDAILYOPENCRTable,
    loadDAILYACCUMULATEDCRTable,
    loadDAILYEFFECTIVECHECKINTable
};