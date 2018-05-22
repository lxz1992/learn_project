# Create your views here.
from md_analysis.const import MdMeta
from md_analysis.services.op_cert_map_service import OpCertMapService
from md_analysis.views import MdAnalysisBaseView


class OpCertMapView(MdAnalysisBaseView):

    def __init__(self, **kwds):
        super(OpCertMapView, self).__init__(**kwds)
        self.op_cert_map_service = OpCertMapService()

    def api_get(self, request):
        result = {}

        latest_sync = self._sync_helper.get_lastest_sync_job_id(
            MdMeta.ActivityId)

        all_data = self.op_cert_map_service.get_op_cert_map_all_data(
            latest_sync['sync_job_id'])

        result.update({'data': all_data})
        result.update({'updateTime': latest_sync['update_time']})
            
        return result
