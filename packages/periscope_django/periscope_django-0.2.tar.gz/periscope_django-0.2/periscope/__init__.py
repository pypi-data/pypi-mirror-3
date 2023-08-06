from django.conf import settings
try:
  from django.conf.urls import include, url
except ImportError:
  from django.conf.urls.defaults import include, url
root_project = __import__(settings.ROOT_URLCONF)
root_project.urls.urlpatterns += (url(r'^periscope/', include('periscope.urls')),)
