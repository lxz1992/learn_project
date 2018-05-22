'''
Created on Sep 11, 2017

@author: mtk06979
'''
from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from cr_review_sys.views import index, act_view
from cr_review_sys.views import users_view
from cr_review_sys.views.act_cat_view import ActCatView
from cr_review_sys.views.activity_config_upate_api import SubmitActivityConfigView
from cr_review_sys.views.cr_by_act_view import ActCrView
from cr_review_sys.views.cr_review_comments_view import CrReviewCommentsView
from cr_review_sys.views.cr_review_info_view import CrReviewInfoView
from cr_review_sys.views.submit_review_info_view import SubmitReviewInfoView
from cr_review_sys.views.sync_views import SyncDataView, SyncUsersDeptsView,\
    SyncActWhileListView


router = DefaultRouter()
router.register(r'activity', act_view.ActViewSet)
router.register(r'users', users_view.UsersViewSet)


urlpatterns = [
    url(r'^$', index),  # front end application, no need to change
    # class based view
    # sync function
    url(r'^sync_users_depts', SyncUsersDeptsView.as_view()),
    url(r'^sync_data', SyncDataView.as_view()),
    url(r'^sync_activity_while_list', SyncActWhileListView.as_view()),
    # rest api
    url(r'^api/', include(router.urls)),
    url(r'^api/cr_by_activity/(?P<activity_id>[-\w]+)/', ActCrView.as_view()),
    url(r'^api/cr_review_info/(?P<activity_id>[-\w]+)/',
        CrReviewInfoView.as_view()),
    url(r'^api/cr_review_comments/(?P<activity_id>[-\w]+)/',
        CrReviewCommentsView.as_view()),
    url(r'^api/submit_review_info/', SubmitReviewInfoView.as_view()),
    url(r'^api/activity_category/', ActCatView.as_view()),
    url(r'^api/submit_act_config/', SubmitActivityConfigView.as_view())
]
