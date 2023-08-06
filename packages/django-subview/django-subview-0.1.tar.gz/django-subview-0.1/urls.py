from django.conf.urls import patterns, url

urlpatterns = patterns('subview.views',
    url(r'^/(?P<view_name>.*?)/(?P<json_params>.*?)[/]?$', 'subview_handler'),
)
