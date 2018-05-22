import 'jquery';
import {
    onKeywordChanged,
    onKeywordMergeTypeChanged,
    oncrOpenDayChanged,
    oncrInDayChanged,
    oncrClassChanged,
    oncrStateChanged,
    onCommentViewChanged,
    oncrTimeTrackingChanged,
    onshowRemarkFieldChanged,
    onshowMpTrackingFieldChanged,
    onshowAnalysisFieldChanged,
    onFilterGroupChanged,
    onFilterTeamChanged
} from '../actions/filter';
import store from '../store';

const jq = jQuery.noConflict();

jq(document).on('click', '.cr-filterTable .add-keyword', (e) => {
    let state = store.getState();
    let curMergeType = 'AND';
    if (state.KeywordMergeType === '+') {
        curMergeType = 'OR';
    }

    let keywordElement = "<span class='label-key'>" + curMergeType + "</span><span class='search-keyword-input'><input type='text' class='keywordFilter'></span>";

    jq(document)
        .find('.search-keyword-input')
        .last()
        .after(keywordElement);

    let inputNumber = jq(document).find('.search-keyword-input').length;
    if (inputNumber === 3) {
        jq(e.currentTarget)
            .slideToggle()
            .siblings()
            .hide('show');
    }

    jq('.keywordFilter').keydown(function (e) {
        var key = e.charCode ? e.charCode : e.keyCode ? e.keyCode : 0;
        if (key === 13) { // press 'Enter'
            let keywordFilters = [];
            jq('.keywordFilter').each(function () {
                var thisFilterValue = jq(this).val();
                if (thisFilterValue !== '') {
                    //alert(thisFilterValue);
                    keywordFilters.push(thisFilterValue);
                }
            });
            store.dispatch(onKeywordChanged(keywordFilters));
            //GV.inputKeywordNum = GV.keywordFilters.length;


        }
    });
});

jq('.keywordFilter').keydown(function (e) {
    var key = e.charCode ? e.charCode : e.keyCode ? e.keyCode : 0;
    if (key === 13) { // press 'Enter'
        let keywordFilters = [];
        jq('.keywordFilter').each(function () {
            var thisFilterValue = jq(this).val();
            if (thisFilterValue !== '') {
                //alert(thisFilterValue);
                keywordFilters.push(thisFilterValue);
            }
        });
        store.dispatch(onKeywordChanged(keywordFilters));
        //GV.inputKeywordNum = GV.keywordFilters.length;


    }
});

jq(document).on('click', '.cr-filterTable .label-key', (e) => {
    let oldText = jq(e.currentTarget).text();
    let newText = oldText === "OR" ? "AND" : "OR";
    let newType = '&';
    if (newText === 'OR') {
        newType = '+';
    }
    store.dispatch(onKeywordMergeTypeChanged(newType));
    jq(e.currentTarget)
        .parent()
        .find('.label-key')
        .text(newText);
});

jq('#crOpenDay').keydown(function (e) {
    console.log('CR openday clicked action....');
    let key = e.charCode ? e.charCode : e.keyCode ? e.keyCode : 0;
    if (key === 13) { // press 'Enter'
        let crOpenDayInput = jq('#crOpenDay').val();
        try {
            parseInt(crOpenDayInput, 10);
        } catch (e) {
            crOpenDayInput = '0';
        }

        store.dispatch(oncrOpenDayChanged(parseInt(crOpenDayInput, 10)));
    }
});
jq('#crInDay').keydown(function (e) {
    let key = e.charCode ? e.charCode : e.keyCode ? e.keyCode : 0;
    if (key === 13) { // press 'Enter'
        let crInDayInput = jq('#crInDay').val();
        try {
            parseInt(crInDayInput, 10);
        } catch (e) {
            crInDayInput = '0';
        }

        store.dispatch(oncrInDayChanged(parseInt(crInDayInput, 10)));
    }
});

jq('.crClassCheckbox').change(function () {
    let crFilterTypeVal = jq(this).val();
    let state = store.getState();
    let crclassfilter = JSON.parse(JSON.stringify(state.crClassFilter));
    if (jq(this).is(':checked')) {
        crclassfilter[crFilterTypeVal] = 1;
    } else {
        crclassfilter[crFilterTypeVal] = 0;
    }
    store.dispatch(oncrClassChanged(crclassfilter));
});

jq('.crStateCheckbox').change(function () {
    let crFilterTypeVal = jq(this).val();
    let state = store.getState();
    let crstatefilter = JSON.parse(JSON.stringify(state.crStateFilter));
    if (jq(this).is(':checked')) {
        crstatefilter[crFilterTypeVal] = 1;
    } else {
        crstatefilter[crFilterTypeVal] = 0;
    }
    store.dispatch(oncrStateChanged(crstatefilter));
});

jq('.commentViewRadio').click(function () {
    store.dispatch(onCommentViewChanged(jq(this).val()));
});

jq('#timeCheckbox').change(function () {
    if (jq(this).is(':checked')) {
        store.dispatch(oncrTimeTrackingChanged(true));
    } else {
        store.dispatch(oncrTimeTrackingChanged(false));
    }
});

jq('#mpTrackingCheckbox').change(function () {
    if (jq(this).is(':checked')) {
        store.dispatch(onshowMpTrackingFieldChanged(true));
    } else {
        store.dispatch(onshowMpTrackingFieldChanged(false));
    }
});

jq('#crAnalysisCheckbox').change(function () {
    if (jq(this).is(':checked')) {
        store.dispatch(onshowAnalysisFieldChanged(true));
    } else {
        store.dispatch(onshowAnalysisFieldChanged(false));
    }
});

jq('#crRemarkCheckbox').change(function () {
    if (jq(this).is(':checked')) {
        store.dispatch(onshowRemarkFieldChanged(true));
    } else {
        store.dispatch(onshowRemarkFieldChanged(false));
    }
});

jq('#selectGroup').change(function () {
    let group = jq('#selectGroup').children('option:selected').val();
    store.dispatch(onFilterGroupChanged(group));
});

jq('#selectTeam').change(function () {
    let team = jq('#selectTeam').children('option:selected').val();
    store.dispatch(onFilterTeamChanged(team));
});