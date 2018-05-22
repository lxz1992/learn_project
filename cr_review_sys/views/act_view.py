from oauth2_provider.contrib.rest_framework import permissions
from oauth2_provider.contrib.rest_framework.permissions import TokenHasScope
from rest_framework import viewsets

from cr_review_sys.models import Activity
from cr_review_sys.serializers import ActSerializer
from my_to_do import consts


class ActViewSet(viewsets.ReadOnlyModelViewSet):
#     permission_classes = [permissions.IsAuthenticated, TokenHasScope]
#     required_scopes = [consts.OAUTH_SCOPES.WCX_FP_MOLY_READ, consts.OAUTH_SCOPES.WCX_SP_ALPS_READ]
    queryset = Activity.objects.all()
    serializer_class = ActSerializer
