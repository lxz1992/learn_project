import {
    MD_DATA
} from '../constants';
import {
    SYS_EVENTS
} from '../actions/index';

function sortSum(a, b) {
    return b['total'] - a['total'];
}

function handlePrio(data) {
    for (let i = 0; i < data.length; i++) {
        if (data[i]['U'] === undefined) {
            data[i]['U'] = 0;
        }
        if (data[i]['H'] === undefined) {
            data[i]['H'] = 0;
        }
        if (data[i]['M'] === undefined) {
            data[i]['M'] = 0;
        }
        if (data[i]['L'] === undefined) {
            data[i]['L'] = 0;
        }
    }
    return data;
}

function refreshStatisticsGraphData(data, type, start, end) {
    let chartinfo = getStatisticsGraphData(data, type, start, end);
    return dispatch => {
        dispatch({
            type: SYS_EVENTS.REFRESH_TOP10_DATA,
            graphdata: chartinfo,

        });
    };
}

function getStatisticsGraphData(data, type, start, end) {
    let info = {};
    let mydata = data[type];
    for (let key_year in mydata) {
        if ((parseInt(key_year) >= parseInt(start)) && (parseInt(key_year) <= parseInt(end))) {
            for (let key_name in mydata[key_year]) {
                if (key_name in info) {
                    for (let key_prio in mydata[key_year][key_name]) {
                        if (info[key_name][key_prio] === undefined) {
                            info[key_name][key_prio] = mydata[key_year][key_name][key_prio];
                        } else {
                            info[key_name][key_prio] += mydata[key_year][key_name][key_prio];
                        }
                    }
                } else {
                    info[key_name] = {};
                    for (let key_prio in mydata[key_year][key_name]) {
                        info[key_name][key_prio] = mydata[key_year][key_name][key_prio];
                    }
                }
            }
        }
    }

    let chartinfo = [];
    for (let key_name in info) {
        let temp = {};
        temp.name = key_name;
        temp.total = 0;
        for (let key_prio in info[key_name]) {
            temp['total'] += info[key_name][key_prio];
            temp[key_prio] = info[key_name][key_prio];
        }
        chartinfo.push(temp);
    }
    //console.log(chartinfo);
    chartinfo.sort(sortSum);
    chartinfo = chartinfo.slice(0, 10);
    chartinfo = handlePrio(chartinfo);

    return chartinfo;

}

function handleMixPrio(data) {
    if (data['U'] === undefined) {
        data['U'] = {};
        data['U']['N'] = 0;
        data['U']['RT'] = 0;
    }
    if (data['H'] === undefined) {
        data['H'] = {};
        data['H']['N'] = 0;
        data['H']['RT'] = 0;
    }
    if (data['M'] === undefined) {
        data['M'] = {};
        data['M']['N'] = 0;
        data['M']['RT'] = 0;
    }
    if (data['L'] === undefined) {
        data['L'] = {};
        data['L']['N'] = 0;
        data['L']['RT'] = 0;
    }

    return data;
}

function sortObjByKey(obj) {
    let temp = [];
    let newObj = {};

    for (let key in obj) {
        temp.push(key);
    }
    if (temp.length === 0) {
        return undefined;
    }
    temp.sort();
    for (let x in temp) {
        newObj[temp[x]] = obj[temp[x]];
    }
    //console.log(JSON.stringify(newObj));

    for (let key_period in newObj) {
        //console.log(key_period);
        newObj[key_period] = handleMixPrio(newObj[key_period]);
        /*
        for (let key_prio in newObj[key_period]) {
            if (newObj[key_period][key_prio] === undefined) {
                newObj[key_period][key_prio] = {};
                newObj[key_period][key_prio]['N'] = 0;
                newObj[key_period][key_prio]['RT'] = 0;
            }
        }*/
    }
    return newObj;
}

function refreshResolveGraphData(redata, dept, customer, period) {
    //for(let t = Date.now();Date.now() - t <= 5000;);
    let info = {};
    let data = redata.resolved;
    let flag;
    let deptdata = {};
    let custlist = {};
    if (period === 'Month') {
        flag = 7;
    } else if (period === 'Year') {
        flag = 4;
    } else {
        flag = 8;
    }
    if (dept === 'All' && customer === 'All') {
        for (let key_dept in data) {
            deptdata[key_dept] = data[key_dept];
            for (let key_company in data[key_dept]) {
                if (key_company === '') {
                    key_company = 'blank_company';
                }
                if (!(key_company in custlist)) {
                    custlist[key_company] = {};
                }
            }
        }
    } else if (dept === 'All' && customer !== 'All') {
        for (let key_dept in data) {
            deptdata[key_dept] = data[key_dept];
            custlist[customer] = {};
        }
    } else if (dept !== 'All' && customer === 'All') {
        deptdata[dept] = data[dept];
        for (let key_company in data[dept]) {
            if (key_company === '') {
                key_company = 'blank_company';
            }
            if (!(key_company in custlist)) {
                custlist[key_company] = {};
            }
        }
    } else {
        deptdata[dept] = data[dept];
        custlist[customer] = {};
    }
    //console.log("parsing resolved data");
    //console.log(JSON.stringify(deptdata));
    //console.log(JSON.stringify(custlist));
    for (let key_dept in deptdata) {
        for (let key_company in deptdata[key_dept]) {
            let tmp_company = key_company;
            if (tmp_company === '') {
                tmp_company = 'blank_company';
            }
            //console.log(tmp_company);
            if ((tmp_company in custlist)) {
                for (let key_period in deptdata[key_dept][key_company]) {
                    if (key_period.length === flag) {
                        if (key_period in info) {
                            for (let key_prio in deptdata[key_dept][key_company][key_period]) {
                                if (key_prio in info[key_period]) {
                                    for (let key_sum in deptdata[key_dept][key_company][key_period][key_prio]) {
                                        info[key_period][key_prio][key_sum] += deptdata[key_dept][key_company][key_period][key_prio][key_sum];
                                    }
                                } else {
                                    info[key_period][key_prio] = {};
                                    for (let key_sum in deptdata[key_dept][key_company][key_period][key_prio]) {
                                        info[key_period][key_prio][key_sum] = deptdata[key_dept][key_company][key_period][key_prio][key_sum];
                                    }
                                }
                            }
                        } else {
                            info[key_period] = {};
                            for (let key_prio in deptdata[key_dept][key_company][key_period]) {
                                info[key_period][key_prio] = {};
                                for (let key_sum in deptdata[key_dept][key_company][key_period][key_prio]) {
                                    info[key_period][key_prio][key_sum] = deptdata[key_dept][key_company][key_period][key_prio][key_sum];
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    let sorted_info = sortObjByKey(info);

    return dispatch => {
        dispatch({
            type: SYS_EVENTS.REFRESH_RESOLVE_DATA,
            graphdata: sorted_info,

        });
    };
}

function refreshOpenGraphData(redata, seldept) {
    let data = redata.open;

    let cust_info = {};
    let delay_info = {};
    let sitelist = {};
    let DelayArray = ['<1W', '1W-2W', '2W-4W', '1-2Month', '>2Month'];

    if (seldept === 'All') {
        for (let key_dept in data) {
            sitelist[key_dept] = {};
        }
    } else {
        sitelist[seldept] = {};
    }
    //console.log(JSON.stringify(sitelist));
    for (let key_dept in sitelist) {
        for (let key_company in data[key_dept]) {
            if (!(key_company in cust_info)) {
                cust_info[key_company] = {};
            }
            for (let key_delay in data[key_dept][key_company]) {
                if (!(key_delay in delay_info)) {
                    delay_info[key_delay] = {};
                }

                for (let key_prio in data[key_dept][key_company][key_delay]) {
                    if (cust_info[key_company][key_prio] === undefined) {
                        cust_info[key_company][key_prio] = data[key_dept][key_company][key_delay][key_prio];
                    } else {
                        cust_info[key_company][key_prio] += data[key_dept][key_company][key_delay][key_prio];
                    }

                    if (delay_info[key_delay][key_prio] === undefined) {
                        delay_info[key_delay][key_prio] = data[key_dept][key_company][key_delay][key_prio];
                    } else {
                        delay_info[key_delay][key_prio] += data[key_dept][key_company][key_delay][key_prio];
                    }
                }
            }
        }
    }

    let customerinfo = [];
    for (let key_company in cust_info) {
        let temp = {};
        temp.name = key_company;
        temp.total = 0;
        for (let key_prio in cust_info[key_company]) {
            temp['total'] += cust_info[key_company][key_prio];
            temp[key_prio] = cust_info[key_company][key_prio];
        }
        customerinfo.push(temp);
    }
    customerinfo.sort(sortSum);
    customerinfo = customerinfo.slice(0, 10);
    customerinfo = handlePrio(customerinfo);

    let delayinfo = [];
    for (let key_delay in delay_info) {
        let temp = {};
        temp.name = key_delay;
        temp.total = 0;
        for (let key_prio in delay_info[key_delay]) {
            temp['total'] += delay_info[key_delay][key_prio];
            temp[key_prio] = delay_info[key_delay][key_prio];
        }
        delayinfo.push(temp);
    }
    delayinfo = handlePrio(delayinfo);
    delayinfo = sortinfo(delayinfo, DelayArray);

    let siteinfo = {};
    let DeptArray = [];
    for (let key_dept in data) {
        DeptArray.push(key_dept);
        if (!(key_dept in siteinfo)) {
            siteinfo[key_dept] = {};
        }
        for (let key_company in data[key_dept]) {
            for (let key_delay in data[key_dept][key_company]) {
                for (let key_prio in data[key_dept][key_company][key_delay]) {
                    if (siteinfo[key_dept][key_prio] === undefined) {
                        siteinfo[key_dept][key_prio] = data[key_dept][key_company][key_delay][key_prio];
                    } else {
                        siteinfo[key_dept][key_prio] += data[key_dept][key_company][key_delay][key_prio];
                    }
                }
            }
        }
    }
    let deptinfo = [];
    for (let key_dept in siteinfo) {
        let temp = {};
        temp.name = key_dept;
        temp.total = 0;
        for (let key_prio in siteinfo[key_dept]) {
            temp['total'] += siteinfo[key_dept][key_prio];
            temp[key_prio] = siteinfo[key_dept][key_prio];
        }
        deptinfo.push(temp);
    }
    deptinfo = handlePrio(deptinfo);
    deptinfo = sortinfo(deptinfo, DeptArray);

    let graphdata = {
        'customerinfo': customerinfo,
        'delayinfo': delayinfo,
        'deptinfo': deptinfo,
    };

    return dispatch => {
        dispatch({
            type: SYS_EVENTS.REFRESH_OPEN_DATA,
            graphdata: graphdata,

        });
    };

}

function sortinfo(info, array) {
    let newArray = [];
    let flag;
    for (let x in info) {
        flag = $.inArray(info[x]['name'], array);
        newArray[flag] = info[x];
    }
    return newArray;
}


function getwwMapGraphData(data, state, start, end) {
    let gdata = data.map.data;
    let info = {};
    let country = [];
    let statelist = [];

    if (state === 'submit') {
        statelist = MD_DATA.State;
    } else {
        statelist.push(state);
    }
    //console.log(statelist);
    for (let key_year in gdata) {
        //console.log(key_year);
        if ((parseInt(key_year) >= parseInt(start)) && (parseInt(key_year) <= parseInt(end))) {
            //console.log("matching date....");
            //for (let key_state in statelist){
            for (let i = 0; i < statelist.length; i++) {
                let key_state = statelist[i];
                //console.log(key_state);
                for (let key_country in gdata[key_year][key_state]) {
                    //console.log(key_country);
                    if (key_country !== '') {
                        if (!(key_country in info)) {
                            info[key_country] = {};
                            country.push(key_country);
                            info[key_country]['z'] = 0;
                        }
                        for (let key_operator in gdata[key_year][key_state][key_country]) {
                            if (!(key_operator in info[key_country])) {
                                info[key_country][key_operator] = {};
                                info[key_country][key_operator]['num'] = 0;
                            }

                            for (let key_class in gdata[key_year][key_state][key_country][key_operator]) {
                                if (key_class in info[key_country][key_operator]) {

                                } else {
                                    info[key_country][key_operator][key_class] = 0;
                                }
                                if (key_class !== 'Urgent'){
                                    info[key_country]['z'] += gdata[key_year][key_state][key_country][key_operator][key_class]; //Country total CR
                                    info[key_country][key_operator]['num'] += gdata[key_year][key_state][key_country][key_operator][key_class]; //operator total CR
                                }
                                info[key_country][key_operator][key_class] += gdata[key_year][key_state][key_country][key_operator][key_class]; //for display bug/feature/question
                            }
                        }
                    }
                }
            }
        }
    }
    //console.log(JSON.stringify(info));   
    let rawData = data.map.countryCode; //Array, one row: {"code": "AF", "z": 0, "name": "Afghanistan"}
    let countrycode = [];
    for (let i in rawData) {
        let row = rawData[i];
        let rowCountry = row['name'];
        if ($.inArray(rowCountry, country) >= 0) {
            row['z'] = info[rowCountry]['z']; //put
            row['operator'] = {}; //for display operator info
            for (let key_operator in info[rowCountry]) {
                if (key_operator !== 'z') {
                    row['operator'][key_operator] = {};
                    row['operator'][key_operator]['num'] = 0;
                    //temp = info[rowCountry][key_operator]['num'];
                    row['operator'][key_operator]['num'] = info[rowCountry][key_operator]['num'];
                    for (let key_class in info[rowCountry][key_operator]) {
                        row['operator'][key_operator][key_class] = info[rowCountry][key_operator][key_class];
                    }
                }
            }
            countrycode.push(row);
        }
    }
    //console.log(JSON.stringify(countrycode));

    return countrycode;
}

function refreshwwMapGraphData(data, state, start, end) {
    let countrycode = getwwMapGraphData(data, state, start, end);
    return dispatch => {
        dispatch({
            type: SYS_EVENTS.REFRESH_MAP_DATA,
            graphdata: countrycode,

        });
    };
}

function refreshwwAllData(data, type, start, end, state, mstart, mend) {
    let chartinfo = getStatisticsGraphData(data, type, start, end);
    let countrycode = getwwMapGraphData(data, state, mstart, mend);
    return dispatch => {
        dispatch({
            type: SYS_EVENTS.REFRESH_WW_DATA,
            top10data: chartinfo,
            mapdata: countrycode,

        });
    };

}

export {
    refreshStatisticsGraphData,
    refreshResolveGraphData,
    refreshOpenGraphData,
    refreshwwMapGraphData,
    refreshwwAllData
};