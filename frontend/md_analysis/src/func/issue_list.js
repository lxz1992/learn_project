import config from '../config';

const jq = jQuery.noConflict();

function initColumnCheck() {
    let checked_column = {
        1: true,
        2: true,
        3: true,
        4: true,
        9: true,
        14: true
    }
    jq('.toggle-vis').each(function () {
        let column_num = jq(this).attr('data-column');
        if (checked_column[column_num]) {
            jq(this).prop('checked', true);
        } else {
            jq(this).prop('checked', false);
        }
    });
}

function showIssueDataTable(list_filter) {
    //let URL = 'http://localhost:8080/resources/json/issuelist_test.json';
    let cfg = config.API;
    let URL = cfg.ISSUE_LIST + '?' + list_filter;
    console.log(URL);
    // Data Tables setting
    if (jq('#table_id_issue').hasClass('DataTable')) {
        let dttable = $('table_id_issue').DataTable();
        dttable.fnClearTable(); 
        dttable.fnDestroy(); 
    }
    let CRTable = jq('#table_id_issue').DataTable({

        //define column data
        'columns': [
            {
                'class': 'details-control',
                'orderable': false,
                'data': null,
                'defaultContent': ''
            },                          // Array Index(=Col Index+1)
            {
                'data': 0,                 //"CR ID"
                'class': 'classCRID',
                'render': function (data) {
                    return '<a href="#">' + data + '</a>';
                }
            },
            { 'data': 1 },              //"Title"  2
            {
                'data': 22,
                'class': 'classPatchID',
                'render': function (data) {
                    return '<a href="#">' + data + '</a>';
                }
            },                        //"Patch ID"
            { 'data': 6 },              //"Class" 
            { 'data': 13 },             //"Country"  5
            { 'data': 10 },             //"Operator" 
            { 'data': 3 },              //"Customer"
            { 'data': 4 },              //"Site"
            {
                'data': 5,                //"Assignee"  //14
                'class': 'classAssignee',
                'render': function (data) {
                    return '<a href="#">' + data + '</a>';
                }
            },
            { 'data': 9 },              //"Platform"                      
            { 'data': 11 },             //"RAT"  9
            { 'data': 12 },             //"Module"   10
            { 'data': 2 },              //"Priority"
            { 'data': 8 },              //"Submit Date"  12
            { 'data': 25 },             //"Assign Data"
            { 'data': 24 },             //"Project Name"
            { 'data': 16 },             //"RAT2"
            { 'data': 17 },             //"TAC/LAC"  
            { 'data': 18 },             //"Cell ID"
            { 'data': 19 },             //"Effort"
            { 'data': 20 },             //"CountryCode"
            { 'data': 7 },              //"State"
            { 'data': 21 },             //"Resolution"
            { 'data': 23 },             //"Solution"

        ],

        'columnDefs': [
            { width: 10, targets: 0 },
            { width: 90, targets: 1 },
            { width: 300, targets: 2 },
            //{ 'visible': false, 'targets': 13 },   //Site
            //{ 'visible': false, 'targets': 14 },   //Assignee
            { 'visible': false, 'targets': 5 },   //Country
            { 'visible': false, 'targets': 6 },   //Operator
            { 'visible': false, 'targets': 7 },   //customer
            { 'visible': false, 'targets': 8 },   //Dept
            { 'visible': false, 'targets': 10 },   //PLatform
            { 'visible': false, 'targets': 11 },   //RAT
            { 'visible': false, 'targets': 12 },   //Module
            { 'visible': false, 'targets': 13 },   //Priority
            { 'visible': false, 'targets': 16 },   //Assign Data
            { 'visible': false, 'targets': 15 },   //Project Name
            { 'visible': false, 'targets': 17 },   //RAT2
            { 'visible': false, 'targets': 18 },   //TAC/LAC
            { 'visible': false, 'targets': 19 },   //Cell ID
            { 'visible': false, 'targets': 20 },   //Effort
            { 'visible': false, 'targets': 21 },   //CountryCode
            { 'visible': false, 'targets': 22 },   //State
            { 'visible': false, 'targets': 23 },    //Patch
            { 'visible': false, 'targets': 24 }    //Solution
        ],
        fixedColumns: true,
        //select search
        initComplete: function () {
            CRTable.columns().every(function () {
                let blackIndexList = [0, 1, 2, 3, 5, 13, 14];
                let column = this;
                let header = jq(column.header());
                let idx = column.index();
                let selTD = header.parent().prev().children().eq(idx);
                if (jq.inArray(idx, blackIndexList) === -1) {
                    let sel_id = 'sel_' + idx;
                    jq('#' + sel_id).remove();
                    let select = jq('<select id="sel_' + idx + '" class="selFilter"><option value="">All</option></select>')
                        .appendTo(selTD)
                        .on('change', function () {
                            let valSel = jq(this).children('option:selected').val();
                            let val = jq.fn.dataTable.util.escapeRegex(valSel);
                            let idx = jq(this).attr('id').substring(4);
                            CRTable.columns(idx)
                                .search(val ? '^' + val + '$' : '', true, false)
                                .draw();
                        });
                    column.data().unique().sort().each(function (d) {
                        select.append('<option value="' + d + '">' + d + '</option>');
                    });
                }
            });

        },

        //retrieve data from server
        'ajax': {
            'url': URL
            //'type': "POST"
        },
        'deferRender': true,  //speed up loading data
        //sort by priority and submit date
        order: [[4, 'asc']],
        paging: true,
        bAutoWidth: false,
        scrollX: true,
        scrollY: '70vh',
        scrollCollapse: true,
        destroy: true,
    });
    jq('.toggle-vis').on('change', function (e) {
        e.preventDefault();
        //console.log(jq(this).attr('data-column'));
        let column = CRTable.column(jq(this).attr('data-column'));
        column.visible(!column.visible());
    });

    jq('#table_id_issue tbody').off('click');
    jq('#table_id_issue tbody').on('click', 'tr td.classCRID', function (e) {
        let baseUrl = 'http://mtkcqweb.mediatek.inc/mtkcqweb_WCX_SmartPhone_ALPS/mtk/sec/cr/cr_view.jsp?crId=';
        let PatchID = jq(e.target).html();
        let preID = PatchID.substr(0, 4);
        let linkUrl = baseUrl + PatchID;
        if (preID === 'MOLY' || preID === 'ALPS') {
            if (preID === 'MOLY') {
                baseUrl = 'http://mtkcqweb.mediatek.inc/mtkcqweb_WCX_FeaturePhone_MOLY/mtk/sec/cr/cr_view.jsp?crId=';
                linkUrl = baseUrl + PatchID;
            }
            window.open(linkUrl);
        }
    });

    jq('#table_id_issue tbody').on('click', 'tr td.classPatchID', function (e) {
        let baseUrl = 'http://mtkcqweb.mediatek.inc/mtkcqweb_WCX_FeaturePhone_MOLY/mtk/sec/cr/cr_view.jsp?crId=';
        let PatchID = jq(e.target).html();
        let preID = PatchID.substr(0, 4);
        let linkUrl = baseUrl + PatchID;
        if (preID === 'MOLY' || preID === 'ALPS') {
            if (preID === 'ALPS') {
                baseUrl = 'http://mtkcqweb.mediatek.inc/mtkcqweb_WCX_SmartPhone_ALPS/mtk/sec/cr/cr_view.jsp?crId=';
                linkUrl = baseUrl + PatchID;
            }
            window.open(linkUrl);
        }
    });

    jq('table').off('click', 'tr td.classAssignee');
    jq('table').on('click', 'tr td.classAssignee', function (e) {
        let baseUrl = 'http://peoplefinder.mediatek.inc/PeopleFinder/Home/SearchResult/ViewByCategories?pSiteGroup=MTK&keyword=';
        let linkUrl = baseUrl + jq(e.target).html();
        window.open(linkUrl);
    });

    // Array to track the ids of the details displayed rows
    let detailRows = [];
    jq('#table_id_issue tbody').off('click', 'tr td.details-control'); 
    jq('#table_id_issue tbody').on('click', 'tr td.details-control', function () {
        let tr = jq(this).closest('tr');
        let row = CRTable.row(tr);
        if (row.child.isShown()) {
            // This row is already open - close it
            row.child.hide();
            tr.removeClass('shown');
        }
        else {
            // Open this row
            row.child(format(row.data())).show();
            tr.addClass('shown');
            let AssgineeDom = jq('tr td.classAssignee').wrapInner('<a href="#"></a>');
        }
    });

    // On each draw, loop over the `detailRows` array and show any child rows
    CRTable.on('draw', function () {
        jq.each(detailRows, function (i, id) {
            jq('#' + id + ' td.details-control').trigger('click');
        });
    });
    //table.$('tr:eq(0)').addClass("selected");
}
function format(d) {
    // `d` is the original data object for the row
    return '<table border="0" style="table-layout:fixed;padding-left:50px;" width="500">' +
        '<tr>' +
        '<td width="108"><strong>State:</strong></td>' +
        '<td>' + d[7] + '</td>' +
        '<td><strong>Resolution:</strong></td>' +
        '<td>' + d[21] + '</td>' +
        '</tr>' +
        '<tr>' +
        '<td width="121"><strong>Solution:</strong></td>' +
        '<td style="word-break:break-all;white-space: pre;" width=400>' + d[23] + '</td>' +
        '</tr>' +
        '</table>';
}

export { showIssueDataTable, initColumnCheck };