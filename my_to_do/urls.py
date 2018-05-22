"""my_to_do URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
import os

from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from my_to_do.views import home, mytodo_login, login_view, mytodo_logout,\
    mytodo_whoami
# from django.urls.conf import path

settings_module = os.getenv('DJANGO_SETTINGS_MODULE', 'my_to_do.settings_dev')

if settings_module == 'my_to_do.settings_dev':
    from my_to_do.settings_dev import DEBUG
    from my_to_do import settings_dev as settings
else:
    from my_to_do.settings_prod import DEBUG
    from my_to_do import settings_prod as settings

urlpatterns = [
    url(r'^$', home),
    url(r'^login/$', mytodo_login),
    url(r'^logout/$', mytodo_logout),
    url(r'^accounts/login/$', login_view),
    url(r'^me/$', mytodo_whoami),
    url(r'^cr_review/', include("cr_review_sys.url")),
    url(r'^md_analysis/', include("md_analysis.url")),
    url(r'^o/', include("auth_sys.urls", namespace='oauth')),
    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
#     path('accounts/', include('django.contrib.auth.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if DEBUG:
    urlpatterns += [
        url(r'^admin/', admin.site.urls),
    ]
