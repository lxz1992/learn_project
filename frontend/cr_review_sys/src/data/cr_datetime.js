function getNowTimeText() {
    let todayDate = new Date();
    //let todayDateText = String(todayDate.getFullYear()) + String(todayDate.getMonth() + 1) + String(todayDate.getDate());
    let todayDateText = sprintf('%04d-%02d-%02d %02d:%02d:%02d', todayDate.getFullYear(), todayDate.getMonth() + 1, todayDate.getDate(), todayDate.getHours(), todayDate.getMinutes(), todayDate.getSeconds());
    return todayDateText;
}

function getSecondBetween(from_time, to_time) {
    from_time = from_time.replace(/\-/g, "/");
    to_time = to_time.replace(/\-/g, "/");
    let date1 = new Date(from_time);
    var date2 = new Date(to_time);
    let result = parseInt(date2 - date1) / 1000;
    return result;
}

function crGetTodayText() {
    let todayDate = new Date();
    let todayDateText = String(todayDate.getFullYear()) + String(todayDate.getMonth() + 1) + String(todayDate.getDate());
    todayDateText = sprintf('%04d-%02d-%02d', todayDate.getFullYear(), todayDate.getMonth() + 1, todayDate.getDate());
    return todayDateText;
}

function crDaysBetween(date1, date2) {
    let sYear = parseInt(date1.substring(0, 4), 10);
    let sMon = parseInt(date1.substring(5, 7), 10);
    let sDay = parseInt(date1.substring(8, 10), 10);
    let sDate1 = new Date(sYear, sMon - 1, sDay);
    sYear = parseInt(date2.substring(0, 4), 10);
    sMon = parseInt(date2.substring(5, 7), 10);
    sDay = parseInt(date2.substring(8, 10), 10);
    let sDate2 = new Date(sYear, sMon - 1, sDay);
    let betweenDays = daysBetween(sDate1, sDate2);
    return betweenDays;
}

function crDaysDiffToday(crDate) {
    let todayDate = new Date();
    let sYear = parseInt(crDate.substring(0, 4), 10);
    let sMon = parseInt(crDate.substring(5, 7), 10);
    let sDay = parseInt(crDate.substring(8, 10), 10);
    let sDate = new Date(sYear, sMon - 1, sDay);
    let betweenDays = daysBetween(sDate, todayDate);
    return betweenDays;
}

function crGetYearFromDate(crDate) {
    return parseInt(crDate.split('-')[0], 10);
}

function crGetWeekOfYearFromDate(crDate) {
    let firstDayOfYear = myGetFirstDayObjFromYearWeek(crGetYearFromDate(crDate), 1);
    let sYear = parseInt(crDate.substring(0, 4), 10);
    let sMon = parseInt(crDate.substring(5, 7), 10);
    let sDay = parseInt(crDate.substring(8, 10), 10);
    let sDate = new Date(sYear, sMon - 1, sDay);
    let betweenDays = daysBetween(firstDayOfYear, sDate);
    return (Math.floor(betweenDays / 7) + 1);
}

function daysBetween(day1, day2) {
    let betweenDays = (day2 - day1) / (1000 * 60 * 60 * 24);
    return Math.abs(betweenDays);
}

function crGetYearWeekFromDate(crDate) {
    //return ('W' + String(crGetYearFromDate(crDate)).substring(2, 4) + '.' + crGetWeekOfYearFromDate(crDate));
    return sprintf('W%02d.%02d', parseInt(String(crGetYearFromDate(crDate)).substring(2, 4), 10), crGetWeekOfYearFromDate(crDate));
}

function crGetCrDateFromDayObj(dayObj) {
    return sprintf('%04d-%02d-%02d', dayObj.getFullYear(), dayObj.getMonth() + 1, dayObj.getDate());
}

function myGetFirstDayObjFromYearWeek(myYear, myWeek) {
    let daysInWeek = 7;
    let thisDay = new Date(myYear, 0, 1);
    let thisDayOfWeek = thisDay.getDay(); // 0 (Sun) ~ 6 (Mon)
    let daysToWeekTwo = daysInWeek - thisDayOfWeek;

    if (myWeek === 1) {
        thisDay.setTime(thisDay.getTime() - thisDayOfWeek * 24 * 60 * 60 * 1000);
    } else {
        thisDay.setTime(thisDay.getTime() + (daysToWeekTwo + (myWeek - 2) * daysInWeek) * 24 * 60 * 60 * 1000);
    }

    //console.log(sprintf('%04d-%02d-%02d', thisDay.getFullYear(), thisDay.getMonth()+1, thisDay.getDate()));
    return thisDay;
}

function crGetDayHashFromYearWeek(myYear, myWeek) {
    let daysInWeek = 7;
    let crDateHash = {};
    let dayObj = myGetFirstDayObjFromYearWeek(myYear, myWeek);

    for (let i = 0; i < daysInWeek; i++) {
        crDateHash[crGetCrDateFromDayObj(dayObj)] = '';
        dayObj.setDate(dayObj.getDate() + 1);
    }

    return crDateHash;
}

function crGetYearWeekListByDate(crDateFrom, crDateTo) {
    let crYearFrom = crGetYearFromDate(crDateFrom);
    let crYearTo = crGetYearFromDate(crDateTo);
    let crWeekFrom = crGetWeekOfYearFromDate(crDateFrom);
    let crWeekTo = crGetWeekOfYearFromDate(crDateTo);
    let weekFullList = [];

    let crWeek = crWeekFrom;
    //let crYear = crYearFrom;
    for (let crYear = crYearFrom; crYear <= crYearTo; crYear++) {
        for (crWeek = crWeekFrom;
            ((crYear < crYearTo) && (crWeek <= 52)) || ((crYear === crYearTo) && (crWeek <= crWeekTo)); crWeek++) {
            let intYear = parseInt(String(crYear).substring(2, 4), 10);
            let intWeek = parseInt(crWeek);
            weekFullList.push(sprintf('W%02d.%02d', parseInt(String(crYear).substring(2, 4), 10), crWeek));
        }
        crWeekFrom = 1;
    }
    return weekFullList;
}

function simplifyDisplayWeekList(weekList) {
    let simplifiedDisplayWeekList = [];
    let isFirstWeek = true;
    let previousYearText = '00';
    for (let i = 0; i < weekList.length; i++) {
        let weekText = weekList[i];
        let yearText = weekText.substring(1, 3);
        if (yearText !== previousYearText) {
            isFirstWeek = true;
        }
        previousYearText = yearText;
        if (!isFirstWeek) {
            weekText = 'W' + weekText.split('.')[1];
        } else {
            isFirstWeek = false;
        }
        simplifiedDisplayWeekList.push(weekText);
    }
    return simplifiedDisplayWeekList;
}

function str_repeat(i, m) {
    let o = [];
    while (m > 0) {
        o.push(i);
        m--;
    }
    return o.join('');
}

function sprintf() {
    var i = 0,
        a, f = arguments[i++],
        o = [],
        m, p, c, x, s = '';
    while (f) {
        if (m = /^[^\x25]+/.exec(f)) {
            o.push(m[0]);
        } else if (m = /^\x25{2}/.exec(f)) {
            o.push('%');
        } else if (m = /^\x25(?:(\d+)\$)?(\+)?(0|'[^$])?(-)?(\d+)?(?:\.(\d+))?([b-fosuxX])/.exec(f)) {
            if (((a = arguments[m[1] || i++]) === null) || (a === undefined)) {
                throw ('Too few arguments.');
            }
            if (/[^s]/.test(m[7]) && (typeof (a) !== 'number')) {
                throw ('Expecting number but found ' + typeof (a));
            }
            switch (m[7]) {
                case 'b':
                    a = a.toString(2);
                    break;
                case 'c':
                    a = String.fromCharCode(a);
                    break;
                case 'd':
                    a = parseInt(a);
                    break;
                case 'e':
                    a = m[6] ? a.toExponential(m[6]) : a.toExponential();
                    break;
                case 'f':
                    a = m[6] ? parseFloat(a).toFixed(m[6]) : parseFloat(a);
                    break;
                case 'o':
                    a = a.toString(8);
                    break;
                case 's':
                    a = ((a = String(a)) && m[6] ? a.substring(0, m[6]) : a);
                    break;
                case 'u':
                    a = Math.abs(a);
                    break;
                case 'x':
                    a = a.toString(16);
                    break;
                case 'X':
                    a = a.toString(16).toUpperCase();
                    break;
            }
            a = (/[def]/.test(m[7]) && m[2] && a >= 0 ? '+' + a : a);
            c = m[3] ? m[3] === '0' ? '0' : m[3].charAt(1) : ' ';
            x = m[5] - String(a).length - s.length;
            p = m[5] ? str_repeat(c, x) : '';
            o.push(s + (m[4] ? a + p : p + a));
        } else {
            throw ('Huh ?!');
        }
        f = f.substring(m[0].length);
    }
    return o.join('');
}

export {
    crGetYearWeekListByDate,
    crGetYearWeekFromDate,
    crGetYearFromDate,
    crGetWeekOfYearFromDate,
    sprintf,
    simplifyDisplayWeekList,
    crGetTodayText,
    getNowTimeText,
    getSecondBetween,
    crDaysBetween
};