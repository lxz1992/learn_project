# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or
# field names.
from __future__ import unicode_literals

from django.db import models


class Activity(models.Model):
    activity_id = models.AutoField(primary_key=True)
    activity_cat = models.ForeignKey('ActivityCategory', models.DO_NOTHING, blank=True, null=True)
    activity_name = models.CharField(max_length=250, blank=True, null=True)
    date_from = models.DateTimeField(blank=True, null=True)
    date_to = models.DateTimeField(blank=True, null=True)
    active = models.NullBooleanField()
    created_time = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    updated_time = models.DateTimeField(blank=True, null=True, auto_now=True)
    owner = models.CharField(max_length=30, blank=True, null=True)
    modifier = models.CharField(max_length=30, blank=True, null=True)
    days_of_bug = models.BigIntegerField(blank=True, null=True)
    days_of_others = models.BigIntegerField(blank=True, null=True)
    additional_mail_to = models.TextField(blank=True, null=True)
    additional_mail_cc = models.TextField(blank=True, null=True)
    mail_to_assignee = models.FloatField(blank=True, null=True)
    mail_to_manager = models.FloatField(blank=True, null=True)
    mail_trigger_time = models.TextField(blank=True, null=True)
    additional_mail_fields = models.TextField(blank=True, null=True)
    user_defined_fields1 = models.TextField(blank=True, null=True)
    user_defined_fields2 = models.TextField(blank=True, null=True)
    db_scope = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'activity'


class ActivityCategory(models.Model):
    activity_cat_id = models.AutoField(primary_key=True)
    activity_cat_name = models.CharField(max_length=50, blank=True, null=True)
    active = models.NullBooleanField()
    relation_table = models.TextField(blank=True, null=True)
    default_activity = models.IntegerField(blank=True, null=True)
    owner = models.CharField(max_length=30, blank=True, null=True)
    created_time = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    updated_time = models.DateTimeField(blank=True, null=True, auto_now=True)
    act_cat_type = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'activity_category'

    def get_activity(self):
        acts = Activity.objects.filter(activity_cat_id=self)
        return acts


class ActivityCr(models.Model):
    activity = models.ForeignKey(Activity, models.DO_NOTHING)
    cr = models.ForeignKey('Cr', models.DO_NOTHING, blank=True, null=True)
    sync_job_id = models.CharField(max_length=32, blank=True, null=True)
    created_time = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    id = models.CharField(primary_key=True, max_length=256)
    updated_time = models.DateTimeField(blank=True, null=True, auto_now=True)
    cr_db = models.CharField(max_length=10, blank=True, null=True)
    active = models.NullBooleanField()

    class Meta:
        managed = False
        db_table = 'activity_cr'


class ActivityUpdateStatus(models.Model):
    id = models.CharField(primary_key=True, max_length=50)
    status = models.CharField(max_length=20, blank=True, null=True)
    error_code = models.FloatField(blank=True, null=True)
    error_msg = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'activity_update_status'


class AuthGroup(models.Model):
    id = models.AutoField(primary_key=True)  # AutoField?
    name = models.CharField(unique=True, max_length=80, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.AutoField(primary_key=True)  # AutoField?
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    id = models.AutoField(primary_key=True)  # AutoField?
    name = models.CharField(max_length=255, blank=True, null=True)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    id = models.AutoField(primary_key=True)  # AutoField?
    password = models.CharField(max_length=128, blank=True, null=True)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(
        unique=True, max_length=150, blank=True, null=True)
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    email = models.CharField(max_length=254, blank=True, null=True)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.AutoField(primary_key=True)  # AutoField?
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.AutoField(primary_key=True)  # AutoField?
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class CesSpecific(models.Model):
    id = models.CharField(primary_key=True, max_length=256)
    activity_id = models.FloatField(blank=True, null=True)
    sync_job_id = models.CharField(max_length=32, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    operator = models.CharField(max_length=100, blank=True, null=True)
    priority = models.CharField(max_length=30, blank=True, null=True)
    cr_count = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ces_specific'


class Cr(models.Model):
    cr_id = models.CharField(primary_key=True, max_length=13)
    title = models.CharField(max_length=254, blank=True, null=True)
    priority = models.CharField(max_length=30, blank=True, null=True)
    cr_class = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=254, blank=True, null=True)
    cr_source = models.CharField(max_length=50, blank=True, null=True)
    bu_type = models.CharField(max_length=10, blank=True, null=True)
    submitter = models.CharField(max_length=254, blank=True, null=True)
    submit_date = models.DateTimeField(blank=True, null=True)
    assignee = models.CharField(max_length=254, blank=True, null=True)
    assignee_dept = models.CharField(max_length=100, blank=True, null=True)
    dispatch_count = models.FloatField(blank=True, null=True)
    assign_date = models.DateTimeField(blank=True, null=True)
    resolve_date = models.DateTimeField(blank=True, null=True)
    resolve_time = models.FloatField(blank=True, null=True)
    resolution = models.CharField(max_length=30, blank=True, null=True)
    customer_company = models.CharField(max_length=50, blank=True, null=True)
    solution = models.TextField(blank=True, null=True)
    inner_solution = models.TextField(blank=True, null=True)
    solution_category_level1 = models.CharField(
        max_length=128, blank=True, null=True)
    solution_category_level2 = models.CharField(
        max_length=128, blank=True, null=True)
    platform_group = models.CharField(max_length=80, blank=True, null=True)
    patch_id = models.CharField(max_length=100, blank=True, null=True)
    sv_mce_effort = models.CharField(max_length=50, blank=True, null=True)
    plmn1 = models.CharField(max_length=100, blank=True, null=True)
    plmn2 = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    countrycode = models.CharField(max_length=20, blank=True, null=True)
    operator = models.CharField(max_length=100, blank=True, null=True)
    md_info_country = models.CharField(max_length=50, blank=True, null=True)
    md_info_op_name = models.CharField(max_length=100, blank=True, null=True)
    rat1 = models.CharField(max_length=100, blank=True, null=True)
    rat2 = models.CharField(max_length=100, blank=True, null=True)
    cell_id = models.CharField(max_length=100, blank=True, null=True)
    tac_lac = models.CharField(max_length=100, blank=True, null=True)
    hw_project_id = models.CharField(max_length=18, blank=True, null=True)
    created_time = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    updated_time = models.DateTimeField(blank=True, null=True, auto_now=True)
    is_active = models.CharField(max_length=1, blank=True, null=True)
    bug_reason = models.CharField(max_length=128, blank=True, null=True)
    local_issue = models.CharField(max_length=300, blank=True, null=True)
    test_category = models.CharField(max_length=300, blank=True, null=True)
    other_info = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cr'


class CrReviewcomments(models.Model):
    id = models.AutoField(primary_key=True)
    cr_id = models.CharField(max_length=13, blank=True, null=True)
    activity_id = models.IntegerField(blank=True, null=True)
    login_name = models.CharField(max_length=30, blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True, auto_now=True)
    review_comments = models.TextField(blank=True, null=True)
    is_synced = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cr_reviewcomments'


class CrReviewinfo(models.Model):
    cr_id = models.CharField(max_length=13)
    updated_time = models.DateTimeField(blank=True, null=True, auto_now=True)
    sync_to_wits = models.NullBooleanField()
    waived = models.CharField(max_length=2, blank=True, null=True)
    activity_id = models.IntegerField()
    importance = models.CharField(max_length=40, blank=True, null=True)
    war_room = models.CharField(max_length=60, blank=True, null=True)
    progress = models.CharField(max_length=80, blank=True, null=True)
    remark = models.TextField(blank=True, null=True)
    reviewed = models.NullBooleanField()
    id = models.CharField(primary_key=True, max_length=100)
    additional_fields = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cr_reviewinfo'


class CrmHwProject(models.Model):
    hw_project_id = models.CharField(max_length=18, blank=True, null=True)
    hw_type = models.CharField(max_length=50, blank=True, null=True)
    hw_project_status = models.CharField(max_length=50, blank=True, null=True)
    hw_project_name = models.CharField(max_length=100, blank=True, null=True)
    company = models.CharField(max_length=50, blank=True, null=True)
    swpm_fullname = models.CharField(max_length=50, blank=True, null=True)
    platform = models.CharField(max_length=80, blank=True, null=True)
    operator = models.CharField(max_length=100, blank=True, null=True)
    fta = models.CharField(max_length=100, blank=True, null=True)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    completed = models.CharField(max_length=1, blank=True, null=True)
    is_active = models.CharField(max_length=1, blank=True, null=True)
    id = models.CharField(primary_key=True, max_length=256)

    class Meta:
        managed = False
        db_table = 'crm_hw_project'


class CrmHwProjectMilestone(models.Model):
    hw_project_id = models.CharField(max_length=18, blank=True, null=True)
    type = models.CharField(max_length=100, blank=True, null=True)
    milestone_name = models.CharField(max_length=100, blank=True, null=True)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    with_vote = models.CharField(max_length=1, blank=True, null=True)
    with_wfc = models.CharField(max_length=1, blank=True, null=True)
    with_vilte = models.CharField(max_length=1, blank=True, null=True)
    completed = models.CharField(max_length=1, blank=True, null=True)
    is_active = models.CharField(max_length=1, blank=True, null=True)
    id = models.CharField(primary_key=True, max_length=256)
    operator = models.CharField(max_length=100, blank=True, null=True)
    milestone_id = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'crm_hw_project_milestone'


class Depts(models.Model):
    dept_id = models.IntegerField(primary_key=True)
    dept_name = models.CharField(max_length=30, blank=True, null=True)
    is_active = models.NullBooleanField()
    created_time = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    updated_time = models.DateTimeField(blank=True, null=True, auto_now=True)
    site = models.CharField(max_length=10, blank=True, null=True)
    dept_mangr = models.CharField(max_length=30, blank=True, null=True)
    parent_dept = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'depts'


class DjangoAdminLog(models.Model):
    id = models.AutoField(primary_key=True)  # AutoField?
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200, blank=True, null=True)
    action_flag = models.IntegerField()
    change_message = models.TextField(blank=True, null=True)
    content_type = models.ForeignKey(
        'DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    id = models.AutoField(primary_key=True)  # AutoField?
    app_label = models.CharField(max_length=100, blank=True, null=True)
    model = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.AutoField(primary_key=True)  # AutoField?
    app = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField(blank=True, null=True)
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Fta(models.Model):
    id = models.CharField(primary_key=True, max_length=256)
    activity_id = models.FloatField(blank=True, null=True)
    sync_job_id = models.CharField(max_length=32, blank=True, null=True)
    operator = models.CharField(max_length=100, blank=True, null=True)
    area = models.CharField(max_length=50, blank=True, null=True)
    is_completed = models.CharField(max_length=1, blank=True, null=True)
    platform = models.CharField(max_length=80, blank=True, null=True)
    company = models.CharField(max_length=50, blank=True, null=True)
    period_year = models.CharField(max_length=4, blank=True, null=True)
    period_week = models.CharField(max_length=6, blank=True, null=True)
    project_count = models.FloatField(blank=True, null=True)
    will_kickoff_project_count = models.FloatField(blank=True, null=True)
    urgent_cr_count = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'fta'


class MdMccMnc(models.Model):
    mcc = models.CharField(max_length=3, blank=True, null=True)
    mcn = models.CharField(max_length=3, blank=True, null=True)
    area = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    country_code = models.CharField(max_length=20, blank=True, null=True)
    operator = models.CharField(max_length=100, blank=True, null=True)
    created_time = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    updated_time = models.DateTimeField(blank=True, null=True, auto_now=True)
    id = models.CharField(primary_key=True, max_length=256)

    class Meta:
        managed = False
        db_table = 'md_mcc_mnc'


class OpArea(models.Model):
    area = models.CharField(max_length=20, blank=True, null=True)
    operator = models.CharField(primary_key=True, max_length=100)

    class Meta:
        managed = False
        db_table = 'op_area'


class OpGroup(models.Model):
    group_name = models.CharField(max_length=50, blank=True, null=True)
    type = models.CharField(max_length=50, blank=True, null=True)
    value = models.CharField(max_length=100, blank=True, null=True)
    id = models.CharField(primary_key=True, max_length=256)

    class Meta:
        managed = False
        db_table = 'op_group'


class OpenEservices(models.Model):
    id = models.CharField(primary_key=True, max_length=256)
    activity_id = models.FloatField(blank=True, null=True)
    sync_job_id = models.CharField(max_length=32, blank=True, null=True)
    assignee_site = models.CharField(max_length=50, blank=True, null=True)
    customer_company = models.CharField(max_length=50, blank=True, null=True)
    stay_submitted = models.CharField(max_length=20, blank=True, null=True)
    priority = models.CharField(max_length=30, blank=True, null=True)
    cr_count = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'open_eservices'


class OperatorCertification(models.Model):
    id = models.CharField(primary_key=True, max_length=256)
    activity_id = models.FloatField(blank=True, null=True)
    sync_job_id = models.CharField(max_length=32, blank=True, null=True)
    operator = models.CharField(max_length=100, blank=True, null=True)
    area = models.CharField(max_length=50, blank=True, null=True)
    is_completed = models.CharField(max_length=1, blank=True, null=True)
    platform = models.CharField(max_length=80, blank=True, null=True)
    company = models.CharField(max_length=50, blank=True, null=True)
    period_year = models.CharField(max_length=4, blank=True, null=True)
    period_week = models.CharField(max_length=6, blank=True, null=True)
    project_count = models.FloatField(blank=True, null=True)
    will_kickoff_project_count = models.FloatField(blank=True, null=True)
    urgent_cr_count = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'operator_certification'


class ResolvedEserives(models.Model):
    id = models.CharField(primary_key=True, max_length=256)
    activity_id = models.FloatField(blank=True, null=True)
    sync_job_id = models.CharField(max_length=32, blank=True, null=True)
    type = models.CharField(max_length=10, blank=True, null=True)
    assignee_site = models.CharField(max_length=50, blank=True, null=True)
    customer_company = models.CharField(max_length=50, blank=True, null=True)
    period = models.CharField(max_length=8, blank=True, null=True)
    priority = models.CharField(max_length=30, blank=True, null=True)
    cr_count = models.FloatField(blank=True, null=True)
    resolve_time_count = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'resolved_eserives'


class SyncControl(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    sync_name = models.CharField(max_length=100, blank=True, null=True)
    sync_type = models.CharField(max_length=10, blank=True, null=True)
    sync_value = models.CharField(max_length=100, blank=True, null=True)
    sync_lastdate = models.DateTimeField(blank=True, null=True)
    sync_system = models.CharField(max_length=100, blank=True, null=True)
    sync_source = models.CharField(max_length=100, blank=True, null=True)
    sync_script_info = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sync_control'


class SyncJob(models.Model):
    activity_id = models.FloatField(blank=True, null=True)
    sync_job_id = models.CharField(primary_key=True, max_length=32)
    created_time = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    is_active = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sync_job'
        get_latest_by = 'created_time'


class Test(models.Model):
    id = models.CharField(primary_key=True, max_length=1)
    name = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'test'


class Users(models.Model):
    dept_id = models.IntegerField(blank=True, null=True)
    login_name = models.CharField(primary_key=True, max_length=30)
    full_name = models.CharField(max_length=50, blank=True, null=True)
    e_mail = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.NullBooleanField()
    is_admin = models.NullBooleanField()
    is_supperuser = models.NullBooleanField()
    created_time = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    updated_time = models.DateTimeField(blank=True, null=True, auto_now=True)
    dept_name = models.CharField(max_length=60, blank=True, null=True)
    site = models.CharField(max_length=10, blank=True, null=True)
    reporting_manager = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'users'


class Wwstatisticmap(models.Model):
    id = models.CharField(primary_key=True, max_length=256)
    activity_id = models.FloatField(blank=True, null=True)
    sync_job_id = models.CharField(max_length=32, blank=True, null=True)
    state = models.CharField(max_length=32, blank=True, null=True)
    period = models.CharField(max_length=4, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    operator = models.CharField(max_length=100, blank=True, null=True)
    md_class = models.CharField(max_length=50, blank=True, null=True)
    cr_count = models.FloatField(blank=True, null=True)
    urgent_cr_count = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'wwstatisticmap'


class Wwstatistictop10(models.Model):
    id = models.CharField(primary_key=True, max_length=256)
    activity_id = models.FloatField(blank=True, null=True)
    sync_job_id = models.CharField(max_length=32, blank=True, null=True)
    period = models.CharField(max_length=4, blank=True, null=True)
    type = models.CharField(max_length=10, blank=True, null=True)
    type_value = models.CharField(max_length=100, blank=True, null=True)
    priority = models.CharField(max_length=30, blank=True, null=True)
    cr_count = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'wwstatistictop10'
