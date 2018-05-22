# Create your views here.
from md_analysis.const import MdMeta
from md_analysis.errors import HwPrjIdNotFound, OpNameNotFound
from md_analysis.services.cr_analysis_by_hwprj_service import CrAnalysisByHwPrjService
from md_analysis.views import MdAnalysisBaseView


class CrAnalysisByHwPrjView(MdAnalysisBaseView):

    def __init__(self, **kwds):
        super(CrAnalysisByHwPrjView, self).__init__(**kwds)
        self.cr_analysis_by_hwprj_service = CrAnalysisByHwPrjService()

    def api_get(self, request):
        result = {}

        '''
        input param check
        '''
        hw_prj_id = request.GET.get("hw_prj_id")
        operator = request.GET.get("operator")

        try:
            if hw_prj_id is None:
                raise HwPrjIdNotFound()

            if operator is None:
                raise OpNameNotFound()

            '''
            handle request
            '''
            act_id = MdMeta.ActivityId
            latest_sync = self._sync_helper.get_lastest_sync_job_id(act_id)
            act_cr_list = self._sync_helper.get_act_cr_list(
                act_id, latest_sync["sync_job_id"])

            all_data = self.cr_analysis_by_hwprj_service.get_cr_analysis_by_hwprj_all_data(
                hw_prj_id, act_id, act_cr_list, operator)

            result.update({'updateTime': latest_sync['update_time']})
            result.update(all_data)
        except HwPrjIdNotFound as e:
            self.logger.exception(e.msg)
            result["error_code"] = e.code
            result["error_msg"] = e.msg

        return result
