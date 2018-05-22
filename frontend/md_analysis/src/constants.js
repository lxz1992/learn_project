const MD_VIEW = {
    STATISTICS: 'WW Statistics',
    WWMAP: 'WW Statisctics map',
    RESOLVED_ESERVICES: 'Resolved Eservices',
    OPEN_ESERVICES: 'Open Eservices',
    OPERATOR_CERTIFICATION: 'Operator Certification',
    FTA: 'FTA',
    TEAM_LOADING: 'Team Loading',
    CES_SPECIFIC: 'CES Specific',
    CES_COUNTRY: 'CES_COUNTRY',
    CES_GROUP: 'CES_GROUP',
    QA_SPECIFIC: 'QA Specific',
    RF_ANT_TREND: 'RF ANT Specific(Trend)',
    RF_ANT_ISSUE: 'RF ANT Specific(Issue)',
    KNOWN_ISSUE: 'Known Issue',
    ESERVICE_BREAKDOWN: 'eServices Breakdown'
};

const MD_DATA = {
    Type: ['Customer', 'Operator', 'Country'],
    OptionSel: ['Week', 'Month', 'Year'],
    Dept: ['HQ', 'MSH', 'MSZ', 'MTI'],
    Delay: ['<1W', '1W-2W', '2W-4W', '1-2Month', '>2Month'],
    State: ['open', 'resolved'],
    State_big: ['open', 'resolved']
};

const CERT_AREA_MAP = {
    China: 'CN',
    India: 'IN',
    Aus: 'AU',
    EU: 'SE',
    Asia: 'JP',
    'North A': 'US',
    LATAM: 'BR',
    Africa: 'NG',
    //Others: 'WS',
};

const MD_UPDATE_STATUS = {
    finish : 'finish',
    ongoing: 'ongoing'
};

const MD_COLOR_MAP = {
    Assigned: '#ff0080',
    Submitted: '#f9f900',
    Working: '#00ec00',
    Reworking: '#ff9224',
    Resolved: '#0000c6',
    Verified: '#098300',
    Closed: '#adadad',
    'Modem team': '#0000c6',
    'Non modem team': '#ff00ff',
    'New bug': '#ff0000',
    'Known issue': '#ff8000',
    'Change feature': '#0000c6',
    'New feature': '#00bb00'
};

const REDUCER_NAME = {
    currentView: 'currentView',
    data: 'data',
    option: 'optoin',
    graphdata: 'graphdata',
    syncStatus: 'syncStatus'
}

export {MD_VIEW, MD_DATA, CERT_AREA_MAP, MD_UPDATE_STATUS, MD_COLOR_MAP, REDUCER_NAME};
