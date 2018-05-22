import {
    showIssueDataTable,
    initColumnCheck
} from '../func/issue_list';
import cmnUtils from '../util/index';

const jq = jQuery.noConflict();

// load colums chart
function loadChartArea(data, sortBy, container, title, subtitle, clickevent) {
    //console.log(JSON.stringify(data));
    let seriesData = [{
            name: 'Urgent',
            color: '#008800',
            data: []
        },
        {
            name: 'High',
            color: '#f7b101',
            data: []
        },
        {
            name: 'Medium',
            color: '#00a1de',
            data: []
        },
        {
            name: 'Low',
            color: '#bbbbbb',
            data: []
        }
    ];
    let xAxis = [];
    for (let i in data) {
        xAxis.push(data[i][sortBy]);
        seriesData[0].data.push(data[i]['U']);
        seriesData[1].data.push(data[i]['H']);
        seriesData[2].data.push(data[i]['M']);
        seriesData[3].data.push(data[i]['L']);
    }
    //console.log(JSON.stringify(seriesData));
    addHcColumn(container, title, subtitle, xAxis, seriesData, clickevent);
}

function optionsHcColumn(container, clickevent) {
    let options = {
        chart: {
            renderTo: container,
            type: 'column'
        },
        xAxis: {
            categories: []
        },
        yAxis: {
            min: 0,
            stackLabels: {
                enabled: true,
                style: {
                    fontWeight: 'bold',
                    color: (Highcharts.theme && Highcharts.theme.textColor) || 'gray'
                }
            }
        },
        legend: {
            align: 'right',
            x: 0,
            verticalAlign: 'top',
            y: 30,
            floating: true,
            backgroundColor: (Highcharts.theme && Highcharts.theme.background2) || 'white',
            borderColor: '#CCC',
            borderWidth: 1,
            shadow: false
        },
        plotOptions: {
            column: {
                stacking: 'normal',
                dataLabels: {
                    enabled: true,
                    formatter: function () {
                        if (this.y === '0') return '';
                        else return this.y;
                    },
                    color: (Highcharts.theme && Highcharts.theme.dataLabelsColor) || 'white',

                }
            },
            series: {
                events: {
                    click: function (e) {
                        if (clickevent) {
                            let name = this.name;
                            let xcategory = e.point.category;
                            jq(function () {
                                jq('#issue_info').modal({
                                    keyboard: true
                                });
                            });

                            jq('#issue_info').one('shown.bs.modal', function (e) {
                                let title = xcategory + ' open eService List';
                                initColumnCheck();
                                let list_filter = '';
                                xcategory = cmnUtils.legalURL(xcategory);
                                if (clickevent === 'CES_Country') {
                                    list_filter = 'cr_type=ces_country_cr&country=' + xcategory;

                                } else if (clickevent === 'CES_Group') {
                                    list_filter = 'cr_type=ces_group_cr&group=' + xcategory;
                                }
                                jq('#issuelist_title').html(title);
                                showIssueDataTable(list_filter);
                            });
                        }
                    }
                }
            }

        },
        credits: {
            enabled: false
        },
        exporting: {
            enabled: false
        },
        series: []
    };

    options.title = {};
    options.subtitle = {};
    options.xAxis.categories = [];
    options.series = new Array();

    return options;
}

function addHcColumn(container, title, subtitle, categories, series, clickevent) {
    let options = optionsHcColumn(container, clickevent);
    options.title.text = title;
    options.subtitle.text = subtitle;
    options.xAxis.categories = categories;
    options.series = series;
    //let chart = new Highcharts.Chart(options);
    let chart = new Highcharts.chart(options);
}

//load mix chart(column and  line)
function optionsMix(container) {
    let options = {
        chart: {
            renderTo: container,
            type: 'column'
        },
        xAxis: {
            categories: []
        },
        yAxis: [{
                min: 0,
                stackLabels: {
                    enabled: true,
                    style: {
                        fontWeight: 'bold',
                        color: (Highcharts.theme && Highcharts.theme.textColor) || 'gray'
                    }
                }
            },
            { // Secondary yAxis
                gridLineWidth: 0,
                title: {
                    text: 'Average Resolved Time',
                    style: {
                        color: Highcharts.getOptions().colors[1]
                    },
                },
                labels: {
                    format: '{value} Day',
                    style: {
                        color: Highcharts.getOptions().colors[1]
                    }
                },
                opposite: true,
            }
        ],
        legend: {
            align: 'right',
            x: -30,
            verticalAlign: 'top',
            y: 20,
            floating: true,
            backgroundColor: (Highcharts.theme && Highcharts.theme.background2) || 'white',
            borderColor: '#CCC',
            borderWidth: 1,
            shadow: false
        },
        plotOptions: {
            column: {
                stacking: 'normal',
                dataLabels: {
                    enabled: true,
                    color: (Highcharts.theme && Highcharts.theme.dataLabelsColor) || 'white',

                }
            },
        },
        credits: {
            enabled: false
        },
        exporting: {
            enabled: false
        },
        series: []
    };

    options.title = {};
    options.subtitle = {};
    options.xAxis.categories = [];
    options.series = new Array();

    return options;
}

function addHcMix(container, title, subtitle, categories, series) {
    let options = optionsMix(container);
    options.title.text = title;
    options.subtitle.text = subtitle;
    options.xAxis.categories = categories;
    options.series = series;
    let chart = new Highcharts.chart(options);
}

/*-----------------Dual Chart: Column+Line-----------------*/
function loadChartMIX(data, container, title, subtitle) {
    let seriesData = [{
            type: 'column',
            name: 'Urgent',
            color: '#008800',
            data: []
        },
        {
            type: 'column',
            name: 'High',
            color: '#f7b101',
            data: []
        },
        {
            type: 'column',
            name: 'Medium',
            color: '#00a1de',
            data: []
        },
        {
            type: 'column',
            name: 'Low',
            color: '#bbbbbb',
            data: []
        }
    ];
    let seriesLine = [{
            type: 'spline',
            name: 'Average Resolved Time of Urgent&High',
            color: '#ff0000',
            yAxis: 1,
            data: []
        },
        {
            type: 'spline',
            name: 'Average Resolved Time of Medium&Low',
            color: '#000000',
            yAxis: 1,
            data: []
        }
    ];

    let xAxis = [];
    for (let key_period in data) {
        let time = [0, 0];
        let sum = [0, 0];
        xAxis.push(key_period);
        for (let key_prio in data[key_period]) {
            if (key_prio === 'U') {
                seriesData[0].data.push(data[key_period][key_prio]['N']);
            } else if (key_prio === 'H') {
                seriesData[1].data.push(data[key_period][key_prio]['N']);
            } else if (key_prio === 'M') {
                seriesData[2].data.push(data[key_period][key_prio]['N']);
            } else {
                seriesData[3].data.push(data[key_period][key_prio]['N']);
            }
            if (key_prio === 'U' || key_prio === 'H') {
                time[0] += data[key_period][key_prio]['RT'];
                sum[0] += data[key_period][key_prio]['N'];

            } else {
                time[1] += data[key_period][key_prio]['RT'];
                sum[1] += data[key_period][key_prio]['N'];
            }
        }
        if (sum[0] === 0) {
            seriesLine[0].data.push(0);
        } else {
            seriesLine[0].data.push(Math.round(time[0] / sum[0]));
        }
        if (sum[1] === 0) {
            seriesLine[1].data.push(0);
        } else {
            seriesLine[1].data.push(Math.round(time[1] / sum[1]));
        }
    }

    seriesData.push(seriesLine[0]);
    seriesData.push(seriesLine[1]);
    addHcMix(container, title, subtitle, xAxis, seriesData);
}


function getUrgentGraphData(oridata) {
    //[{"code":"CN","z":2,"name":"China","operator":{"China Mobile":{"num":2,"Non-bug":2,"Urgent":1}}},{"code":"IN","z":1,"name":"India","operator":{"Jio":{"num":1,"Non-bug":1}}}]
    let result = [];
    for (let i in oridata) {
        let total_urgent_num = 0;
        let row = oridata[i];
        let contry_operator = row.operator;
        for (let key_operator in contry_operator) {
            let operator_info = contry_operator[key_operator];
            if ((operator_info.hasOwnProperty('Urgent')) && (operator_info.Urgent > 0)) {
                total_urgent_num = total_urgent_num + operator_info.Urgent;
            }
        }
        if (total_urgent_num > 0) {
            let country_info = {};
            country_info.code = row.code;
            country_info.z = 0 - Math.ceil(row.z / 2);
            country_info.name = row.name;
            result.push(country_info);
        }
    }
    return result;
}

//load word map
function loadMapArea(data, state, container) {
    //console.log(JSON.stringify(data));
    let totaldata = data;
    let urgentdata = [];
    if ((state === 'open') || (state === 'Open')) {
        urgentdata = getUrgentGraphData(data);
    }
    Highcharts.mapChart(container, {
        chart: {
            borderWidth: 0,
            map: 'custom/world'
        },

        title: {
            text: 'World Wide Modem Support Eservice'
        },

        subtitle: {
            text: 'eservice reported from total <b>' + data.length + '</b> Countries<br><em>(World wide total 214 Countries)</em>'
        },

        legend: {
            enabled: false
        },

        mapNavigation: {
            enabled: true,
            buttonOptions: {
                verticalAlign: 'bottom'
            }
        },
        plotOptions: {
            series: {
                events: {
                    click: function (e) {
                        let state = $('#State').children('option:selected').val();
                        let from_year = $('#myearStart').children('option:selected').val();
                        let to_year = $('#myearEnd').children('option:selected').val();
                        let country_code = e.point.code;
                        let country = countryName(country_code, data);
                        let sum = e.point.z;
                        
                        if (((state === 'open') || (state === 'Open')) && (sum < 0)) {
                            //if (!e.point.selected) {
                                $('#urgent_select_result').show();
                            //} else {
                            //    $('#urgent_select_result').hide();
                            //}
                            let info = urgentissueinfo(country, data);
                            jq('#urgent_select_result').html(info);
                            jq('#urgent_select_result a').click(function () {
                                loadUrgentIssue(jq(this).attr('data-value'), state, from_year, to_year, country);
                            });
    
                            
                        } else {
                            $('#urgent_select_result').hide();
                            //console.log(country);
                            jq(function () {
                                jq('#issue_info').modal({
                                    keyboard: true
                                });
                            });
    
                            jq('#issue_info').one('shown.bs.modal', function (e) {
                                initColumnCheck();
                                country = cmnUtils.legalURL(country);
                                let list_filter = 'cr_type=map_cr&state='+ state + '&from_year=' + from_year + '&to_year=' + to_year + '&country=' + country;
                                jq('#issuelist_title').html(country + ' ' + jq('#State').children('option:selected').val() + ' issue list');
                                showIssueDataTable(list_filter);
                            });
                        }
                    }
                }
            }
        },
        series: [{
                name: 'Countries',
                color: '#E0E0E0',
                enableMouseTracking: false
            },
            {
                type: 'mapbubble',
                name: 'Eservice',
                zThreshold: 0,
                sizeByAbsoluteValue: true,
                joinBy: ['iso-a2', 'code'],
                data: data,
                mapData: Highcharts.maps['custom/world'],
                minSize: 4,
                maxSize: '10%',
                tooltip: {
                    pointFormatter: function () {
                        let country = this['iso-a2'];
                        return tooltip(country, data, state);
                    }
                }
            }, {
                type: 'mapbubble',
                name: 'urgent issue',
                negativeColor: '#FF0022',
                color: '#FF0022',
                zThreshold: 0,
                sizeByAbsoluteValue: true,
                joinBy: [
                    'iso-a2', 'code'
                ],
                data: urgentdata,
                mapData: Highcharts.maps['custom/world'],
                minSize: 2,
                maxSize: '6%',
                tooltip: {
                    pointFormatter: function () {
                        let country = this['iso-a2'];
                        return tooltip(country, data, state);
                    }
                }
            }
        ],
        credits: {
            enabled: false
        },
        exporting: {
            enabled: false
        }
    });
}

function loadUrgentIssue(operator, state, from_year, to_year, country) {
    jq(function () {
        jq('#issue_info').modal({
            keyboard: true
        });
    });

    jq('#issue_info').one('shown.bs.modal', function (e) {
        jq('#issuelist_title').html(operator + ' urgent issue list');
        //let list_filter = 'cr_type=urgent_cr&operator=' + operator;
        initColumnCheck();
        country = cmnUtils.legalURL(country);
        operator = cmnUtils.legalURL(operator);
        let list_filter = 'cr_type=map_cr&state='+ state + '&from_year=' + from_year + '&to_year=' + to_year + '&country=' + country + '&operator=' + operator;
        showIssueDataTable(list_filter);
    });

}

function urgentissueinfo(country, data) {
    let content = '';
    for (let i in data) {
        let row = data[i];
        if (row['name'] === country) {
            content = '<b>' + row['name'] + ' operator with urgent issues:</b><br/>';
            for (let key_operator in row['operator']) {
                for (let key_class in row['operator'][key_operator]) {
                    if ((key_class === 'Urgent') && (row['operator'][key_operator][key_class] > 0)) {
                        //content += key_operator + ':' + '<font color="red"><strong>' + row['operator'][key_operator][key_class] + '</strong></font>;<br/>';
                        content += '<a href="javascript:void(0);" data-value="' + key_operator + '"; >' + key_operator + ' : <font color="red"><strong>' + row['operator'][key_operator][key_class] + '</strong></font></a>';
                        content += ' ;<br/>';
                    }
                    
                }
            }
        }
    }
    return content;
}

function countryName(country_code, data) {
    let country = '';
    for (let i in data) {
        let row = data[i];
        if (row['code'] === country_code) {
            country = row['name'];
        }
    }
    return country;
}

function tooltip(country, CoutryCodes, state) {
    let content = '';
    for (let i in CoutryCodes) {
        let row = CoutryCodes[i];
        if (row['code'] === country) {
            content = '<b>Country: ' + row['name'] + '</b><br/>';
            for (let key_operator in row['operator']) {
                let CRClass = {
                    'num': '',
                    'new bug': '',
                    'known issue': '',
                    'new feature': '',
                    'change feature': '',
                    'non-bug': '',
                    'Urgent': '',
                    'others': ''
                };
                //content += key_operator +' : ' + row['operator'][key_operator]['num']+' (';
                let classContent = [];
                for (let key_class in row['operator'][key_operator]) {
                    switch (key_class) {
                        case 'num':
                            CRClass['num'] = key_operator + ' : ' + row['operator'][key_operator]['num'] + ' (';
                            break;
                        case 'Non-bug':
                            CRClass['non-bug'] = ' Non-bug:' + '<strong>' + row['operator'][key_operator][key_class] + '</strong>';
                            break;
                        case 'Known bug':
                            CRClass['known issue'] = ' Known bug:' + '<strong>' + row['operator'][key_operator][key_class] + '</strong>,';
                            break;
                        case 'New feature':
                            CRClass['new feature'] = ' New feature:' + '<strong>' + row['operator'][key_operator][key_class] + '</strong>,';
                            break;
                        case 'Change feature':
                            CRClass['change feature'] = ' Change feature:' + '<strong>' + row['operator'][key_operator][key_class] + '</strong>,';
                            break;
                        case 'New bug':
                            CRClass['new bug'] = ' New bug:' + '<strong>' + row['operator'][key_operator][key_class] + '</strong>,';
                            break;
                        case 'Urgent':
                            if ((row['operator'][key_operator][key_class] > 0) && ((state === 'open') || (state === 'Open'))){
                                CRClass['Urgent'] = key_operator + ' : ' + '<font color="red"><strong>' + row['operator'][key_operator][key_class] + '</strong></font>/' + row['operator'][key_operator]['num'] + ';<br/>';
                            }
                            
                            break;
                        default:
                            CRClass['others'] = ' Others:' + '<strong>' + row['operator'][key_operator][key_class] + '</strong>';
                    }
                }
                if ((state === 'open') || (state === 'Open')) {
                    if (CRClass['Urgent'] !== '') {
                        content += CRClass['Urgent'];
                    } else {
                        content += key_operator + ' : ' + '<font color="red"><strong>0</strong></font>/' + row['operator'][key_operator]['num'] + ';<br/>';
                    }
                    
                }else {
                    for (let key_CRClass in CRClass) {
                        content += CRClass[key_CRClass];
                    }
                    content += classContent + ' )<br/>';
                }
                
            }
        }
    }
    return content;
}


export {
    loadChartArea,
    loadChartMIX,
    loadMapArea
};