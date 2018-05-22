import HtmlUtil from '../func/htmlutils';

function loadOption(year) {
    $('#YearSel').empty();
    let tempStr = '';
    let i = year.length;
    for (let x in year) {
        tempStr += HtmlUtil.genOptionString(year[i - x - 1]);
    }
    $('#YearSel').append(tempStr);
}

function loadProjectDistributionGraph(sel_year, data, owner, chip_on_container, custom_on_container, chip_in_container, custom_in_container, distr_container, custom_container) {
    let orig_data = data.chip_ongoing;
    let period = orig_data.period;
    let xCategory = ['Original Operator Lab Entry projects in ' + period, 'New add Operator Lab Entry projects in' + period];
    let container = chip_on_container;
    let title = owner + ' project chipset current status';
    let subtitle = owner + ' ongoing project';
    let ytitle = 'projects';
    let graphdata = orig_data.data;
    loadChart(container, title, xCategory, ytitle, subtitle, graphdata, 1);

    orig_data = data.customer_ongoing;
    container = custom_on_container;
    title = owner + ' project customer current status';
    graphdata = orig_data.data;
    loadChart(container, title, xCategory, ytitle, subtitle, graphdata, 1);

    orig_data = data.chip_incoming;
    xCategory = orig_data.x;
    container = chip_in_container;
    title = owner + ' project chipset current status';
    subtitle = owner + ' new coming in project next month';
    graphdata = orig_data.data;
    loadChart(container, title, xCategory, ytitle, subtitle, graphdata, 1);

    orig_data = data.customer_incoming;
    xCategory = orig_data.x;
    container = custom_in_container;
    title = owner + ' project customer current status';
    subtitle = owner + ' new coming in project next month';
    graphdata = orig_data.data;
    loadChart(container, title, xCategory, ytitle, subtitle, graphdata, 1);
    if ((sel_year !== '') && (sel_year !== undefined)) {
        loadyearChart(sel_year, data, owner, distr_container, custom_container);
    }
}


function loadyearChart(year, data, owner, distr_container, custom_container) {
    let orig_data = data['year'][year];
    let xCategory = orig_data.all_chip;
    let container = distr_container;
    let title = owner + ' projects dsitribution yearly';
    let subtitle = owner + ' ' + year + ' projects';
    let ytitle = 'projects';
    let graphdata = [{
        'data': orig_data.chip_data
    }];
    loadChart(container, title, xCategory, ytitle, subtitle, graphdata, 0);

    xCategory = orig_data.all_customer;
    container = custom_container;
    title = owner + ' projects dsitribution yearly';
    subtitle = owner + ' ' + year + ' Top10 customer';
    ytitle = 'projects';
    graphdata = [{
        'data': orig_data.customer_data
    }];
    loadChart(container, title, xCategory, ytitle, subtitle, graphdata, 0);
}

function loadChart(container, gtitle, xCategory, ytitle, gsubtitle, data, isshowlegend) {
    let chart = {
        renderTo: container,
        type: 'column'
    };
    let title = {
        text: gtitle
    };
    let subtitle = {
        text: gsubtitle
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
        },
        title: {
            text: ytitle
        }


    };
    let pointFormat = '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
        '<td style="padding:0"><b>{point.y}</b></td></tr>';
    if (!isshowlegend) {
        pointFormat = '<tr><td style="padding:0"><b>{point.y} </b></td></tr>';
    }

    let tooltip = {
        headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
        pointFormat: pointFormat,
        footerFormat: '</table>',
        //shared: true,
        useHTML: true
    };
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
    let chartOptions = {};
    chartOptions.chart = chart;
    chartOptions.title = title;
    chartOptions.subtitle = subtitle;
    chartOptions.tooltip = tooltip;
    chartOptions.xAxis = xAxis;
    chartOptions.yAxis = yAxis;
    chartOptions.series = series;
    chartOptions.plotOptions = plotOptions;
    chartOptions.credits = credits;
    if (!isshowlegend) {
        let legend = {
            enabled: false
        };
        chartOptions.legend = legend;
    }
    let gchart = new Highcharts.chart(chartOptions);
}


export { loadProjectDistributionGraph, loadOption, loadyearChart };
