/*jslint node: true */
"use strict";

import {
    getProjectDistributionData
} from '../actions/projectdistributiondata';
import {
    loadProjectDistributionGraph,
    loadOption,
    loadyearChart
} from '../func/projectdistribution';
import {
    showDataTable,
    refreshChart
} from '../func/operator_project_list';
import {
    showIssueDataTable,
    initColumnCheck
} from '../func/issue_list';
import config from '../config';
import cmnUtils from '../util/index';
import util from 'util';

const jq = jQuery.noConflict();
// load  chart
function loadOperatorCertArea(proj_data, urgent_data) {
    let container = 'cert_map';
    let title = 'Operator Certification status ';
    Highcharts.mapChart(container, {
        chart: {
            borderWidth: 1,
            map: 'custom/world'
        },

        title: {
            text: title
        },

        mapNavigation: {
            enabled: true,
            buttonOptions: {
                verticalAlign: 'bottom'
            }
        },

        colorAxis: {
            min: 0
        },
        plotOptions: {
            mapbubble: {
                allowPointSelect: true,
                marker: {
                    states: {
                        select: {
                            //fillColor: "#5fdef9", lineColor: '#135c78',

                        }
                    }
                },
                events: {
                    click: function (e) {
                        if (!e.point.selected) {
                            $('#select_result').show();
                        } else {
                            $('#select_result').hide();
                        }
                        let country = e.point.code;
                        let sum = e.point.z;
                        //$("#select_result").toggle()
                        let info = '';
                        if (sum > 0) {
                            info = projecttooltip(country, proj_data);
                        } else {
                            info = urgenttooltip(country, urgent_data);
                        }
                        //alert(country); alert(sum);
                        jq('#select_result').html(info);
                        jq('#select_result a').click(function () {
                            if (jq(this).attr('func') === 'proj_info') {
                                loadProjectDistribution(jq(this).attr('data-value'));
                            } else if (jq(this).attr('func') === 'project_list') {
                                loadProjectList(jq(this).attr('data-value'));
                            } else if (jq(this).attr('func') === 'urgent_proj') {
                                loadUrgentIssue(jq(this).attr('data-value'));
                            }
                            //alert($(this).attr("data-value") + '   ' + $(this).attr("func"));
                        });

                    }
                }
            }
        },
        series: [{
            name: 'operator projects',
            color: '#E0E0E0',
            enableMouseTracking: false
        }, {
            type: 'mapbubble',
            allowPointSelect: true,
            name: 'operator projects',
            zThreshold: 0,
            sizeByAbsoluteValue: true,
            joinBy: [
                'iso-a2', 'code'
            ],
            data: proj_data,
            mapData: Highcharts.maps['custom/world'],
            minSize: 5,
            maxSize: '12%',
            tooltip: {
                followPointer: true,
                pointFormatter: function () {
                    let country = this['iso-a2'];
                    return projecttooltip(country, proj_data);
                }
            }
        }, {
            type: 'mapbubble',
            name: 'urgent issue projects',
            negativeColor: '#FF0022',
            color: '#FF0022',
            zThreshold: 0,
            sizeByAbsoluteValue: true,
            joinBy: [
                'iso-a2', 'code'
            ],
            data: urgent_data,
            mapData: Highcharts.maps['custom/world'],
            minSize: 5,
            maxSize: '6%',
            tooltip: {
                followPointer: true,
                backgroundColor: '#FF0022',
                style: {
                    fontColor: '#FF0022'
                },
                pointFormatter: function () {
                    let country = this['iso-a2'];
                    return urgenttooltip(country, urgent_data);
                }
            }
        }],
        credits: {
            enabled: false
        },
        exporting: {
            enabled: false
        }
    });
}

function projecttooltip(country, CoutryCodes) {
    // let content = '<b>Country: '+ country +'</b><br/>';
    let content = '';
    for (let i in CoutryCodes) {
        let row = CoutryCodes[i];
        if (i >= 0) {
            if (row['code'] === country) {
                content = '<font size="2" color="blue"><b> ' + row['name'] + ' Operator Projects</b></font><br/>';
                for (let key_operator in row['operator']) {
                    for (let key_class in row['operator'][key_operator]) {
                        switch (key_class) {
                            case 'ongoing':
                                // content += '<a href="javascript:void(0);"data-value="' + key_operator + '"; "
                                // onclick="project_info(this);">' + key_operator + ' : ' + '<strong>' +
                                // row['operator'][key_operator]['ongoing'] + '</strong>/';
                                content += '<a href="javascript:void(0);" data-value="' + key_operator + '"; func="proj_info";>' + key_operator + ' : <strong>' + row['operator'][key_operator]['ongoing'] + '</strong>/';
                                break;
                            case 'incoming':
                                content += '<strong>' + row['operator'][key_operator][key_class] + '</strong></a>';
                                break;

                            default:
                                break;
                        }
                    }
                    content += ' ; <a href="javascript:void(0);" data-value="' + key_operator + '";  func="project_list";>project list</a><br/>';

                }
            }
        }
    }
    //console.log(content);
    return content;
}

function urgenttooltip(country, CoutryCodes) {
    // let content = '<b>Country: '+ country +'</b><br/>';
    let content = '';
    for (let i in CoutryCodes) {
        if (i >= 0) {
            let row = CoutryCodes[i];
            if (row['code'] === country) {
                content = '<font size="2" color="red"><b> ' + row['name'] + ' Operator Projects with urgent issue</b></font><br/>';
                for (let key_operator in row['operator']) {
                    for (let key_class in row['operator'][key_operator]) {
                        switch (key_class) {
                            case 'urgent issue':
                                if ((row['operator'][key_operator]['urgent issue'] > 0) & (row['operator'][key_operator]['urgent issue'] !== '')){
                                    content += '<a href="javascript:void(0);" data-value="' + key_operator + '"; func="urgent_proj";>' + key_operator + ' : <strong>' + row['operator'][key_operator]['urgent issue'] + '</strong></a>';
                                    content += ' ;<br/>';
                                }
                                break;
                            default:
                                break;
                        }
                    }
                    //content += ' ;<br/>';
                    //alert(content);
                }
            }
        }
    }
    return content;
}

function loadProjectList(operator) {
    jq(function () {
        jq('#projlistmodal').modal({
            keyboard: true
        });
    });

    jq('#projlistmodal').one('shown.bs.modal', function (e) {
        jq('#projectlist_title').html(operator + ' customer project status');
        showDataTable(operator);

        let table = jq('#project_table').dataTable();
        jq('#project_table tbody').on('click', 'tr', function () {
            if (jq(this).hasClass('selected')) {
                jq(this).removeClass('selected');
            } else {
                table
                    .$('tr.selected')
                    .removeClass('selected');
                jq(this).addClass('selected');
            }
            //console.log('[get data]' + table.fnGetData(this)[0]);
            let project = table.fnGetData(this)[0];
            refreshChart(operator, project);
        });

    });
}

function loadUrgentIssue(operator) {
    jq(function () {
        jq('#issue_info').modal({
            keyboard: true
        });
    });

    jq('#issue_info').one('shown.bs.modal', function (e) {
        jq('#issuelist_title').html(operator + ' urgent issue list');
        initColumnCheck();
        operator = cmnUtils.legalURL(operator);
        let list_filter = 'cr_type=urgent_cr&operator=' + operator;
        showIssueDataTable(list_filter);
    });

}

function loadProjectDistribution(operator) {
    let ulroperator = cmnUtils.legalURL(operator);
    let url = `${config.API.OPERATOR_PROJECT}${(cmnUtils.isProd())? `&op_name=${ulroperator}`: ""}`;
    fetch(url, {credentials: 'include'}).then(function (response) {
            if (response.status !== 200) {
                alert('there is problem when fetching，status is：' + response.status);
                return;
            }
            response
                .json()
                .then(function (data) {
                    if (data.hasOwnProperty('data')) {
                        let chip_on_container = 'chip_ongoing';
                        let custom_on_container = 'customer_ongoing';
                        let chip_in_container = 'chip_comingin';
                        let custom_in_container = 'customer_comingin';
                        let distr_container = 'project_distribution';
                        let custom_container = 'cusstomer_top10';
                        //console.log(JSON.stringify(data.data));
                        let graphdata = getProjectDistributionData(data.data);
                        //console.log(JSON.stringify(graphdata));
                        jq(function () {
                            jq('#projdistrmodal').modal({
                                keyboard: true
                            });
                        });
                        jq('#projdistrmodal').one('shown.bs.modal', function (e) {
                            let sel_year = '';
                            let year = graphdata.year.all_year;
                            if (year.length > 0) {
                                loadOption(year);
                                sel_year = jq('#YearSel')
                                .children('option:selected')
                                .val();
                            }
                            loadProjectDistributionGraph(sel_year, graphdata, operator, chip_on_container, custom_on_container, chip_in_container, custom_in_container, distr_container, custom_container);
                        });

                        jq('#projdistrmodal').one('hide.bs.modal', function (e) {
                            jq('#chip_ongoing').html('');
                            jq('#customer_ongoing').html('');
                            jq('#chip_comingin').html('');
                            jq('#customer_comingin').html('');
                            jq('#project_distribution').html('');
                            jq('#cusstomer_top10').html('');
                            jq('#YearSel').empty();
                        });
                        jq('#YearSel').off('change');
                        jq('#YearSel').change(function () {
                            let year = jq('#YearSel')
                                .children('option:selected')
                                .val();
                            console.log('----' + JSON.stringify(graphdata));
                            loadyearChart(year, graphdata, operator, distr_container, custom_container);
                        });
                        return;
                    } else {
                        alert("There are no data from DB!");
                    }
                });
        })
        .catch(function (err) {
            alert('Fetch error:' + err);

            return;
        });
}

export {
    loadOperatorCertArea
};