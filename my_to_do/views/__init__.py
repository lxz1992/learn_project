'''
Created on Dec 18, 2017

@author: MTK06979
'''

import base64
import json
import logging

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.http.response import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.generic.base import View

from cr_review_sys.const import Const
from cr_review_sys.models import DjangoSession
from my_to_do.consts import AUTH_USER
from my_to_do.errors import LoginError, UnknownError
from my_to_do.util.sync_helper import SyncHelper


def home(request):
    return render(
        request,
        'home.html',
    )


def login_view(request):
    return render(
        request,
        'login.html', {"showlogin": " "}
    )


@csrf_exempt
def mytodo_whoami(request):
    result = {}
    try:
        temp = request.session.get(AUTH_USER, '{}')
        result = json.loads(temp)

    except Exception as e:
        logging.getLogger("aplogger").exception("fail to get who I am")
        result[Const.ERROR_CODE] = UnknownError.CODE
        result[Const.ERROR_MSG] = "{}: {}".format(UnknownError.MSG, e)

    return JsonResponse(result)


@require_http_methods(["GET", "POST"])
@csrf_exempt
def mytodo_login(request):
    login_result = {}
    try:
        auth = request.META['HTTP_AUTHORIZATION'].split()
        temp = base64.b64decode(auth[1].encode()).decode("utf-8")
        user_id, user_pwd = temp.split(":")
        user = authenticate(request, username=user_id, password=user_pwd)

        if not user:
            login_result[Const.ERROR_CODE] = LoginError.CODE
            login_result[Const.ERROR_MSG] = LoginError.MSG
        else:
            login(request, user)
            login_result = {
                "user": {
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "email": user.email,
                    "id": user.username,
                    "last_login": user.last_login.strftime("%Y-%m-%d_%H:%M:%S"),
                }
            }
            request.session[AUTH_USER] = json.dumps(login_result)

    except Exception as e:
        logging.getLogger("aplogger").exception("login failed")
        login_result[Const.ERROR_CODE] = UnknownError.CODE
        login_result[Const.ERROR_MSG] = "{}: {}".format(UnknownError.MSG, e)

    return JsonResponse(login_result)


@require_http_methods(["POST"])
@csrf_exempt
def mytodo_logout(request):
    logout_result = {}
    sid = request.session.session_key
    try:
        logout(request)

        if sid:
            DjangoSession.objects.filter(session_key=sid).delete()

        logout_result["result"] = "success"
    except Exception as e:
        logging.getLogger("aplogger").exception("logout failed")
        logout_result[Const.ERROR_CODE] = UnknownError.CODE
        logout_result[Const.ERROR_MSG] = "{}: {}".format(UnknownError.MSG, e)

    return JsonResponse(logout_result)


class MyToDoBaseView(View):

    _sync_helper = SyncHelper()

    # for future common security
    def __init__(self, **kwds):
        super(MyToDoBaseView, self).__init__(**kwds)

        self.logger = logging.getLogger('aplogger')
