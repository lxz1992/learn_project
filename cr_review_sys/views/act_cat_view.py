from oauth2_provider.contrib.rest_framework import permissions
from oauth2_provider.contrib.rest_framework.permissions import TokenHasScope
from rest_framework import generics

from cr_review_sys.models import ActivityCategory
from cr_review_sys.serializers import ActCatSerializer
from my_to_do import consts


class ActCatView(generics.ListAPIView):
    '''
    By default, only query active=1
    '''
    serializer_class = ActCatSerializer
#     permission_classes = [permissions.IsAuthenticated, TokenHasScope]
#     required_scopes = [consts.OAUTH_SCOPES.WCX_FP_MOLY_READ, consts.OAUTH_SCOPES.WCX_SP_ALPS_READ]

    def get_queryset(self):
        queryset = ActivityCategory.objects.filter(active=1)
        act_cat_type = self.request.GET.get("act_cat_type")

        if act_cat_type:
            queryset = queryset.filter(act_cat_type=act_cat_type)
        return queryset
