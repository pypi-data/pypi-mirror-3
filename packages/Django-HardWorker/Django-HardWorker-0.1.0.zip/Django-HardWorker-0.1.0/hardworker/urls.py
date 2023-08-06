from django.conf.urls import patterns, url
from views import ajax_register_view, register_view, status_view, list_view

urlpatterns = patterns('',
    url(r'^ajax/register/(?P<app>\w+)/(?P<worker>\w+)/$', ajax_register_view, name = 'ajax-register-view'),
    url(r'^register/(?P<app>\w+)/(?P<worker>\w+)/$', register_view, name = 'register-view'),
    url(r'^status/$', status_view, name = 'status-view'),
    url(r'^list/$', list_view, name = 'list-view'),
)
