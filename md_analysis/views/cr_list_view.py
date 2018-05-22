# Create your views here.
from md_analysis.const import ValidCrType, MdMeta, MdState
from md_analysis.errors import CrTypeNotFound, InvalidCrType, ParamNotFound, MdStateNotFound,\
    InvalidYearInterval
from md_analysis.services.country_code_service import CountryCodeService
from md_analysis.services.cr_list_service import CrListService
from md_analysis.views import MdAnalysisBaseView


class CrListView(MdAnalysisBaseView):

    def __init__(self, **kwds):
        super(CrListView, self).__init__(**kwds)
        self.cr_list_service = CrListService()
        self.country_code_service = CountryCodeService()

    def api_get(self, request):
        result = {}

        try:
            '''
            input param check
            '''
            cr_type = request.GET.get("cr_type")

            if cr_type is None:
                raise CrTypeNotFound()
            else:
                try:
                    # check for valid param for particular cr_type
                    param_list = getattr(ValidCrType, cr_type)

                    for each_param in param_list:
                        if request.GET.get(each_param) is None:
                            self.logger.exception(
                                "param: %s not found", each_param)
                            raise ParamNotFound()
                        self.logger.info("param: %s, check ok", each_param)
                except ParamNotFound as e:
                    raise ParamNotFound()
            '''
            handle request
            '''
            latest_sync = self._sync_helper.get_lastest_sync_job_id(
                MdMeta.ActivityId)
            act_cr_list = self._sync_helper.get_act_cr_list(
                MdMeta.ActivityId, latest_sync["sync_job_id"])

            all_data = {}

            p_state = None
            p_from_year = None
            p_to_year = None
            p_country = None
            p_group = None
            p_operator = None
            p_ww_operator = None

            if cr_type == "map_cr":
                lower_state = request.GET.get("state").lower()
                p_state = self.get_state_condition(lower_state)
                p_from_year = request.GET.get("from_year")
                p_to_year = request.GET.get("to_year")
                p_country = request.GET.get("country")
                p_ww_operator = request.GET.get("operator")
            elif cr_type == "urgent_cr":
                # operator also with white space, need to tackle later
                p_operator = request.GET.get("operator")
            elif cr_type == "ces_country_cr":
                p_country = request.GET.get("country")
            elif cr_type == "ces_group_cr":
                # group also with white space, need to tackle later
                p_group = request.GET.get("group")
            else:
                raise CrTypeNotFound()

            all_data = self.cr_list_service.get_cr_list_all_data(
                p_state, p_from_year, p_to_year, p_country, p_group, p_operator, act_cr_list, p_ww_operator)

            result.update({
                'aaData': all_data,
                'updateTime': latest_sync['update_time'],
                'sEcho': 1,
                'iTotalRecords': len(all_data),
                'iTotalDisplayRecords': len(all_data)
            })
        except (CrTypeNotFound, InvalidCrType, ParamNotFound, MdStateNotFound, InvalidYearInterval) as e:
            self.logger.exception(e.msg)
            result["error_code"] = e.code
            result["error_msg"] = e.msg

        return result

    def get_state_condition(self, lower_state):
        p_state = None

        if lower_state == MdState.Open.__name__.lower():
            p_state = MdState.Open.__name__
        elif lower_state == MdState.Resolved.__name__.lower():
            p_state = MdState.Resolved.__name__
        elif lower_state == MdState.Submit.__name__.lower():
            p_state = MdState.Submit.__name__
        else:
            raise MdStateNotFound()
        return p_state
