'''
Created on Jan 16, 2018

@author: MTK06979
'''

from django.conf import settings # import the settings file

def version_info(request):
    # return the value you want as a dictionnary. you may add multiple values in there.
    return {'BACKEND_VERSION': settings.BACKEND_VERSION}