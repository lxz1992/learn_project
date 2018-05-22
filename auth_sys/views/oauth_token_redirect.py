'''
Created on Mar 6, 2018

@author: mtk06979
'''
import base64

from django.shortcuts import render

from auth_sys.models import Application
from oauth2_provider.models import Grant


def oauth_token_redirect(request):
    # Create your views here.
    code = request.GET.get("code")
    grant = Grant.objects.get(code=code)
    auth = "{}:{}".format(grant.application.client_id, grant.application.client_secret)
    encode_auth = base64.b64encode(auth.encode()).decode("ascii")

    return render(
        request,
        # front end will overwrite this template
        'oauth_redirect.html',  context={'AUTH_CODE': encode_auth}
    )
