from rest_framework import generics

from cr_review_sys.models import ActivityCr
from cr_review_sys.serializers import ActCrSerializer


class ActCrView(generics.ListAPIView):
    serializer_class = ActCrSerializer
    lookup_url_kwarg = "activity_id"

    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        activity_id = self.kwargs.get(self.lookup_url_kwarg)
        queryset = ActivityCr.objects.filter(active=1, activity_id=activity_id)

        cr_db = self.request.GET.get("cr_db")
        if cr_db:
            _cr_db = cr_db.split(",")
            queryset = queryset.filter(cr_db__in=_cr_db)
        queryset = self.get_serializer_class().setup_eager_loading(queryset)
        return queryset
