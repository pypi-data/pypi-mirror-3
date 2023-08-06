from django.conf.urls.defaults import patterns, include, url
from views import provide_screen_info

urlpatterns = patterns('',
    url(r'^set_screen_info/(?P<screen_width>\d+)/(?P<screen_height>\d+)/$', provide_screen_info, name='set_screen_info'),
    url(r'^get_screen_info/', provide_screen_info, name='get_screen_info'),
)
