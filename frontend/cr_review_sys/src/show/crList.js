import 'jquery';
import 'datatables.net';
import {
    GV
} from '../constants';
import {
    showCrReviewWindow
} from './crReview';
const jq = jQuery.noConflict();

function loadColumnChkBox(allFields, currView, all_display_name) {
    let htmlStr = '';
    let additionalField = [10, 16, 19, 24, 25, 26, 27, 28];
    for (let field in allFields) {
        let checkTag = '';
        if (GV.showField[currView].indexOf(field) >= 0) {
            checkTag = 'checked';
        }
        let column_num = allFields[field];
        if (additionalField.indexOf(column_num) < 0) {
            if (all_display_name[field] !== undefined) {
                field = all_display_name[field];
            }
            htmlStr += `<input type="checkbox" class="column-toggle-vis" data-column="${column_num}" ${checkTag}><span class="column-filtet-span">${field}&nbsp</span>`;
        }
    }
    jq('#crcolumnChkBox').html(htmlStr);
}

function parseCrTableData(crlist, allFields, currView, all_display_name) {
    let resultData = {};
    let columns = [];
    let data = [];

    for (let field in allFields) {
        let crcolumn = {};
        let showTag = true;
        let title = field;
        //if (GV.showField[currView].indexOf(field) >= 0) {
        //    showTag = true;
        //}
        if (all_display_name[field] !== undefined) {
            title = all_display_name[field];
        }
        if (field === 'id') {
            crcolumn.class = 'classCRID';
            crcolumn.render = function (data) {
                return '<a href="#">' + data + '</a>';
            };
        }
        if ((field === 'Assignee_Dept') || (field === 'Assignee_Name')) {
            crcolumn.class = 'classPeopleFinder';
            crcolumn.render = function (data) {
                return '<a href="#">' + data + '</a>';
            };
        }
        field = field.replace(".", "");
        crcolumn.data = field;
        crcolumn.title = title;
        crcolumn.visible = showTag;
        columns.push(crcolumn);
    }
    for (let i in crlist) {
        let cr = crlist[i];
        let crdata = {};
        for (let field in allFields) {
            let fieldValue = cr[field];
            field = field.replace(".", "");
            if (fieldValue !== undefined) {
                crdata[field] = fieldValue;
            } else {
                crdata[field] = 'None';
            }
        }
        data.push(crdata);
    }
    resultData.columns = columns;
    resultData.data = data;
    return resultData;

}

function defineColumns() {
    let columnsdef = [];
    let defitem = {
        'sClass': 'crcolumn_tracking',
        'aTargets': [24, 25, 26]
    };
    columnsdef.push(defitem);
    defitem = {
        'sClass': 'crcolumn_remark',
        'aTargets': [28]
    };
    columnsdef.push(defitem);
    defitem = {
        'sClass': 'crcolumn_analysis',
        'aTargets': [27]
    };
    columnsdef.push(defitem);
    defitem = {
        'sClass': 'crcolumn_time',
        'aTargets': [10, 16, 19]
    };
    columnsdef.push(defitem);
    return columnsdef;
}

function loadListDataTables(crlist, allFields, currView, showfields, bugDays, otherDays, activity_id, all_display_name, currUser) {
    console.log('start parse cr table data:' + new Date());
    let rowData = parseCrTableData(crlist, allFields, currView, all_display_name);
    //console.log(JSON.stringify(rowData));
    let columndef = defineColumns();
    if (jq.fn.DataTable.isDataTable('#crreviewFilteredList')) {
        jq('#crreviewFilteredList').dataTable().fnDestroy();
        jq('#crreviewFilteredList').empty();
    }
    console.log('start load datatables:' + new Date());

    let CRTable = jq('#crreviewFilteredList').DataTable({
        headerCallback: function (thead, data, start, end, display) {

        },

        createdRow: function (row, data, index) {
            //console.log(JSON.stringify(data));
            let isFlavorCr = false;
            if (data.Class === 'Bug') {
                let clazz = jq(row).find('td:eq(0)');
                jq(clazz).attr('class', 'crColorFlavor');
                clazz = jq(row).find('td:eq(3)');
                jq(clazz).attr('class', 'crColorFlavor');

                let daysText = data.Assign_Days;
                if (daysText > bugDays) {
                    clazz = jq(row).find('td:eq(15)');
                    jq(clazz).attr('class', 'crColorFlavor');
                    isFlavorCr = true;
                }
                daysText = data.Open_Days;
                if (daysText > bugDays) {
                    clazz = jq(row).find('td:eq(9)');
                    jq(clazz).attr('class', 'crColorFlavor');
                    isFlavorCr = true;
                }
                daysText = data.Resolve_Days;
                if (daysText > bugDays) {
                    clazz = jq(row).find('td:eq(18)');
                    jq(clazz).attr('class', 'crColorFlavor');
                    isFlavorCr = true;
                }
            } else {
                let daysText = data.Assign_Days;
                let clazz = '';
                if (daysText > otherDays) {
                    clazz = jq(row).find('td:eq(15)');
                    jq(clazz).attr('class', 'crColorFlavor');
                    isFlavorCr = true;
                }
                daysText = data.Open_Days;
                if (daysText > otherDays) {
                    clazz = jq(row).find('td:eq(9)');
                    jq(clazz).attr('class', 'crColorFlavor');
                    isFlavorCr = true;
                }
                daysText = data.Resolve_Days;
                if (daysText > otherDays) {
                    clazz = jq(row).find('td:eq(18)');
                    jq(clazz).attr('class', 'crColorFlavor');
                    isFlavorCr = true;

                }
            }
            if ((currView === 'CR Notify') && (isFlavorCr)) {
                jq(row).css({
                    'background-color': '#ffaaaa'
                });
            }
            try {
                var showLocal = '';
                var isNwIndependent = data.User_Field3.substring(0, 1);
                if (isNwIndependent === 'Y') {
                    showLocal = '--';
                } else if (isNwIndependent === 'N') {
                    showLocal = 'Local';
                    if ((currView === 'CR Review') || (currView === 'Waived CR')) {
                        showLocal = 'Local<br>當地<br>複製';
                    }
                }
                let clazz = jq(row).find('td:eq(5)');
                jq(clazz).attr('class', 'crColorFlavor');
                jq(clazz).html(showLocal);
            } catch (e) {
                // bypass
            }
        },
        paging: false,
        searching: false,
        //processing: true,
        info: false,
        destroy: true,
        aaData: rowData.data,
        aoColumns: rowData.columns,
        aoColumnDefs: columndef
    });
    console.log('end load datatables:' + new Date());

    for (let field in allFields) {
        let showTag = false;
        if (showfields.indexOf(field) >= 0) {
            showTag = true;
        }
        let column_num = GV.fieldColumn[field];
        if (!showTag) {
            let column = CRTable.column(column_num);
            column.visible(showTag);
        }
    }
    console.log('hide some columns:' + new Date());
    jq('.column-toggle-vis').on('change', function (e) {
        e.preventDefault();
        let column = CRTable.column(jq(this).attr('data-column'));
        column.visible(!column.visible());
    });

    jq('.filterCrColumns').on('change', function (e) {
        e.preventDefault();
        let checkboxValue = jq(this).attr('value');
        let showTag = false;
        if (jq(this).is(':checked')) {
            showTag = true;
        }
        let mapField = checkboxValue.split(',');
        for (let i in mapField) {
            let column_num = mapField[i];
            let column = CRTable.column(column_num);
            column.visible(showTag);
        }
    });

    jq('#crreviewFilteredList tbody').off('click');
    jq('#crreviewFilteredList tbody').on('click', 'tr td.classPeopleFinder', function (e) {
        let baseUrl = GV.wePeopleFinderKeywordPage;
        let keyword = jq(e.target).html();
        keyword = getLinkText(keyword);
        let linkUrl = baseUrl + keyword;
        window.open(linkUrl);
    });
    jq('#crreviewFilteredList tbody').on('click', 'tr td.classCRID', function (e) {
        let PatchID = jq(e.target).html();
        PatchID = getLinkText(PatchID);
        let preID = PatchID.substr(0, PatchID.length - 8);
        let baseUrl = GV.webCqLink[preID];
        let linkUrl = baseUrl + PatchID;
        window.open(linkUrl);
    });

    jq('#crreviewFilteredList tbody').on('dblclick', 'tr', function () {
        if ((currView === 'CR Review') || (currView === 'Waived CR')) {
            if (currUser === '') {
                alert('You must login before you can review the cr!');
            } else {
                let table = jq('#crreviewFilteredList').dataTable();
                let selectCR = table.fnGetData(this);
                console.log(JSON.stringify(selectCR));
                if ((selectCR !== undefined) && (selectCR !== null)) {
                    showCrReviewWindow(selectCR, this, activity_id, currUser);
                }
            }
        }
    });
}


function getLinkText(strText) {
    strText = strText.replace('<a href="#">', '');
    strText = strText.replace('</a>', '');
    return strText;
}

export {
    loadColumnChkBox,
    loadListDataTables
};