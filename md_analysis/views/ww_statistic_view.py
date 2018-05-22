# Create your views here.
from md_analysis.const import MdMeta
from md_analysis.services.ww_statistic_service import WwStatisticService
from md_analysis.views import MdAnalysisBaseView


class WWStatisticTop10View(MdAnalysisBaseView):

    def __init__(self, **kwds):
        super(WWStatisticTop10View, self).__init__(**kwds)
        self.wwstatistic_service = WwStatisticService()

    def api_get(self, request):
        all_data = {}

        latest_sync = self._sync_helper.get_lastest_sync_job_id(
            MdMeta.ActivityId)

        all_data = self.wwstatistic_service.get_top10_all_data(
            latest_sync['sync_job_id'])

        all_data.update({'updateTime': latest_sync['update_time']})

        return all_data


class WWStatisticMapView(MdAnalysisBaseView):

    def __init__(self, **kwds):
        super(WWStatisticMapView, self).__init__(**kwds)
        self.wwstatistic_service = WwStatisticService()

    def api_get(self, request):
        result = {}

        all_data = {}
        all_country_code = []
        latest_sync = self._sync_helper.get_lastest_sync_job_id(
            MdMeta.ActivityId)

        (all_data, all_country_code) = self.wwstatistic_service.get_map_all_data(
            latest_sync['sync_job_id'])

        result.update(
            {'map': {'data': all_data, 'countryCode': all_country_code}})
        result.update({'updateTime': latest_sync['update_time']})

        return result
