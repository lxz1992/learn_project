# Create your views here.
import logging

from md_analysis.const import MdMeta
from md_analysis.errors import MdErrorCode, OpNameNotFound
from md_analysis.services.prj_list_service import PrjListService
from md_analysis.views import MdAnalysisBaseView


class PrjListView(MdAnalysisBaseView):

    def __init__(self, **kwds):
        super(PrjListView, self).__init__(**kwds)
        self.prj_list_service = PrjListService()
        self.valid_prj_type = ["Ongoing", "Incoming"]

    def api_get(self, request):
        result = {}

        try:
            '''
            input param check
            '''
            operator = request.GET.get("op_name")

            if operator is None:
                raise OpNameNotFound()
            '''
            handle request
            '''
            latest_sync = self._sync_helper.get_lastest_sync_job_id(
                MdMeta.ActivityId)

            all_data = self.prj_list_service.get_prj_list_all_data(
                operator=operator)

            result.update({
                'aaData': all_data,
                'updateTime': latest_sync['update_time'],
                'sEcho': 1,
                'iTotalRecords': len(all_data),
                'iTotalDisplayRecords': len(all_data)
            })
        except OpNameNotFound as e:
            result["error_code"] = e.code
            result["error_msg"] = e.msg

        return result
