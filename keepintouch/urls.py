"""keepintouch URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
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

from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.conf.urls.static import static

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^select2/', include('django_select2.urls')),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^qumon/', include('django_rq.urls')),
    url(r'^account/password/', include('password_reset.urls')),
    url(r'^', include('core.urls', namespace='core', app_name='core')),
    url(r'^messaging/', include('messaging.urls', namespace='messaging', app_name='messaging')),
    url(r'^reports/', include('reportng.urls', namespace='reports', app_name='reports')),
    url(r'^', include('gomez.urls', namespace='gomez', app_name='gomez')),
    url(r'^callup/', include('kitcall.urls', namespace='callup', app_name='callup')),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)#+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = 'In.Touch Email+SMS Administration'