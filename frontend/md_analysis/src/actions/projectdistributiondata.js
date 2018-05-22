import {
    SYS_EVENTS
} from '../actions/index';


function refreshFTAData(data) {
    let graphdata = parseData(data);
    //console.log(JSON.stringify(graphdata));
    return dispatch => {
        dispatch({
            type: SYS_EVENTS.REFRESH_FTA_DATA,
            graphdata: graphdata,

        });
    };
}

function getYearWeek(year, month, day) {
    let nowdate = new Date(year, month, day);
    let firstdayofyeardate = new Date(nowdate.getFullYear(), 0, 1);
    let day1 = nowdate.getDay();
    if (day1 == 0) day1 = 7;
    let day2 = firstdayofyeardate.getDay();
    if (day2 == 0) day2 = 7;
    let intervaladay = Math.round((nowdate.getTime() - firstdayofyeardate.getTime() + (day2 - day1) * (24 * 60 * 60 * 1000)) / 86400000);
    let weeknum = Math.ceil(intervaladay / 7) + 1;
    if (weeknum < 10) {
        weeknum = '0' + weeknum.toString();
    }
    let yy = year.toString().substr(2, 2);
    return 'W' + yy + '.' + weeknum;
}

function GetDate(AddDayCount) {
    let date = new Date();
    if (AddDayCount > 0) {
        date.setDate(date.getDate() + AddDayCount);
    } //get date after AddDayCount 
    let year = date.getFullYear();
    let month = date.getMonth(); // 
    let day = date.getDate();
    return {
        'year': year,
        'month': month,
        'day': day
    };
}

function getfiveWeeks() {
    let returnArray = [];
    //let AddDayCount = 0;
    for (let i = 0; i < 5; i++) {
        let AddDayCount = 7 * i;
        let returndate = GetDate(AddDayCount);
        returnArray.push(getYearWeek(returndate.year, returndate.month, returndate.day));
    }
    return returnArray;
}

function parseData(data) {
    let graphdata = {};
    let chip_ongoing_data = {};
    let customer_ongoing_data = {};
    let chip_incoming_data = {};
    let customer_incoming_data = {};
    let ongoing = {};
    let new_proj = {};
    let incoming = {};
    let year_data = {};
    let all_incoming_week = [];
    let all_year = [];
    let all_year_data = {};
    let fiveWeeks = [];
    let chip_new = {};
    let customer_new = {};
    let chip_ongoing = {};
    let customer_ongoing = {};

    if (data.hasOwnProperty('ongoing')) {
        ongoing = data.ongoing;
    }
    if (data.hasOwnProperty('new')) {
        new_proj = data.new;
    }
    if (data.hasOwnProperty('incoming')) {
        incoming = data.incoming;
    }
    if (data.hasOwnProperty('year')) {
        year_data = data.year;
    }

    fiveWeeks = getfiveWeeks();
    let curWeek = fiveWeeks[0];
    console.log(JSON.stringify(fiveWeeks));
    if (new_proj.hasOwnProperty(curWeek)) {
        let new_data = new_proj[curWeek];
        if (new_data.hasOwnProperty('chip')) {
            chip_new = new_data.chip;
        }
        if (new_data.hasOwnProperty('customer')) {
            customer_new = new_data.customer;
        }
    }

    for (let key_period in ongoing) {
        if (ongoing[key_period].hasOwnProperty('chip')) {
            for (let key_chip in ongoing[key_period]['chip']) {
                if (chip_ongoing.hasOwnProperty(key_chip)) {
                    chip_ongoing[key_chip] += ongoing[key_period]['chip'][key_chip];
                } else {
                    chip_ongoing[key_chip] = ongoing[key_period]['chip'][key_chip];
                }
            }
        }
        if (ongoing[key_period].hasOwnProperty('customer')) {
            for (let key_customer in ongoing[key_period]['customer']) {
                if (customer_ongoing.hasOwnProperty(key_customer)) {
                    customer_ongoing[key_customer] += ongoing[key_period]['customer'][key_customer];
                } else {
                    customer_ongoing[key_customer] = ongoing[key_period]['customer'][key_customer];
                }
            }
        }
    }
    let chip_data = getOngingGraphData(chip_ongoing, chip_new);
    let customer_data = getOngingGraphData(customer_ongoing, customer_new);
    chip_ongoing_data['period'] = curWeek;
    chip_ongoing_data['data'] = chip_data;
    customer_ongoing_data['period'] = curWeek;
    customer_ongoing_data['data'] = customer_data;
    //console.log(JSON.stringify(chip_ongoing_data));
    for (let x in fiveWeeks) {
        if (x > 0) {
            all_incoming_week.push(fiveWeeks[x]);
        }
    }
    all_incoming_week.sort();
    chip_data = getIncomingData(all_incoming_week, incoming, 'chip');
    customer_data = getIncomingData(all_incoming_week, incoming, 'customer');
    chip_incoming_data['x'] = all_incoming_week;
    chip_incoming_data['data'] = chip_data;
    customer_incoming_data['x'] = all_incoming_week;
    customer_incoming_data['data'] = customer_data;

    for (let key_year in year_data) {
        all_year.push(key_year);
    }
    all_year_data['all_year'] = all_year;
    for (let x in all_year) {
        let year_chip = [];
        let year_chip_data = [];
        let year = all_year[x];
        let chip_data = year_data[year]['chip'];
        for (let chip in chip_data) {
            year_chip.push(chip);
            year_chip_data.push(chip_data[chip]);
        }
        let customer_data = year_data[year]['customer'];
        let all_customer_info = [];
        for (let customer in customer_data) {
            let temp = {};
            temp['name'] = customer;
            temp['total'] = customer_data[customer];
            all_customer_info.push(temp);
        }
        all_customer_info.sort(sortSum);
        all_customer_info = all_customer_info.slice(0, 10);
        let year_customer = [];
        let year_customer_data = [];
        for (let x in all_customer_info) {
            let temp = all_customer_info[x];
            year_customer.push(temp['name']);
            year_customer_data.push(temp['total']);
        }
        all_year_data[year] = {};
        all_year_data[year]['all_chip'] = year_chip;
        all_year_data[year]['chip_data'] = year_chip_data;
        all_year_data[year]['all_customer'] = year_customer;
        all_year_data[year]['customer_data'] = year_customer_data;
    }

    graphdata['chip_ongoing'] = chip_ongoing_data;
    graphdata['customer_ongoing'] = customer_ongoing_data;
    graphdata['chip_incoming'] = chip_incoming_data;
    graphdata['customer_incoming'] = customer_incoming_data;
    graphdata['year'] = all_year_data;

    return graphdata;
}

function sortSum(a, b) {
    return b['total'] - a['total'];
}

function getOngingGraphData(ongoing_proj, new_proj) {
    let all_chip = {};
    let return_data = [];
    for (let chip in ongoing_proj) {
        all_chip[chip] = 1;
    }
    for (let chip in new_proj) {
        if (!(chip in all_chip)) {
            all_chip[chip] = 1;
        }
    }
    for (let chip in all_chip) {
        let ongoing_num = (chip in ongoing_proj) ? ongoing_proj[chip]: 0;
        let new_num = (chip in new_proj) ? new_proj[chip]: 0;
        let info = {};
        info['name'] = chip;
        info['data'] = [ongoing_num, new_num];
        return_data.push(info);
    }
    return return_data;
}

function getIncomingData(all_incoming_week, incoming, type) {
    let all_list = {};
    let return_data = [];
    for (let x in all_incoming_week) {
        let period = all_incoming_week[x];
        if (incoming.hasOwnProperty(period)) {
            let data = incoming[period][type];
            for (let key_type in data) {
                if (!(key_type in all_list)) {
                    all_list[key_type] = 1;
                }
            }
        }

    }
    for (let key in all_list) {
        let key_data = [];
        for (let x in all_incoming_week) {
            let period = all_incoming_week[x];
            let num = 0;
            if (incoming.hasOwnProperty(period)) {
                if (type in incoming[period]) {
                    let data = incoming[period][type];
                    num = (key in data) ? data[key]: 0;
                }
            }
            key_data.push(num);
        }
        let info = {};
        info['name'] = key;
        info['data'] = key_data;
        return_data.push(info);
    }
    return return_data;
}


function getProjectDistributionData(data) {
    let graphdata = parseData(data);
    return graphdata;
}

export {
    refreshFTAData,
    getProjectDistributionData
};