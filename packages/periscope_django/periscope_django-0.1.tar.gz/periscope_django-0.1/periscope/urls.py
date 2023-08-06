from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url('^look/$', 'periscope.views.look'),
    url('^login/$', 'periscope.views.login')
)
