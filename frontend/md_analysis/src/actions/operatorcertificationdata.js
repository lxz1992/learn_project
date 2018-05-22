import { CERT_AREA_MAP } from '../constants';
import { SYS_EVENTS } from '../actions/index';


function refreshOperatorCertData(data) {
    let graphdata = {};
    let new_proj = [];
    let urgent_proj = [];
    for (let key_area in data) {
        let info = {};
        info['name'] = key_area;
        info['code'] = CERT_AREA_MAP[key_area];
        info['operator'] = {};
        let urgent_info = {};
        let total_proj = 0;
        let urgent_proj_num = 0;
        for (let key_operator in data[key_area]) {
            for (let key_type in data[key_area][key_operator]) {
                if (key_type === 'urgent') {
                    urgent_proj_num = urgent_proj_num + data[key_area][key_operator][key_type];
                    if ('operator' in urgent_info) {
                        urgent_info['operator'][key_operator] = {};
                        urgent_info['operator'][key_operator]['urgent issue'] = data[key_area][key_operator][key_type];
                    } else {
                        urgent_info['operator'] = {};
                        urgent_info['operator'][key_operator] = {};
                        urgent_info['name'] = key_area;
                        urgent_info['code'] = CERT_AREA_MAP[key_area];
                        urgent_info['operator'][key_operator]['urgent issue'] = data[key_area][key_operator][key_type];
                    }
                } else { //ongoing or incoming projects
                    total_proj = total_proj + data[key_area][key_operator][key_type];
                    if (!(key_operator in info['operator'])) {
                        info['operator'][key_operator] = {};
                    }
                    info['operator'][key_operator][key_type] = data[key_area][key_operator][key_type];
                }
            }
        }
        if (total_proj > 0){
            info['z'] = total_proj;
            if (urgent_proj_num > 0) {
                urgent_info['z'] = 0 - Math.ceil(total_proj / 2);
                urgent_proj.push(urgent_info);
            }
            new_proj.push(info);
        }

    }
    graphdata['proj'] = new_proj;
    graphdata['urgent'] = urgent_proj;
    //console.log(JSON.stringify(graphdata));
    return dispatch => {
        dispatch({
            type: SYS_EVENTS.REFRESH_CERT_DATA,
            graphdata: graphdata,

        });
    };
}

export { refreshOperatorCertData };
