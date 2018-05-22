# Create your views here.
import logging

from md_analysis.const import MdMeta
from md_analysis.errors import HwTypeNotFound, OpNameNotFound, InvalidHwType
from md_analysis.services.prj_status_service import PrjStatusService
from md_analysis.views import MdAnalysisBaseView


class PrjStatusView(MdAnalysisBaseView):

    def __init__(self, **kwds):
        super(PrjStatusView, self).__init__(**kwds)
        self.prj_status_service = PrjStatusService()
        self.valid_hw_type = {
            "Operator": "get_prj_status_by_operator_all_data",
            "FTA": "get_prj_status_for_FTA_all_data"
        }

    def api_get(self, request):
        result = {}

        try:
            '''
            input param check
            '''
            hw_type = request.GET.get("hw_type")
            operator = request.GET.get("op_name")

            if hw_type is None:
                raise HwTypeNotFound()
            else:
                if not (hw_type in self.valid_hw_type.keys()):
                    raise InvalidHwType()
                else:
                    if hw_type == "Operator" and operator is None:
                        raise OpNameNotFound()
            '''
            handle request
            '''
            latest_sync = self._sync_helper.get_lastest_sync_job_id(
                MdMeta.ActivityId)

            all_data = getattr(self.prj_status_service,
                               self.valid_hw_type[hw_type])(hw_type=hw_type, op_name=operator, **latest_sync)
            result.update({'data': all_data})
            result.update({'updateTime': latest_sync['update_time']})
        except (HwTypeNotFound, OpNameNotFound, InvalidHwType) as e:
            self.logger.exception(e.msg)
            result["error_code"] = e.code
            result["error_msg"] = e.msg
            
        return result
