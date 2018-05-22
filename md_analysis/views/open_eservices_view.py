# Create your views here.
from md_analysis.const import MdMeta
from md_analysis.services.open_eservices_service import OpenEservicesService
from md_analysis.views import MdAnalysisBaseView


class OpenEservicesView(MdAnalysisBaseView):

    def __init__(self, **kwds):
        super(OpenEservicesView, self).__init__(**kwds)
        self.open_eservice_service = OpenEservicesService()

    def api_get(self, request):
        result = {}

        latest_sync = self._sync_helper.get_lastest_sync_job_id(
            MdMeta.ActivityId)

        all_data = self.open_eservice_service.get_open_eservices_all_data(
            latest_sync['sync_job_id'])

        result.update({'open': all_data})
        result.update({'updateTime': latest_sync['update_time']})

        return result
