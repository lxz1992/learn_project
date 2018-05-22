from django.http.response import JsonResponse
from django.shortcuts import render
from django.views import View

from cr_review_sys.const import Const
from cr_review_sys.errors import CrReviewError, CrReviewErrorCode
from cr_review_sys.services.act_update_status_service import ActivityUpdateStatusService
from cr_review_sys.services.sync_service import SyncService
from md_analysis.errors import MdError
from my_to_do.views import MyToDoBaseView
from cr_review_sys.services.submit_review_info_service import SubmitReviewInfoService


def index(request):
    # Create your views here.
    return render(
        request,
        'cr_review.html',  # front end will overwrite this template
    )


class CrReviewBaseView(MyToDoBaseView):

    # double secure the singleton
    _wits_service = SyncService()
    _act_update_status_service = ActivityUpdateStatusService()
    _submit_review_info_service = SubmitReviewInfoService()

    def __init__(self, **kwds):
        super(CrReviewBaseView, self).__init__(**kwds)

    def get(self, request):
        result = {}
        try:
            result = self.api_get(request)
        except (MdError, CrReviewError) as e:
            self.logger.exception(e.msg)
            result[Const.ERROR_CODE] = e.code
            result[Const.ERROR_MSG] = e.msg

        except Exception as e:
            msg = "unknown exception: {}".format(e)
            self.logger.exception(msg)
            result[Const.ERROR_CODE] = CrReviewErrorCode.UnknownError
            result[Const.ERROR_MSG] = msg

        return JsonResponse(result)
    # for the inheritance override

    def api_get(self, request):
        return {}

    def post(self, request):
        result = {}
        try:
            result = self.api_post(request)
        except (MdError, CrReviewError) as e:
            self.logger.exception(e.msg)
            result[Const.API_DETAIL] = e.msg

        except Exception as e:
            msg = "unknown exception: {}".format(e)
            self.logger.exception(msg)
            result[Const.API_DETAIL] = msg

        return JsonResponse(result)
    # for the inheritance override

    def api_post(self, request):
        return {}
