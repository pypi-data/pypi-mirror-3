from django.conf import settings
from django.conf.urls import include, url
root_project = __import__(settings.ROOT_URLCONF)
root_project.urls.urlpatterns += (url(r'^periscope/', include('periscope.urls')),)
