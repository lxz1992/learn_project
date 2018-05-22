import '../../node_modules/bootstrap/dist/css/bootstrap.min.css';
//import '../node_modules/highcharts/css/highcharts.css';
import '../resources/css/md_analysis.css';
import '../../node_modules/datatables.net-dt/css/jquery.dataTables.css';
import 'jquery';
import 'bootstrap';
import Highcharts from 'highcharts';
require('highcharts/modules/map')(Highcharts);
require('highcharts/modules/data')(Highcharts);
require('../lib/mapdata/world');
import { onViewChanged } from './actions/index';
import store from './store';
import { fetchModemData, viewOptionsChanged } from './actions/mddata';
import { refreshResolveGraphData, refreshStatisticsGraphData, refreshOpenGraphData, refreshwwMapGraphData, refreshwwAllData } from './actions/graphdata';
import { refreshOperatorCertData } from './actions/operatorcertificationdata';
import { refreshFTAData } from './actions/projectdistributiondata';
import { refreshCESGroupData, refreshCESCountryData } from './actions/cesspecificdata';
import { MD_VIEW, MD_UPDATE_STATUS, REDUCER_NAME } from './constants';
import { loadChartArea, loadChartMIX, loadMapArea } from './func/graph';
import { loadOperatorCertArea } from './func/operatorcertgraph';
import { loadProjectDistributionGraph, loadyearChart } from './func/projectdistribution';
import HtmlUtil from './func/htmlutils';
import { updateSource } from './actions/update_source_action';
import update_src_view from './views/update_src_view';
import cmnUtils from './util/index';
import isEqual from 'is-equal';
import watch from 'redux-watch';

const jq = jQuery.noConflict();
let prevMsg = "";

let flag_need_update_option = true;
let flag_first_option_init = false;

function checkUpdateStatus(){
    const defaultInterval = 60 * 1000;
    let interval = null;
    interval = window.setInterval(()=>{
        let curState = store.getState();
        if (curState.syncStatus.isSyncing){
            // console.log("polling for udpate");
            store.dispatch(updateSource(true));
        } else {
            console.log("remove polling for update");
            window.clearInterval(interval);
        }
    }, defaultInterval);
}

jq('#viewRadioBtn a').on('click', (e) => {
    let self = e.currentTarget;
    let sel = jq(self).data('title');
    flag_first_option_init = false;
    flag_need_update_option = true;
    
    store.dispatch(fetchModemData(sel));
    store.dispatch(onViewChanged(sel));
});

jq('#btnUpdate').click(function () {
    let state = store.getState();
    store.dispatch(updateSource(false));
    checkUpdateStatus();
});

jq('#yearStart, #yearEnd').change(function () {
    let start = jq('#yearStart').children('option:selected').val();
    let end = jq('#yearEnd').children('option:selected').val();
    if (parseInt(start) > parseInt(end)) {
        jq("#yearEnd").val(start);
        alert('Invalid select, try again!');
    }
});

jq('#myearStart, #myearEnd').change(function () {
    let start = jq('#myearStart').children('option:selected').val();
    let end = jq('#myearEnd').children('option:selected').val();
    if (parseInt(start) > parseInt(end)) {
        jq("#myearEnd").val(start);
        alert('Invalid select, try again!');
    }
});


jq(document).ready((e) => {
    let sela = 'MD Analysis';
    var selector = '.nav li';
    $(selector).removeClass('active');
    var alist = document.getElementsByTagName("li");
    for (var i = 0; i < alist.length; i++){
        var list = alist[i];
        if(list.innerHTML.indexOf(sela) > 0 ){
            $(list).addClass('active');
        }
    }
    
    store.dispatch(updateSource(true, true));
    checkUpdateStatus();
});

function updateViewPage(newVal, oldVal, objectPath) {
    let sel = newVal;
    let viewId = 'curView';

    jq(`#${viewId}`).prop('value', sel);
    jq(`a[data-toggle="${viewId}"]`).not(`[data-title="${sel}"]`).removeClass('active').addClass('notActive');
    jq(`a[data-toggle="${viewId}"][data-title="${sel}"]`).removeClass('notActive').addClass('active');

}

function updateOptionItem(domname, option, key, sort) {
    if (option.hasOwnProperty(key)) {
        jq("#" + domname).empty();
        let option_item = option[key];
        let len = option_item.length;

        let tempStr = '';
        for (let x in option_item) {
            if (sort === 0) {
                tempStr += HtmlUtil.genOptionString(option_item[x]);
            } else {
                tempStr += HtmlUtil.genOptionString(option_item[len - x - 1]);
            }
        }
        jq("#" + domname).append(tempStr);
    }

}

function updatemapoptionbystate(state) {
    if (state === 'open') {
        jq('#myearStart').hide();
        jq('#myearEnd').hide();
        jq('#labelmyearfrom').hide();
        jq('#labelmyearto').hide();
        jq('#urgent_select_result').show();
        //document.getElementById("container_map").style.width = "1000px";
        document.getElementById("container_map").setAttribute("class","col-sm-10 col-md-10");
    }else {
        jq('#myearStart').show();
        jq('#myearEnd').show();
        jq('#labelmyearfrom').show();
        jq('#labelmyearto').show();
        jq('#urgent_select_result').hide();
        //document.getElementById("container_map").style.width = "1300px";
        document.getElementById("container_map").setAttribute("class","col-sm-12 col-md-12");
    }
}

function updateStatisticsOption(option, data) {

    if (!flag_need_update_option) {
        jq("#ww_all").show();
        jq("#Type").empty();

        let tempStr = "";
        for (let x in option.option_type) {
            tempStr += HtmlUtil.genOptionString(option.option_type[x]);
        }
        jq("#Type").append(tempStr);

        let type = jq('#Type')
            .children('option:selected')
            .val();
        let sel_option = option.option_year;
        updateOptionItem("yearStart", sel_option, type, 0);
        updateOptionItem('yearEnd', option.option_year, type, 1);
        flag_first_option_init = true;

        jq('#Type').change(function () {
            let type = $(this).children('option:selected').val();
            updateOptionItem('yearStart', option.option_year, type, 0);
            updateOptionItem('yearEnd', option.option_year, type, 1);
        });

        jq("#yearStart, #yearEnd, #Type").change(function () {
            let start = jq('#yearStart').children('option:selected').val();
            let end = jq('#yearEnd').children('option:selected').val();
            let type = jq('#Type').children('option:selected').val();
            store.dispatch(refreshStatisticsGraphData(data, type, start, end));
        });

        //update map option    
        jq("#State").empty();

        tempStr = "";
        for (let x in option.option_map_state) {
            tempStr += HtmlUtil.genOptionString(option.option_map_state[x]);
        }
        jq("#State").append(tempStr);

        let i = option.option_map_year.length;
        jq("#myearStart").empty();
        jq("#myearEnd").empty();
        let tempStr2 = "";
        tempStr = "";
        for (let x in option.option_map_year) {
            tempStr += HtmlUtil.genOptionString(option.option_map_year[x]);
            tempStr2 += HtmlUtil.genOptionString(option.option_map_year[i - x - 1]);
        }
        jq("#myearStart").append(tempStr);
        jq("#myearEnd").append(tempStr2);

        jq("#myearStart, #myearEnd, #State").change(function () {
            let start = jq('#myearStart')
                .children('option:selected')
                .val();
            let end = jq('#myearEnd')
                .children('option:selected')
                .val();
            let state = jq('#State')
                .children('option:selected')
                .val();
            updatemapoptionbystate(state);
            
            store.dispatch(refreshwwMapGraphData(data, state, start, end));
        });

        type = jq('#Type')
            .children('option:selected')
            .val();
        let start = jq('#yearStart')
            .children('option:selected')
            .val();
        let end = jq('#yearEnd')
            .children('option:selected')
            .val();
        let mstart = jq('#myearStart')
            .children('option:selected')
            .val();
        let mend = jq('#myearEnd')
            .children('option:selected')
            .val();
        let state = jq('#State')
            .children('option:selected')
            .val();
        updatemapoptionbystate(state);
        store.dispatch(refreshwwAllData(data, type, start, end, state, mstart, mend));
    }
}


function updateResolvedOption(option, data) {
    jq("#resolved_all").show();
    jq("#deptSel").empty();
    jq("#State").append("<option value=All>All</option>");
    let tempStr = "";

    for (let x in option.option_resolved_sites) {
        tempStr += HtmlUtil.genOptionString(option.option_resolved_sites[x]);
    }
    jq("#deptSel").append(tempStr);

    jq("#periodSel").empty();
    tempStr = "";
    for (let x in option.option_sel) {
        tempStr += HtmlUtil.genOptionString(option.option_sel[x]);
    }
    jq("#periodSel").append(tempStr);
    flag_first_option_init = true;

    let dept = jq('#deptSel').children('option:selected').val();
    let sel_option = option.option_resolved_customer;
    updateOptionItem("custSel", sel_option, dept, 0);

    jq('#deptSel').change(function () {
        let dept = $(this).children('option:selected').val();
        updateOptionItem("custSel", sel_option, dept, 0);
    });
    jq("#deptSel, #custSel, #periodSel").change(function () {
        let dept = jq('#deptSel').children('option:selected').val();
        let cust = jq('#custSel').children('option:selected').val();
        let period = jq('#periodSel').children('option:selected').val();
        store.dispatch(refreshResolveGraphData(data, dept, cust, period));
    });

    dept = jq('#deptSel').children('option:selected').val();
    let cust = jq('#custSel').children('option:selected').val();
    let period = jq('#periodSel').children('option:selected').val();
    store.dispatch(refreshResolveGraphData(data, dept, cust, period));
}

function updateFirstOption(selected, data, option) {
    let sel = selected;
    if (!data["isFetching"]) {
        if (flag_need_update_option === true) {
            //if ((JSON.stringify(data.Customer) != "{}") & (JSON.stringify(data.map) != "{}")) {
                flag_need_update_option = false;
                store.dispatch(viewOptionsChanged(data));
            //}
        }
        // for users who just switched the tabs but didn't click the update
        jq('#lastestUpdate').html(data.updateTime);
        if (!flag_first_option_init) {
            removeBody();
            switch (sel) {
                case MD_VIEW.STATISTICS:
                    if ((JSON.stringify(data.Customer) !== "{}") & (JSON.stringify(data.map) !== "{}")) {
                        updateStatisticsOption(option, data);
                    }else{
                        flag_need_update_option = true;
                    }
                    break;

                case MD_VIEW.RESOLVED_ESERVICES:
                    updateResolvedOption(option, data);

                    break;
                case MD_VIEW.OPEN_ESERVICES:
                    jq("#open_all").show();
                    jq("#deptOpenSel").empty();
                    jq("#deptOpenSel").append("<option value=All>All</option>");
                    let tempStr = "";
                    for (let x in option.option_open_sites) {
                        tempStr += HtmlUtil.genOptionString(option.option_open_sites[x]);
                    }
                    jq("#deptOpenSel").append(tempStr);
                    flag_first_option_init = true;
                    store.dispatch(refreshOpenGraphData(data, "All"));
                    jq("#deptOpenSel").change(function () {
                        let dept = jq('#deptOpenSel').children('option:selected').val();
                        store.dispatch(refreshOpenGraphData(data, dept));
                    });
                    break;
                case MD_VIEW.OPERATOR_CERTIFICATION:
                    jq("#operator_cert").show();
                    //console.log("refresh operator data.....");
                    //console.log(JSON.stringify(data.operator_certification));
                    flag_first_option_init = true;
                    store.dispatch(refreshOperatorCertData(data.operator_certification));
                    break;
                case MD_VIEW.FTA:
                    jq("#fta").show();
                    //console.log("refresh operator data.....");
                    //console.log(JSON.stringify(data.operator_certification));
                    flag_first_option_init = true;
                    store.dispatch(refreshFTAData(data.fta));
                    break;
                case MD_VIEW.CES_SPECIFIC:
                    jq("#ces").show();
                    if ((JSON.stringify(data.ces_country) != "{}") | (JSON.stringify(data.ces_group) != "{}")) {
                        if (JSON.stringify(data.ces_country) != "{}") {
                            flag_first_option_init = true;
                            store.dispatch(refreshCESCountryData(data.ces_country));
                            flag_first_option_init = false;
                        }
                        if (JSON.stringify(data.ces_group) != "{}") {
                            flag_first_option_init = true;
                            store.dispatch(refreshCESGroupData(data.ces_group));
                        }
                        
                    }

                    break;
                default:
                    break;
            }

        }
    }

    prevMsg = data['message']
}


function updateGraph(selected, data, graphdata) {
    let sel = selected;

    //console.log("updating graph");
    //console.log(JSON.stringify(state.graphdata));
    if (!data["isFetching"]) {
        switch (sel) {
            case MD_VIEW.STATISTICS:
                let ww_top10_graphdata = graphdata.top10data;
                let ww_map_graphdata = graphdata.ww_map;
                let type = jq('#Type').children('option:selected').val();
                let start = jq('#yearStart').children('option:selected').val();
                let end = jq('#yearEnd').children('option:selected').val();
                let state = jq('#State')
                .children('option:selected')
                .val();
                loadChartArea(ww_top10_graphdata, 'name', 'container_customer', 'Submit Eservices Top 10 ' + type, start + '-' + end);
                //console.log(JSON.stringify(ww_map_graphdata));
                loadMapArea(ww_map_graphdata, state, 'container_map');

                break;

            case MD_VIEW.RESOLVED_ESERVICES:
                let eresolved_graphdata = graphdata.resolvedata;
                let period = $('#periodSel').children('option:selected').val();
                let title;
                if (period == 'Month') {
                    title = 'Resolved Issues Recent 1 Year';
                } else if (period == 'Year') {
                    title = 'Resolved Issues Recent Years';
                } else {
                    title = 'Resolved Issues Recent 12 Weeks';
                }
                loadChartMIX(eresolved_graphdata, 'container_resolved', title, '');
                break;
            case MD_VIEW.OPEN_ESERVICES:
                let customerinfo = graphdata.opendata.customerinfo;
                let delayinfo = graphdata.opendata.delayinfo;
                let deptinfo = graphdata.opendata.deptinfo;

                let subtitle = "";
                if ($('#deptSel').children('option:selected').val() != 'All') {
                    subtitle = $('#deptSel').children('option:selected').val();
                }
                loadChartArea(customerinfo, 'name', 'open_customer', 'Open Eservices Top 10 Customers', subtitle);
                loadChartArea(delayinfo, 'name', 'open_depay', 'Open Eservices Delay Status', subtitle);
                loadChartArea(deptinfo, 'name', 'open_site', 'Open Eservices By Site', '');
                break;
            case MD_VIEW.OPERATOR_CERTIFICATION:
                let certinfo = graphdata.operator_cert_data.proj;
                let urgentinfo = graphdata.operator_cert_data.urgent;
                loadOperatorCertArea(certinfo, urgentinfo);
                break;
            case MD_VIEW.FTA:
                let ftadata = graphdata.ftadata;
                //console.log(JSON.stringify(ftadata));
                let all_year = ftadata.year.all_year;
                $("#YearFTASel").empty();
                let tempStr = ""
                let i = all_year.length;
                for (let x in all_year) {
                    tempStr += HtmlUtil.genOptionString(all_year[i - x - 1]);
                }

                $("#YearFTASel").append(tempStr);

                let chip_on_container = "fta_chip_ongoing";
                let custom_on_container = "fta_customer_ongoing";
                let chip_in_container = "fta_chip_comingin";
                let custom_in_container = "fta_customer_comingin";
                let distr_container = "fta_project_distribution";
                let custom_container = "fta_cusstomer_top10";
                let year = $('#YearFTASel').children('option:selected').val();
                let operator = "FTA";
                loadProjectDistributionGraph(year, ftadata, operator, chip_on_container, custom_on_container, chip_in_container, custom_in_container, distr_container, custom_container);

                $("#YearFTASel").change(function () {
                    year = $('#YearFTASel').children('option:selected').val();
                    loadyearChart(year, ftadata, operator, distr_container, custom_container);
                });
                //let _adrobj = JSON.stringify(ftadata).replace(/\"/g,"'");  
                //let url = './templates/operator_project_distribution.html?owner=fta&data=' + JSON.stringify(_adrobj);
                //document.getElementById("fta").innerHTML = '<object type="text/html" data='+url+' width="100%" height="800px"></object>';
                break;
            case MD_VIEW.CES_SPECIFIC:
                let ces_country_data = graphdata.ces_country_data;
                let ces_group_data = graphdata.ces_group_data;
                let click_event = "CES_Country";
                loadChartArea(ces_country_data, 'name', 'mea_top10', 'MEA Top 10 country open eService', '', click_event);
                click_event = "CES_Group";
                loadChartArea(ces_group_data, 'name', 'eu_operator', 'EU Group open eService', '', click_event);
            default:
                return;
        }
    }
}



function removeBody() {
    jq("#ww_all").hide();
    jq("#resolved_all").hide();
    jq("#open_all").hide();

    jq("#operator_cert").hide();
    jq("#fta").hide();
    jq("#loading").hide();
    jq("#ces").hide();
    jq("#qa").hide();
    jq("#rf_ant_trend").hide();
    jq("#rf_ant_issue").hide();
    jq("#known_issue").hide();
    jq("#eServer_breakdown").hide();
}

let subscribeReducer = (reducerPath, evenhandler, ...params) => {
    let w = watch(store.getState, reducerPath, isEqual);
    store.subscribe(w((newVal, oldVal, objectPath) => {
        evenhandler(newVal, oldVal, objectPath, ...params);
    }));
};

subscribeReducer(REDUCER_NAME.currentView, updateViewPage);
subscribeReducer(REDUCER_NAME.syncStatus, update_src_view, jq);

let globalstate;
store.subscribe(() => {
    globalstate = store.getState();
    if (globalstate.data["isFetching"]) {
        jq('#spinner-modal').modal('show');
    }else{
        jq('#spinner-modal').modal('hide');
    }
    if (globalstate.data["code"] && prevMsg != globalstate.data["message"]) {
        removeBody();
        jq("#fail-info").show();
        jq("#fail-info").html(globalstate.data["message"]);
    } else {
        jq("#fail-info").hide();
        updateFirstOption(globalstate.currentView, globalstate.data, globalstate.option);
        updateGraph(globalstate.currentView, globalstate.data, globalstate.graphdata);
    }
});
