import json

from cr_review_sys.const import Const, ReviewInfoFieldMap, SubmitReviewInfo,\
    ReviewCommentFieldMap
from cr_review_sys.errors import IncompleteParam, SubmitReviewInfoNoKey
from cr_review_sys.views import CrReviewBaseView
from my_to_do.util.compute_helper import ComputeHelper


class SubmitReviewInfoView(CrReviewBaseView):

#     @method_decorator(csrf_exempt)
#     def dispatch(self, request, *args, **kwargs):
#         return super(SubmitReviewInfoView, self).dispatch(request, *args, **kwargs)

    def api_post(self, request):
        result = {"result": "success"}
        body_info = json.loads(request.body.decode('utf-8'))
        input_param = list(body_info.keys())
        valid_param = [e.value for e in getattr(SubmitReviewInfo, "Param")]
        check_param = ComputeHelper.check_list_subset(input_param, valid_param)

        if check_param:
            if body_info[SubmitReviewInfo.Param.ACTIVITY_ID.value] and body_info[SubmitReviewInfo.Param.CR_ID.value]:
                # basic check ok, format to dic with db field name
                activity_id = body_info[SubmitReviewInfo.Param.ACTIVITY_ID.value]
                cr_id = body_info[SubmitReviewInfo.Param.CR_ID.value]
                updated_time = body_info[SubmitReviewInfo.Param.UPDATED_TIME.value]
                review_info = {
                    ReviewInfoFieldMap.WAIVED: body_info[SubmitReviewInfo.Param.WAIVED.value],
                    ReviewInfoFieldMap.IMPORTANCE: body_info[SubmitReviewInfo.Param.IMPORTANCE.value],
                    ReviewInfoFieldMap.WAR_ROOM: body_info[SubmitReviewInfo.Param.WAR_ROOM.value],
                    ReviewInfoFieldMap.PROGRESS: body_info[SubmitReviewInfo.Param.PROGRESS.value],
                    ReviewInfoFieldMap.REMARK: body_info[SubmitReviewInfo.Param.REMARK.value],
                    ReviewInfoFieldMap.ADDITIONAL_FIELDS: body_info[
                        SubmitReviewInfo.Param.ADDITIONAL_FIELDS.value]
                }
                review_comments = []

                for eachcomment in body_info[SubmitReviewInfo.Param.REVIEW_COMMENTS.value]:
                    review_comments.append({
                        ReviewCommentFieldMap.ACTIVITY_ID: body_info[SubmitReviewInfo.Param.ACTIVITY_ID.value],
                        ReviewCommentFieldMap.CR_ID: body_info[SubmitReviewInfo.Param.CR_ID.value],
                        ReviewCommentFieldMap.LOGIN_NAME: body_info[SubmitReviewInfo.Param.LOGIN_NAME.value],
                        ReviewCommentFieldMap.REVIEW_COMMENTS: eachcomment
                    })

                data = {
                    Const.UPDATED_TIME: updated_time,
                    Const.REVIEW_COMMENTS: review_comments,
                    Const.REVIEW_INFO: review_info
                }
                self._submit_review_info_service.submit_review_info_entry(
                    activity_id, cr_id, **data)
            else:
                raise SubmitReviewInfoNoKey()
        else:
            raise IncompleteParam()
        return result
