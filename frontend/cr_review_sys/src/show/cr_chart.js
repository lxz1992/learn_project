import Highcharts from 'highcharts';
import {
    simplifyDisplayWeekList
} from '../data/cr_datetime';
import {
    GV
} from '../constants';

const jq = jQuery.noConflict();

function plotLineChart(myContainer, gTitle, xAxisList, countList, dataNameList, plotOptionHash) {
    let countBarList = {};
    let seriesDataList = [];
    let setDataLabelText = true;
    let chartType = null;
    let optionFieldList = ['type', 'color'];
    let weeklyOrDaily = 'weekly';
    let xlabelText = '';
    let legendLayout = 'horizontal';
    let legendPosition = 'right';

    if (plotOptionHash['weekly-or-daily'] !== undefined) {
        weeklyOrDaily = plotOptionHash['weekly-or-daily'];
    }

    if (weeklyOrDaily === 'weekly') {
        xlabelText = 'Week';
    } else if (weeklyOrDaily === 'daily') {
        xlabelText = 'Date';
    }

    if (plotOptionHash['xlabel'] !== undefined) {
        xlabelText = plotOptionHash['xlabel'];
    }

    if (plotOptionHash['chartType'] !== undefined) {
        chartType = plotOptionHash['chartType'];
    }
    //console.log(countList[0].length);
    if (countList.length === 0) {
        jq('#' + myContainer).html(gTitle);
        return;
    }

    if (countList[0].length === 1) {
        setDataLabelText = false;
    }

    for (let i = 0; i < dataNameList.length; i++) {
        countBarList[i] = [];
    }

    for (let i = 0; i < xAxisList.length; i++) {
        for (let j = 0; j < countList[0].length; j++) {
            countBarList[j].push({
                'y': countList[i][j]
            });
        }
    }
    for (let i = 0; i < countList[0].length; i++) {
        let myDataItem = {
            name: dataNameList[i],
            data: countBarList[i]
        };

        for (let j = 0; j < optionFieldList.length; j++) {
            let myField = optionFieldList[j];
            if (plotOptionHash[myField] !== undefined) {
                if (plotOptionHash[myField][i] !== undefined) {
                    myDataItem[myField] = plotOptionHash[myField][i];
                }
            }
        }

        seriesDataList.push(myDataItem);
    }
    //console.log(seriesDataList);
    let myStackOption = null;
    if (plotOptionHash['stacking'] !== undefined) {
        myStackOption = plotOptionHash['stacking'];
    }

    let lineLabels = true;
    if (plotOptionHash['lineLabels'] !== undefined) {
        lineLabels = plotOptionHash['lineLabels'];
    }

    let splineLabels = true;
    if (plotOptionHash['splineLabels'] !== undefined) {
        splineLabels = plotOptionHash['splineLabels'];
    }

    //console.log(JSON.stringify(seriesDataList));
    let chart = new Highcharts.chart({
        chart: {
            renderTo: myContainer,
            type: chartType,
            zoomType: 'x',
            resetZoomButton: {
                position: {
                    align: 'left',
                    verticalAlign: 'top',
                    x: 10,
                    y: 10
                },
                relativeTo: 'chart'
            }
        },
        title: {
            text: gTitle
        },
        xAxis: {
            categories: xAxisList,
            title: {
                text: xlabelText
            }
        },
        yAxis: {
            min: 0,
            title: {
                text: 'Count'
            },
            stackLabels: {
                enabled: true,
                style: {
                    color: (Highcharts.theme && Highcharts.theme.textColor) || 'gray'
                }
            }
        },
        legend: {
            layout: legendLayout,
            align: legendPosition,
            verticalAlign: 'top',
            x: 0,
            y: 30,
            floating: true,
            backgroundColor: (Highcharts.theme && Highcharts.theme.legendBackgroundColorSolid) || 'white',
            borderColor: '#CCC',
            borderWidth: 1,
            shadow: false
        },
        tooltip: {
            formatter: function () {
                let displayText = '';
                if (weeklyOrDaily === 'weekly') {
                    displayText += '<b>Week ' + this.x + '</b><br/>' + this.series.name + ': ' + this.y;
                } else if (weeklyOrDaily === 'daily') {
                    displayText += '<b>' + this.x + '</b><br/>' + this.series.name + ': ' + this.y;
                }
                if (this.point.stackTotal !== undefined) {
                    displayText += '<br/>' + 'Total: ' + this.point.stackTotal;
                }
                if ((myStackOption !== null) && (this.point.stackTotal > 0)) {
                    displayText += '<br/>' + parseInt(100 * this.y / this.point.stackTotal) + '%';
                }

                return displayText;
            }
        },
        plotOptions: {
            column: {
                stacking: myStackOption,
                dataLabels: {
                    enabled: true,
                    style: {
                        color: (Highcharts.theme && Highcharts.theme.textColor) || '#005DAC'
                    }
                }
            },
            line: {
                stacking: myStackOption,
                dataLabels: {
                    enabled: lineLabels,
                    style: {
                        color: (Highcharts.theme && Highcharts.theme.textColor) || 'gray'
                    }
                }
            },
            spline: {
                stacking: myStackOption,
                dataLabels: {
                    enabled: splineLabels,
                    style: {
                        color: (Highcharts.theme && Highcharts.theme.textColor) || 'gray'
                    }
                }
            }
        },
        series: seriesDataList
    });

    jq('.Highcharts-legend').click(function () {
        if (jq(this).attr('opacity') === 1) {
            jq(this).attr('opacity', 0.5);
        } else if (jq(this).attr('opacity') === 0.5) {
            jq(this).attr('opacity', 0);
        } else {
            jq(this).attr('opacity', 1);
        }
    });
}


function loadCrDailyCountChart(chartTitle, plotDivId, dayList, dayCountHash, analysisFieldList, countLabelList, plotOption) {
    let countList = [];
    for (let i = 0; i < dayList.length; i++) {
        let tmpCountList = [];
        for (let j in analysisFieldList) {
            let analysisField = analysisFieldList[j];
            let thisCount = dayCountHash[dayList[i]][analysisField];
            tmpCountList.push(thisCount);
        }
        countList.push(tmpCountList);
    }

    plotLineChart(plotDivId, chartTitle, dayList, countList, countLabelList, plotOption);

}


function loadCrWeeklyCountChart(chartTitle, plotDivId, weekList, weekCountHash, analysisFieldList, countLabelList, plotOption) {
    let countList = [];
    let simplifiedDisplayWeekList = simplifyDisplayWeekList(weekList);
    for (let i in weekList) {
        let week = weekList[i];
        let tmpCountList = [];
        for (let j in analysisFieldList) {
            let analysisField = analysisFieldList[j];
            tmpCountList.push(weekCountHash[week][analysisField]);
        }
        countList.push(tmpCountList);
    }
    plotLineChart(plotDivId, chartTitle, simplifiedDisplayWeekList, countList, countLabelList, plotOption);
}

function loadCountByTeamChart(chartTitle, plotDivId, teamList, teamCrTotalList, plotOption, teamCrInfo) {
    //console.log(JSON.stringify(plotOption));
    let labellist = ['Total CR', 'Open CR'];
    plotLineChart(plotDivId, chartTitle, teamList, teamCrTotalList, labellist, plotOption);

    jq('.crCountByTeamBtn').click(function () {
        let newTeamCrTotalList = [];
        labellist = ['Total CR', 'Open CR'];
        for (let i = 0; i < teamList.length; i++) {
            let team = teamList[i];
            let teamTotalCrCount = teamCrInfo[team]['Total CR'];
            let teamOpenCrCount = teamCrInfo[team]['Open CR'];
            switch (jq(this).val()) {
                case 'Total':
                    newTeamCrTotalList.push([team, [teamTotalCrCount]]);
                    break;
                case 'Open':
                    newTeamCrTotalList.push([team, [teamOpenCrCount]]);
                    break;
                default:
                    newTeamCrTotalList.push([team, [teamTotalCrCount, teamOpenCrCount]]);
                    break;
            }
        }

        let plotOption = {
            'xlabel': 'Teams',
            'type': {
                0: 'column',
                1: 'column'
            },
            'color': {
                0: GV.color['gray'],
                1: GV.color['red']
            }
        };

        if (jq(this).val() === 'Open') {
            newTeamCrTotalList.sort(function (a, b) {
                return b[1][0] - a[1][0];
            });
            labellist = ['Open CR'];
            plotOption['color'] = {
                0: GV.color['red']
            };
        }

        let newTeamList = [];
        let newCrList = [];
        for (let i = 0; i < newTeamCrTotalList.length; i++) {
            if (newTeamCrTotalList[i][1][0] > 0) {
                newTeamList.push(newTeamCrTotalList[i][0]);
                newCrList.push(newTeamCrTotalList[i][1]);
            }
        }

        plotLineChart(plotDivId, chartTitle, newTeamList, newCrList, labellist, plotOption);
    });
}

export {
    loadCrDailyCountChart,
    loadCrWeeklyCountChart,
    loadCountByTeamChart
};