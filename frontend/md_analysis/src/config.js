/*jslint node: true */
'use strict';

import cmnUtils from './util/index';

let config = ((cmnUtils.isProd()) ? {
        API: {
            STATISTICS: '/md_analysis/wwstatistic_top10/',
            WWMAP: '/md_analysis/wwstatistic_map/',
            RESOLVED_ESERVICES: '/md_analysis/resolved_eservices/',
            OPEN_ESERVICES: '/md_analysis/open_eservices/',
            OPERATOR_CERTIFICATION: '/md_analysis/op_cert_map/',
            FTA: '/md_analysis/project_status/?hw_type=FTA',
            CES_COUNTRY: '/md_analysis/ces_specific_by_country/',
            CES_GROUP: '/md_analysis/ces_specific_by_group/',
            OPERATOR_PROJECT: '/md_analysis/project_status/?hw_type=Operator',
            ISSUE_LIST: '/md_analysis/cr_list/',
            OPERATOR_PROJECT_LIST: '/md_analysis/project_list/',
            PROJECT_CR: '/md_analysis/cr_analysis_by_hwprj/',
            UPDATE_SOURCE: '/cr_review/sync_data/?db=ALPS&clan=WCX_SmartPhone'
        }
    } :
    {
        API: {
            STATISTICS: '/md_analysis/resources/json/wwstatistic_data.json',
            WWMAP: '/md_analysis/resources/json/wwmap_data.json',
            RESOLVED_ESERVICES: '/md_analysis/resources/json/resolved_data.json',
            OPEN_ESERVICES: '/md_analysis/resources/json/open_data.json',
            OPERATOR_CERTIFICATION: '/md_analysis/resources/json/operator_certification_data.json',
            FTA: '/md_analysis/resources/json/fta_data.json',
            CES_COUNTRY: '/md_analysis/resources/json/ces_MEA_data.json',
            CES_GROUP: '/md_analysis/resources/json/ces_group_data.json',
            OPERATOR_PROJECT: '/md_analysis/resources/json/operator_project_data.json',
            ISSUE_LIST: '/md_analysis/resources/json/issuelist_test.json',
            OPERATOR_PROJECT_LIST: '/md_analysis/resources/json/operator_project_list.json',
            PROJECT_CR: '/md_analysis/resources/json/operator_project_cr_state.json',
            UPDATE_SOURCE: '/md_analysis/resources/json/update_source.json'
        }
    });

export default config;