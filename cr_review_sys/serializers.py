from rest_framework import serializers

from cr_review_sys.models import ActivityCategory, Activity, ActivityCr,\
    CrReviewinfo, CrReviewcomments, Users


class ActSerializer(serializers.ModelSerializer):
    date_from = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    date_to = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = Activity
        fields = ('activity_id', 'activity_cat_id', 'activity_name', 'date_from', 'date_to',
                  'active', 'db_scope', 'owner', 'modifier', 'days_of_bug',
                  'days_of_others', 'additional_mail_to', 'additional_mail_cc',
                  'mail_to_assignee', 'mail_to_manager', 'mail_trigger_time',
                  'additional_mail_fields', 'user_defined_fields1', 'user_defined_fields2')


class ActCatSerializer(serializers.ModelSerializer):
    activities = ActSerializer(
        source='get_activity',
        many=True,
        read_only=True
    )

    class Meta:
        model = ActivityCategory
        fields = ('activity_cat_id', 'activity_cat_name',
                  'default_activity', 'owner', 'activities')
        read_only_fields = ('activity_cat_id', )


class ActCrSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='cr.title', read_only=True)
    priority = serializers.CharField(source='cr.priority', read_only=True)
    cr_class = serializers.CharField(source='cr.cr_class', read_only=True)
    state = serializers.CharField(source='cr.state', read_only=True)
    cr_source = serializers.CharField(source='cr.cr_source', read_only=True)
    submitter = serializers.CharField(source='cr.submitter', read_only=True)
    submit_date = serializers.DateTimeField(
        source='cr.submit_date', read_only=True)
    assignee = serializers.CharField(source='cr.assignee', read_only=True)
    assignee_dept = serializers.CharField(
        source='cr.assignee_dept', read_only=True)
    dispatch_count = serializers.IntegerField(
        source='cr.dispatch_count', read_only=True)
    assign_date = serializers.DateTimeField(
        source='cr.assign_date', read_only=True)
    resolve_date = serializers.DateTimeField(
        source='cr.resolve_date', read_only=True)
    resolve_time = serializers.IntegerField(
        source='cr.resolve_time', read_only=True)
    resolution = serializers.CharField(source='cr.resolution', read_only=True)
    customer_company = serializers.CharField(
        source='cr.customer_company', read_only=True)
    solution = serializers.CharField(source='cr.solution', read_only=True)
    inner_solution = serializers.CharField(
        source='cr.inner_solution', read_only=True)
    solution_category_level1 = serializers.CharField(
        source='cr.solution_category_level1', read_only=True)
    solution_category_level2 = serializers.CharField(
        source='cr.solution_category_level2', read_only=True)
    platform_group = serializers.CharField(
        source='cr.platform_group', read_only=True)
    patch_id = serializers.CharField(source='cr.patch_id', read_only=True)
    sv_mce_effort = serializers.CharField(
        source='cr.sv_mce_effort', read_only=True)
    plmn1 = serializers.CharField(source='cr.plmn1', read_only=True)
    plmn2 = serializers.CharField(source='cr.plmn2', read_only=True)
    country = serializers.CharField(source='cr.country', read_only=True)
    countrycode = serializers.CharField(
        source='cr.countrycode', read_only=True)
    operator = serializers.CharField(source='cr.operator', read_only=True)
    md_info_country = serializers.CharField(
        source='cr.md_info_country', read_only=True)
    md_info_op_name = serializers.CharField(
        source='cr.md_info_op_name', read_only=True)
    rat1 = serializers.CharField(source='cr.rat1', read_only=True)
    rat2 = serializers.CharField(source='cr.rat2', read_only=True)
    cell_id = serializers.CharField(source='cr.cell_id', read_only=True)
    tac_lac = serializers.CharField(source='cr.tac_lac', read_only=True)
    hw_project_id = serializers.CharField(
        source='cr.hw_project_id', read_only=True)
    bug_reason = serializers.CharField(source='cr.bug_reason', read_only=True)
    local_issue = serializers.CharField(
        source='cr.local_issue', read_only=True)
    test_category = serializers.CharField(
        source='cr.test_category', read_only=True)
    other_info = serializers.CharField(
        source='cr.other_info', read_only=True)

    @staticmethod
    def setup_eager_loading(queryset):
        """ Perform necessary eager loading of data. """

        # select_related for "to-one" relationships
        queryset = queryset.select_related('cr')

        return queryset

    class Meta:
        model = ActivityCr
        fields = ('cr_id', 'title', 'priority', 'cr_class', 'state', 'cr_source', 'submitter', 'submit_date', 'assignee', 'assignee_dept', 'dispatch_count', 'resolve_date', 'assign_date', 'resolve_time', 'resolution', 'customer_company', 'solution', 'inner_solution', 'solution_category_level1', 'solution_category_level2',
                  'platform_group', 'patch_id', 'sv_mce_effort', 'plmn1', 'plmn2', 'country', 'countrycode', 'operator', 'md_info_country', 'md_info_op_name', 'rat1', 'rat2', 'cell_id', 'tac_lac', 'hw_project_id', 'bug_reason', 'local_issue', 'test_category', 'other_info')
        extra_kwargs = {
            'url': {'lookup_field': 'activity_id'}
        }


class CrReviewInfoSerializer(serializers.ModelSerializer):
    updated_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = CrReviewinfo
        fields = '__all__'


class CrReviewCommentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrReviewcomments
        fields = '__all__'


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ('login_name', 'full_name')
