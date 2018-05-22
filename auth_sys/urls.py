
from django.conf.urls import url

from .views import ApplicationRegistrationView, ApplicationUpdateView, CustomAuthorizationView
from auth_sys.views.oauth_token_redirect import oauth_token_redirect

urlpatterns = [
    url(r'^oauth_redirect/$', oauth_token_redirect),
    url(r'^authorize/$', CustomAuthorizationView.as_view(), name='authorize'),
    url(r'^applications/register/$', ApplicationRegistrationView.as_view(), name='register'),
    url(r'^applications/(?P<pk>[\w-]+)/update/$', ApplicationUpdateView.as_view(), name='update'),
]

app_name = "auth_sys"