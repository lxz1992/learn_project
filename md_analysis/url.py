'''
Created on Sep 11, 2017

@author: mtk06979
'''
from django.conf.urls import url

from md_analysis.views import index
from md_analysis.views.ces_specific_view import CesSpecificByCountryView, CesSpecificByGroupView
from md_analysis.views.cr_analysis_by_hwprj_view import CrAnalysisByHwPrjView
from md_analysis.views.cr_list_view import CrListView
from md_analysis.views.op_cert_map_view import OpCertMapView
from md_analysis.views.open_eservices_view import OpenEservicesView
from md_analysis.views.prj_list_view import PrjListView
from md_analysis.views.prj_status_view import PrjStatusView
from md_analysis.views.resolved_eservices_view import ResolvedEservicesView
from md_analysis.views.ww_statistic_view import WWStatisticTop10View, WWStatisticMapView


urlpatterns = [
    url(r'^$', index),  # front end application no need to change
    # url(r'^your_generic_view_for_rest_api/$', index)  # back end implemented
    # rest api
    url(r'^wwstatistic_top10/', WWStatisticTop10View.as_view()),
    url(r'^wwstatistic_map/', WWStatisticMapView.as_view()),
    url(r'^ces_specific_by_country/', CesSpecificByCountryView.as_view()),
    url(r'^ces_specific_by_group/', CesSpecificByGroupView.as_view()),
    url(r'^resolved_eservices/', ResolvedEservicesView.as_view()),
    url(r'^open_eservices/', OpenEservicesView.as_view()),
    url(r'^op_cert_map/', OpCertMapView.as_view()),
    url(r'^project_status/', PrjStatusView.as_view()),
    url(r'^project_list/', PrjListView.as_view()),
    url(r'^cr_list/', CrListView.as_view()),
    url(r'^cr_analysis_by_hwprj/', CrAnalysisByHwPrjView.as_view()),
]
