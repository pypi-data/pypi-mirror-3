#encoding:utf-8
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
    url(r'^request/file/(?P<file_id>\w*)/$', 'helmholtz.access_request.views.request_file', name='download-request'),
    url(r'^request/accept/(?P<request_id>\w*)/$', 'helmholtz.access_request.views.accept_request', name='accept-request'),
    url(r'^request/set_permission/(?P<request_id>\w*)/$', 'helmholtz.access_request.views.set_access_control', {'template':'dialog.html'}, name='set-permission'),
    url(r'^request/refuse/(?P<request_id>\w*)/$', 'helmholtz.access_request.views.refuse_request', name='refuse-request'),
    url(r'^request/delete/(?P<request_id>\w*)/$', 'helmholtz.access_request.views.delete_request', name='delete-request'),
) 
