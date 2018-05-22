import config from '../config';
import { MD_COLOR_MAP } from '../constants';
import cmnUtils from '../util/index';
/*
$(document).ready(function () {

    let request = GetRequest();
    if (request.length != 1) {
        alert("This request need 1 parameters: owner");
    } else {
        let owner = request[0];
        showDataTable(owner);

        let table = $('#project_table').dataTable();
        $('#project_table tbody').on('click', 'tr', function () {
            if ($(this).hasClass('selected')) {
                $(this).removeClass('selected');
            }
            else {
                table.$('tr.selected').removeClass('selected');
                $(this).addClass('selected');
            }
            //console.log('[get data]' + table.fnGetData(this)[0]);
            let project = table.fnGetData(this)[0];
            refreshChart(owner, project);
        });

    }
});


function GetRequest() {
    let url = location.search;
    let theRequest = [];
    if (url.indexOf("?") != -1) {
        let str = url.substr(1);
        strs = str.split("&");
        for (let i = 0; i < strs.length; i++) {
            theRequest[i] = unescape(strs[i].split("=")[1]);
        }
    }
    return theRequest;
}
*/
function showDataTable(owner) {
    //let URL = '../resources/json/operator_project_list.json';
    let urlOwner = cmnUtils.legalURL(owner);
    let cfg = config.API;
    let URL = cfg.OPERATOR_PROJECT_LIST + '?op_name=' + urlOwner;
    //console.log(URL);
    //let URL = 'http://localhost:8080/resources/json/issuelist_test.json';
    // Data Tables setting
    $('#project_table').DataTable().destroy();
    $('#project_table').empty();
    let CRTable = $('#project_table').DataTable({

        //define column data
        columns: [{
                'data': 0,
                'title': 'PROJECTID'
            }, //"projectID"
            {
                'data': 1,
                'title': 'CUSTOMER'
            }, //customer
            {
                'data': 2,
                'title': 'PROJECT_NAME'
            }, //project name
            {
                'data': 3,
                'title': 'PLATFORM_NAME'
            }, //"PLATFORM_NAME" 
            {
                'data': 4,
                'title': 'SWPM'
            }, //"SWPM"  
            {
                'data': 5,
                'title': 'TYPE'
            }, //"type" 
            {
                'data': 6,
                'title': 'MILESTONE_NAME'
            }, //"MILESTONE_NAME"
            {
                'data': 7,
                'title': 'START_DATA'
            }, //"START_DATA"
            {
                'data': 8,
                'title': 'END_DATA'
            }, //"END_DATA"                      
            {
                'data': 9,
                'title': 'WITH_VOLTE'
            }, //"WITH_VOLTE" 
            {
                'data': 10,
                'title': 'WITH_WFC'
            }, //"WITH_WFC"  
            {
                'data': 11,
                'title': 'WITH_VLTE'
            }, //"WITH_VLTE"
            {
                'data': 12,
                'title': 'ISCOMPLETED'
            }, //"ISCOMPLETED"

        ],
        'columnDefs': [{
                'visible': false,
                'targets': 0
            }, //projectID

        ],
        fixedColumns: true,
        //retrieve data from server
        ajax: {
            'url': URL
            //'type': "POST"
        },
        //"deferRender": true,  //speed up loading data
        order: [
            [1, 'asc']
        ],
        scrollX: true,
        bInfo: false,
        scrollY: '200px',
        scrollCollapse: true,
        paging: false,
        destroy: true,
        bFilter: false,

        initComplete: function () {
            let table = $('#project_table').dataTable();
            let nTrs = table.fnGetNodes();
            $(nTrs[0]).addClass('selected');
            let project = table.fnGetData(nTrs[0])[0];
            //console.log(project);
            refreshChart(owner, project);
        },
    });
    //table.$('tr:eq(0)').addClass("selected");
}

function refreshChart(owner, project) {
    let cfg = config.API;
    let urlOwner = cmnUtils.legalURL(owner);
    let url = cfg.PROJECT_CR + '?hw_prj_id=' + project + '&operator=' + urlOwner;
    //console.log(url);
    //let url = 'http://localhost:8080/resources/json/operator_project_cr_state.json';
    fetch(url, {credentials: 'include'})
        .then(
            function (response) {
                if (response.status !== 200) {
                    alert('there is problem when fetching，status is：' + response.status);
                    return;
                }
                response.json().then(function (data) {
                    //console.log("return data.......");
                    let data_item = data.state;
                    let graphdata = getPieGraphData(data_item);
                    let container = 'cr_state';
                    let title = 'CR State Distribution';
                    loadPieChart(container, graphdata, title);

                    // data_item = data.group;
                    // graphdata = getPieGraphData(data_item);
                    // container = 'cr_assignee';
                    // title = 'CR Assignee-group Distribution';
                    // loadPieChart(container, graphdata, title);

                    data_item = data.all_patch;
                    graphdata = getPieGraphData(data_item);
                    container = 'all_patch';
                    title = 'All Patch Distribution';
                    loadPieChart(container, graphdata, title);

                    // data_item = data.modem_patch;
                    // graphdata = getPieGraphData(data_item);
                    // container = 'modem_patch';
                    // title = 'Modem Patch Distribution';
                    // loadPieChart(container, graphdata, title);

                    data_item = data.modem_open;
                    graphdata = getColumnGraphData(data_item);
                    container = 'modem_open';
                    title = 'Modem Open CR Owning Distribution';
                    loadColumnChart(container, title, graphdata.x, graphdata.data);

                });
            }
        )
        .catch(function (err) {
            alert('Fetch error:' + err);
        });
}


function getPieGraphData(data) {
    let graphdata = [];
    for (let key in data) {
        if ((data[key] === 0) || (data[key] === '')) {
            continue;
        }
        let temp = {};
        temp.name = key;
        temp.y = data[key];
        if (MD_COLOR_MAP[key] !== undefined) {
            temp.color = MD_COLOR_MAP[key];
        }
        graphdata.push(temp);
    }
    //console.log(JSON.stringify(graphdata));
    return graphdata;
}

function getColumnGraphData(data) {
    let graphdata = {};
    let xCategory = [];
    let column_data = [];
    for (let key in data) {
        xCategory.push(key);
        column_data.push(data[key]);
    }
    let temp = [];
    temp = [{
        'name': 'CR number',
        'data': column_data
    }];
    graphdata['x'] = xCategory;
    graphdata['data'] = temp;
    return graphdata;
}

function loadPieChart(container, graphdata, gtitle) {
    let options = {
        chart: {
            renderTo: container,
            plotBackgroundColor: null,
            plotBorderWidth: null,
            plotShadow: false,
            type: 'pie'
        },
        title: {
            text: gtitle
        },
        tooltip: {
            pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
        },
        plotOptions: {

            pie: {
                //allowPointSelect: false,
                cursor: 'pointer',
                dataLabels: {
                    enabled: true,
                    formatter: function () {
                        return Highcharts.numberFormat(this.percentage, 1) +'%('+
                        Highcharts.numberFormat(this.y, 0, ',') +')';
                    },
                    style: {
                        font: '8px Trebuchet MS, Verdana, sans-serif'
                       }
                },
                showInLegend: true
            }
        },
        credits: {
            enabled: false
        },
        exporting: {
            enabled: false
        },
        series: [{
            name: 'Brands',
            colorByPoint: true,
            data: graphdata
        }],
    };
    let gchart = new Highcharts.chart(options);

}


function loadColumnChart(container, gtitle, xCategory, data) {
    let chart = {
        renderTo: container,
        type: 'column'
    };
    let title = {
        text: gtitle
    };

    let xAxis = {
        categories: xCategory,
        crosshair: true
    };
    let yAxis = {
        min: 0,
        stackLabels: {
            enabled: true,
            style: {
                fontWeight: 'bold',
                color: (Highcharts.theme && Highcharts.theme.textColor) || 'gray'
            }
        }

    };
    /*
    let tooltip = {
        headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
        pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
        '<td style="padding:0"><b>{point.y:.1f} mm</b></td></tr>',
        footerFormat: '</table>',
        shared: true,
        useHTML: true
    };*/
    let plotOptions = {
        column: {
            pointPadding: 0.2,
            borderWidth: 0
        }
    };
    let credits = {
        enabled: false
    };

    let series = data;
    //series =  [{"name":"Urgent","color":"#008800","data":[0,29,321,2,1,0,109,0,110,0]},{"name":"High","color":"#f7b101","data":[1023,1062,1259,408,1134,510,704,418,222,538]},{"name":"Medium","color":"#00a1de","data":[4497,2868,1986,2708,1924,2699,2062,1793,1404,1708]},{"name":"Low","color":"#bbbbbb","data":[141,319,213,348,323,95,276,446,746,72]}];
    let json = {};
    json.chart = chart;
    json.title = title;
    //json.subtitle = subtitle;
    //json.tooltip = tooltip;
    json.xAxis = xAxis;
    json.yAxis = yAxis;
    json.series = series;
    json.plotOptions = plotOptions;
    json.credits = credits;
    //$(container).highcharts(json);
    let gchart = new Highcharts.chart(json);
}

export {
    showDataTable,
    refreshChart
};