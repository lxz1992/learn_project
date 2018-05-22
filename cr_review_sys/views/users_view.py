from oauth2_provider.contrib.rest_framework import permissions
from oauth2_provider.contrib.rest_framework.permissions import TokenHasScope
from rest_framework import viewsets

from cr_review_sys.models import Users
from cr_review_sys.serializers import UsersSerializer
from my_to_do import consts


class UsersViewSet(viewsets.ReadOnlyModelViewSet):
#     permission_classes = [permissions.IsAuthenticated, TokenHasScope]
#     required_scopes = [consts.OAUTH_SCOPES.WCX_FP_MOLY_READ,
#                        consts.OAUTH_SCOPES.WCX_SP_ALPS_READ]

    queryset = Users.objects.filter(is_active=1)
    serializer_class = UsersSerializer
