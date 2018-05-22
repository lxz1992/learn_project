# Create your views here.
from md_analysis.const import MdMeta
from md_analysis.services.resolved_eservices_service import ResolvedEservicesService
from md_analysis.views import MdAnalysisBaseView


class ResolvedEservicesView(MdAnalysisBaseView):

    def __init__(self, **kwds):
        super(ResolvedEservicesView, self).__init__(**kwds)
        self.resolved_eservice_service = ResolvedEservicesService()

    def api_get(self, request):
        result = {}

        latest_sync = self._sync_helper.get_lastest_sync_job_id(
            MdMeta.ActivityId)

        all_data = self.resolved_eservice_service.get_resolved_eservices_all_data(
            latest_sync['sync_job_id'])

        result.update({'resolved': all_data})
        result.update({'updateTime': latest_sync['update_time']})

        return result
