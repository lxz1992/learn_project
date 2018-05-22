'''
Created on Feb 8, 2018

@author: mtk06979
'''


class MyTodoErrorCode:
    UnknownError = 1
    LoginError = 2


class UnknownError(Exception):

    CODE = MyTodoErrorCode.UnknownError
    MSG = "unknown my todo error"


class LoginError(Exception):

    CODE = MyTodoErrorCode.LoginError
    MSG = "fail to authenticate user, wrong account/password"
