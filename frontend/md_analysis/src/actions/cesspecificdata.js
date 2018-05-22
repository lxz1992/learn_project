import {
    SYS_EVENTS
} from '../actions/index';


function refreshCESCountryData(data) {
    let graphdata = parseData(data);
    graphdata = graphdata.sort(sortSum);
    graphdata = graphdata.slice(0, 10);
    graphdata = handlePrio(graphdata);
    return dispatch => {
        dispatch({
            type: SYS_EVENTS.REFRESH_CES_COUNTRY_DATA,
            graphdata: graphdata,

        });
    };
}

function refreshCESGroupData(data) {
    let graphdata = parseData(data);
    graphdata = handlePrio(graphdata);
    //console.log(JSON.stringify(graphdata));
    return dispatch => {
        dispatch({
            type: SYS_EVENTS.REFRESH_CES_GROUP_DATA,
            graphdata: graphdata,

        });
    };
}

function parseData(data) {
    let graphdata = [];

    for (let key in data) {
        if ((key === 'Others') | (key === 'others')) {
            continue;
        }
        let total = 0;
        let key_info = {};
        for (let key_priority in data[key]) {
            key_info[key_priority] = data[key][key_priority];
            total = total + data[key][key_priority];
        }
        key_info['name'] = key;
        key_info['total'] = total;
        graphdata.push(key_info);
    }
    return graphdata;
}

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

export {
    refreshCESGroupData,
    refreshCESCountryData
};