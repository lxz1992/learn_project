class DbTableHelper(object):
    '''
    Helper to generate id for table which id is a combination key with particular sequence
    '''

    @staticmethod
    def get_wwsta_top10_id(act_id, sync_job_id, period, figure_type, type_value, priority):
        return "{}_{}_{}_{}_{}_{}".format(act_id, sync_job_id, period, figure_type, type_value, priority)

    @staticmethod
    def get_wwsta_map_id(act_id, sync_job_id, state, period, country, operator, md_class):
        return "{}_{}_{}_{}_{}_{}_{}".format(act_id, sync_job_id, state, period, country, operator, md_class)

    @staticmethod
    def get_resolved_es_id(act_id, sync_job_id, period_type, site, customer, period, priority):
        return "{}_{}_{}_{}_{}_{}_{}".format(act_id, sync_job_id, period_type, site, customer, period, priority)

    @staticmethod
    def get_open_es_id(act_id, sync_job_id, site, customer, stay_submitted, priority):
        return "{}_{}_{}_{}_{}_{}".format(act_id, sync_job_id, site, customer, stay_submitted, priority)

    @staticmethod
    def get_operator_cert_id(act_id, sync_job_id, operator, is_completed, platform, company, period_week):
        return "{}_{}_{}_{}_{}_{}_{}".format(act_id, sync_job_id, operator, is_completed, platform, company, period_week)

    @staticmethod
    def get_fta_id(act_id, sync_job_id, is_completed, platform, company, period_week):
        return "{}_{}_{}_{}_{}_{}".format(act_id, sync_job_id, is_completed, platform, company, period_week)

    @staticmethod
    def get_ces_specific_id(act_id, sync_job_id, country, operator, priority):
        return "{}_{}_{}_{}_{}".format(act_id, sync_job_id, country, operator, priority)

    @staticmethod
    def get_crm_hw_prj_id(hw_prj_id, hw_type, operator):
        return "{}_{}_{}".format(hw_prj_id, hw_type, operator)

    @staticmethod
    def get_crm_hw_prj_milestone_id(hw_prj_id, hw_type, milestone_id, operator):
        return "{}_{}_{}_{}".format(hw_prj_id, hw_type, milestone_id, operator)

    @staticmethod
    def get_act_cr_id(act_id, cr_id):
        return "{}_{}".format(act_id, cr_id)

    @staticmethod
    def get_cr_review_info_id(cr_id, act_id):
        return "{}_{}".format(cr_id, act_id)
