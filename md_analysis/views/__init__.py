from django.http.response import JsonResponse
from django.shortcuts import render
from django.views.generic.base import View

from md_analysis.errors import MdErrorCode, ParseResultNotFound, DbDataNotFound,\
    HwPrjIdNotFound
from my_to_do.util.sync_helper import SyncHelper
from my_to_do.views import MyToDoBaseView


def index(request):
    # Create your views here.
    return render(
        request,
        'md_analysis.html',  # front end will overwrite this template
    )


class MdAnalysisBaseView(MyToDoBaseView):

    def __init__(self, **kwds):
        super(MdAnalysisBaseView, self).__init__(**kwds)

    def get(self, request):
        result = {}
        try:
            result = self.api_get(request)
        except (ParseResultNotFound, DbDataNotFound) as e:
            self.logger.exception(e.msg)
            result["error_code"] = e.code
            result["error_msg"] = e.msg
        except Exception as e:
            msg = "unknown exception: {}".format(e)
            self.logger.exception(msg)
            result["error_code"] = MdErrorCode.UnknownError
            result["error_msg"] = msg
        return JsonResponse(result)
    # for the inheritance override

    def api_get(self, request):
        return {}
