import json

from cr_review_sys.const import Const
from cr_review_sys.models import Activity
from cr_review_sys.serializers import ActSerializer
from cr_review_sys.views import CrReviewBaseView


class SubmitActivityConfigView(CrReviewBaseView):

#         return super(SubmitActivityConfigView, self).dispatch(request, *args, **kwargs)
#     @method_decorator(csrf_exempt)
#     def dispatch(self, request, *args, **kwargs):

    def api_post(self, request):
        body_info = json.loads(request.body.decode('utf-8'))
        activity_id = body_info.get(Const.ACTIVITY_ID, None)

        if activity_id:
            act = Activity(**body_info)
            act.save()
            serializer = ActSerializer(instance=act)
        else:
            # create Activity
            act = Activity.objects.create(**body_info)
            serializer = ActSerializer(instance=act)
        return serializer.data
