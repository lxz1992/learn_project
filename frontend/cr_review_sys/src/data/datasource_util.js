import 'jquery';

function handleResponse(response) {
    if (response.status === 200 || response.status === 0) {
        return Promise.resolve(response.json());
    } else {
        return Promise.reject(new Error(`Status: ${response.status}\nMessage: ${response.statusText}`));
    }
}

function rotateResolutionData(data) {
    //const colNames = ["completed", "rejected", "duplicated", "not_reproducible", "not_to_fix", "sum"];
    let colNames = Object.keys(data);
    const rowNames = {
        count: "Count",
        percent: "%"
    };

    let result = {};
    let tabledata = [];
    let tablecolums = [];
    let columdef = {
        sTitle: "Resolution",
        mData: "type"
    };
    tablecolums.push(columdef);
    colNames.forEach(colName => {
        columdef = {
            sTitle: colName,
            mData: colName
        };
        tablecolums.push(columdef);
    });
    Object.keys(rowNames).forEach(rowName => {
        let rowData = {};
        rowData["type"] = rowNames[rowName];
        colNames.forEach(colName => {
            rowData[colName] = data[colName][rowName];
        });
        tabledata.push(rowData);
    });
    result.data = tabledata;
    result.columns = tablecolums;
    return result;
    
}

function rotateCRCountData(data, rowsName, Title) {
    let colNames = Object.keys(data);
    let columns = [];
    let resultdata = [];
    let columndef = {
        'data': 'type',
        'title': Title
    };
    columns.push(columndef);

    colNames.forEach(colName => {
        let title = colName;
        let re = /W\d{4}/;
        if (re.test(colName)){
            let prestr = colName.substring(0,3);
            let laststr = colName.substring(3,colName.length);
            title = prestr + '.' + laststr;
        }
        columndef = {
            'data': colName,
            'title': title
        };
        columns.push(columndef);
    });

    Object.keys(rowsName).forEach(rowName => {
        let rowData = {};
        rowData["type"] = rowsName[rowName];
        colNames.forEach(colName => {
            rowData[colName] = data[colName][rowName];
        });
        //console.log(JSON.stringify(rowData));
        resultdata.push(rowData);
    });
    let result = {
        'columns': columns,
        'data': resultdata
    };
    return result;
}

function getHomeCrCountByDate(dayList, dayCountHash, rowInfo) {
    let DataHash = {};
    let displayHash = {};
    let percentHash = {};
    for (let i = 0; i < rowInfo['name'].length; i++) {
        let thisRowName = rowInfo['name'][i];
        let thisCrField = rowInfo['field'][thisRowName];
        let thisCrFieldOperation = '';
        let thisCrFieldMore = '';

        if (thisCrField !== undefined) {
            if ((thisCrField.indexOf('-') > 0) &&
                (rowInfo['field'][thisRowName].split('-')[0].indexOf('Date') > 0) &&
                (rowInfo['field'][thisRowName].split('-')[1].indexOf('Date') > 0)) {
                thisCrField = rowInfo['field'][thisRowName].split('-')[0];
                thisCrFieldMore = rowInfo['field'][thisRowName].split('-')[1];
                thisCrFieldOperation = '-';
            }
        }

        let thisCountType = rowInfo['type'][thisRowName];
        let thisCount = 0;

        let col = 0;
        for (let j = 0; j < dayList.length; j++) {
            let thatDate = dayList[j];
            let thisMon = parseInt(thatDate.split('-')[1], 10);
            let thisDay = parseInt(thatDate.split('-')[2], 10);
            let datastr = thisMon + '/' + thisDay;
            if (DataHash[datastr] === undefined) {
                DataHash[datastr] = {};
            }
            if (thisCountType === 'daily') {
                thisCount = 0;
            }
            if (dayCountHash[thatDate][thisCrField] !== undefined) {
                thisCount += dayCountHash[thatDate][thisCrField];
            }
            if (thisCrFieldOperation === '-') {
                if (dayCountHash[thatDate][thisCrFieldMore] !== undefined) {
                    thisCount -= dayCountHash[thatDate][thisCrFieldMore];
                }
            }
            if (thisCountType === 'accumulated') {
                if (percentHash[thatDate] === undefined) {
                    percentHash[thatDate] = {};
                }
                percentHash[thatDate][thisRowName] = thisCount;
            }
            /*
            if (thatDate < GV.activityStartDate) {
                continue;
            }
            */
            if (thisRowName === 'percent') {
                let thisNumerator = thisCrField.split('/')[0];
                let thisDenominator = thisCrField.split('/')[1];
                if (displayHash[thisDenominator][col] === 0) {
                    thisCount = '0%';
                } else {
                    thisCount = Math.floor(100 * displayHash[thisNumerator][col] / displayHash[thisDenominator][col]) + '%';
                }
                col += 1;
            }

            if (displayHash[thisRowName] === undefined) {
                displayHash[thisRowName] = [];
            }
            displayHash[thisRowName].push(thisCount);
            DataHash[datastr][thisRowName] = thisCount;
        }

    }
    let result = {};
    result.Date = DataHash;
    //console.log(JSON.stringify(result));
    return result;
}

function getHomeCrCountByWeek(weekList, weekCountHash, rowInfo) {
    let weekData = {};
    let displayHash = {};
    let percentHash = {};
       
    for (let i = 0; i < rowInfo['name'].length; i++) {
        let thisRowName = rowInfo['name'][i];
        let thisCrField = rowInfo['field'][thisRowName];
        let thisCrFieldOperation = '';
        let thisCrFieldMore = '';
        
        if (thisCrField !== undefined) {
            if ((thisCrField.indexOf('-') > 0)&&
                (rowInfo['field'][thisRowName].split('-')[0].indexOf('Date') > 0)&&
                (rowInfo['field'][thisRowName].split('-')[1].indexOf('Date') > 0)) {
                thisCrField = rowInfo['field'][thisRowName].split('-')[0];
                thisCrFieldMore = rowInfo['field'][thisRowName].split('-')[1];
                thisCrFieldOperation = '-';
            }
        }
        
        let thisCountType = rowInfo['type'][thisRowName];
        
        let thisCount = 0;
        let col = 0;
        for (let j = 0; j < weekList.length; j++) {
            //let skipField = false;
            let thatWeek = weekList[j];
            let weekstr = thatWeek;
            weekstr=weekstr.replace(".","");
            if (weekData[weekstr] === undefined) {
                weekData[weekstr] = {};
            }
            if (thisCountType === 'daily') {
                thisCount = 0;
            }
            if (weekCountHash[thatWeek][thisCrField] !== undefined) {
                thisCount += weekCountHash[thatWeek][thisCrField];
            }
            if (thisCrFieldOperation === '-') {
                if (weekCountHash[thatWeek][thisCrFieldMore] !== undefined) {
                    thisCount -= weekCountHash[thatWeek][thisCrFieldMore];
                }
            }
            if (thisCountType === 'accumulated') {
                if (percentHash[thatWeek] === undefined) {
                    percentHash[thatWeek] = {};
                }
                percentHash[thatWeek][thisRowName] = thisCount;
            }
            
            if (thisRowName === 'percent') {
                let thisNumerator = thisCrField.split('/')[0];
                let thisDenominator = thisCrField.split('/')[1];
                if (displayHash[thisDenominator][col] === 0) {
                    thisCount = '0%';
                } else {
                    thisCount = Math.floor(100*displayHash[thisNumerator][col]/displayHash[thisDenominator][col]) + '%';
                }
                col += 1;
            }
            
            if (displayHash[thisRowName] === undefined) {displayHash[thisRowName] = [];}
            
            displayHash[thisRowName].push(thisCount);
            weekData[weekstr][thisRowName] = thisCount;
        }
    }
    let result = {};
    result.Week = weekData;
    return result;
}

export {
    handleResponse,
    rotateResolutionData,
    rotateCRCountData,
    getHomeCrCountByDate,
    getHomeCrCountByWeek
};