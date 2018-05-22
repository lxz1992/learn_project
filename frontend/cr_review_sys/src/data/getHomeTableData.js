import {
    GV
} from '../constants';

function getHomeTableData(crlist, state) {
    let result = {};
    let curactivity = state.currentActivity;
    if (curactivity === 'default-activity') {
        curactivity = state.activities["default"];
    }

    let crSummaryTypeList = ['All CR', 'Bug CR'];
    if (curactivity.indexOf('_Bug') >= 0) {
        crSummaryTypeList = ['Bug CR'];
    } else if (curactivity.indexOf('_NonBug') >= 0) {
        crSummaryTypeList = ['All CR'];
    }
    let countCategoryList = {
        'All CR': {
            'total': 0,
            'open': 0,
            'completed': 0
        },
        'Bug CR': {
            'total': 0,
            'open': 0,
            'completed': 0
        }
    };

    let crClassStateCount = {};
    let resolutionHash = {};
    for (let i = 0; i < GV.resolutionList.length; i++) {
        let resolution = GV.resolutionList[i];
        resolutionHash[resolution] = 0;
    }
    let totalCount = 0;

    for (let i in crlist) {
        let cr = crlist[i];
        countCategoryList['All CR']['total'] += 1;
        if (cr.Class === 'Bug') {
            countCategoryList['Bug CR']['total'] += 1;
        }
        if (cr.Resolution.toLowerCase() === 'completed') {
            countCategoryList['All CR']['completed'] += 1;
        }
        if (isCropenByState(cr.State)) {
            countCategoryList['All CR']['open'] += 1;
            if (cr.Class === 'Bug') {
                countCategoryList['Bug CR']['open'] += 1;
            }
        } else {
            if ((cr.Class === 'Bug') &&
                (cr.Resolution.toLowerCase() === 'completed')) {
                countCategoryList['Bug CR']['completed'] += 1;
            }
        }

        if (GV.classHash[cr.Class] !== '') {
            cr.Class = 'Others';
        }
        if (crClassStateCount[cr.Class] === undefined) {
            crClassStateCount[cr.Class] = {};
        }
        if (crClassStateCount[cr.Class][cr.State] === undefined) {
            crClassStateCount[cr.Class][cr.State] = 0;
        }
        if (crClassStateCount[cr.Class]['Sum'] === undefined) {
            crClassStateCount[cr.Class]['Sum'] = 0;
        }
        crClassStateCount[cr.Class][cr.State] += 1;
        crClassStateCount[cr.Class]['Sum'] += 1;

        let resolution = cr.Resolution;
        if (resolution !== '') {
            if (resolutionHash[resolution] !== undefined) {
                resolutionHash[resolution] += 1;
                totalCount += 1;
            } else {
                resolutionHash[resolution] = 1;
                totalCount += 1;
            }
        }
    }

    let returnSummaryData = getSummaryData(countCategoryList, crSummaryTypeList);
    let returnClassStateData = getClassStateData(crClassStateCount);
    //console.log(JSON.stringify(resolutionHash));
    let returnResolutionData = getResolutionData(resolutionHash, totalCount);

    result.summaryCountData = returnSummaryData;
    result.ClassStateCountData = returnClassStateData;
    result.ResolutionCountData = returnResolutionData;
    //console.log(JSON.stringify(result));
    return result;
}

function isCropenByState(crstate) {
    for (let i in GV.openStateList) {
        let openState = GV.openStateList[i];
        if (crstate === openState) {
            return true;
        }
    }
    return false;
}

function getSummaryData(countCategoryList, crSummaryTypeList) {
    let summarydata = [];
    for (let j in crSummaryTypeList) {
        let countField = crSummaryTypeList[j];
        let countFieldData = countCategoryList[countField];
        countFieldData.type = countField;
        summarydata.push(countFieldData);
    }
    let returnSummaryData = {};
    returnSummaryData.summary = summarydata;
    return returnSummaryData;
}

function lowerJSONKey(jsonObj) {
    for (var key in jsonObj) {
        jsonObj[key.toLowerCase()] = jsonObj[key];
        delete(jsonObj[key]);
    }
    return jsonObj;
}

function getNullClassStateData(statelist) {
    let result = {};
    for (let i in statelist) {
        let crstate = statelist[i];
        result[crstate] = 0;
    }
    return result;
}

function getClassStateData(crClassStateCount) {
    let myCrFieldList = {
        'Class': [],
        'State': []
    };
    myCrFieldList['Class'] = [].concat(GV.crFieldList['Class'], ['Sum']);
    myCrFieldList['State'] = [].concat(GV.crFieldList['State'], ['Sum']);
    let classstatedata = [];
    let statesum = getNullClassStateData(myCrFieldList['State']);
    for (let i in myCrFieldList['Class']) {
        let crclass = myCrFieldList['Class'][i];
        if ((crClassStateCount[crclass] === undefined) && (crclass !== 'Sum')) {
            let countFieldData = getNullClassStateData(myCrFieldList['State']);
            countFieldData = lowerJSONKey(countFieldData);
            countFieldData.class = crclass;
            classstatedata.push(countFieldData);
        } else {
            if (crclass !== 'Sum') {
                let countFieldData = crClassStateCount[crclass];
                for (let j in myCrFieldList['State']) {
                    let crstate = myCrFieldList['State'][j];
                    if (countFieldData[crstate] === undefined) {
                        countFieldData[crstate] = 0;
                    }
                    statesum[crstate] += countFieldData[crstate];
                }
                countFieldData = lowerJSONKey(countFieldData);
                countFieldData.class = crclass;
                classstatedata.push(countFieldData);
            }
        }
    }
    statesum = lowerJSONKey(statesum);
    statesum.class = 'Sum';
    classstatedata.push(statesum);
    //console.log(JSON.stringify(classstatedata));
    let returnClassStateData = {};
    returnClassStateData.count = classstatedata;
    return returnClassStateData;
}

function getResolutionData(resolutionHash, totalCount) {
    let resolutionCount = {};
    for (let solution in resolutionHash) {
        console.log(JSON.stringify(solution));
        let count = resolutionHash[solution];
        console.log(JSON.stringify(count));
        let myval = parseInt(1000 * (count / totalCount), 10) / 10;
        if (isNaN(myval) === true) {
            myval = '-';
        } else {
            myval += '%';
        }
        resolutionCount[solution] = {};
        resolutionCount[solution]['count'] = resolutionHash[solution];
        resolutionCount[solution]['percent'] = myval;
    }
    resolutionCount['Sum'] = {};
    resolutionCount['Sum']['count'] = totalCount;
    resolutionCount['Sum']['percent'] = '100%';
    let result = {};
    result.Resolution = resolutionCount;
    return result;
}

export {
    getHomeTableData
};