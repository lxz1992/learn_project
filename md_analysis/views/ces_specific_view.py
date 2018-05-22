# Create your views here.
from md_analysis.const import MdMeta
from md_analysis.errors import MeaTop10NotFound
from md_analysis.services.ces_specific_service import CesSpecificService
from md_analysis.views import MdAnalysisBaseView


class CesSpecificByCountryView(MdAnalysisBaseView):

    def __init__(self, **kwds):
        super(CesSpecificByCountryView, self).__init__(**kwds)
        self.ces_specific_service = CesSpecificService()

    def api_get(self, request):
        result = {}

        try:
            latest_sync = self._sync_helper.get_lastest_sync_job_id(
                MdMeta.ActivityId)

            all_data = self.ces_specific_service.get_by_country_all_data(
                latest_sync['sync_job_id'])

            result.update({'Country': all_data})
            result.update({'updateTime': latest_sync['update_time']})
            
        except (MeaTop10NotFound) as e:
            self.logger.exception(e.msg)
            result["error_code"] = e.code
            result["error_msg"] = e.msg
            
        return result


class CesSpecificByGroupView(MdAnalysisBaseView):

    def __init__(self, **kwds):
        super(CesSpecificByGroupView, self).__init__(**kwds)
        self.ces_specific_service = CesSpecificService()

    def api_get(self, request):
        result = {}

        latest_sync = self._sync_helper.get_lastest_sync_job_id(
            MdMeta.ActivityId)

        all_data = self.ces_specific_service.get_by_group_all_data(
            latest_sync['sync_job_id'])

        result.update({'group': all_data})
        result.update({'updateTime': latest_sync['update_time']})
            
        return result
