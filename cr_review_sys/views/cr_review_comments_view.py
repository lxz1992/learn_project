from rest_framework import generics

from cr_review_sys.models import CrReviewcomments
from cr_review_sys.serializers import CrReviewCommentsSerializer


class CrReviewCommentsView(generics.ListAPIView):
    serializer_class = CrReviewCommentsSerializer
    lookup_url_kwarg = "activity_id"

    def get_queryset(self):

        queryset = None
        activity_id = self.kwargs.get(self.lookup_url_kwarg)
        cr_id = self.request.GET.get("cr_id")

        if cr_id:
            queryset = CrReviewcomments.objects.filter(
                activity_id=activity_id, cr_id=cr_id)
        else:
            queryset = CrReviewcomments.objects.filter(activity_id=activity_id)
        return queryset
