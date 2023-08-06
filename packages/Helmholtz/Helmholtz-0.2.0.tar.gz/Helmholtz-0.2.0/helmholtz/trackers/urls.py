#encoding:utf-8
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
    url(r'^detect_connection/$', 'helmholtz.trackers.views.detect_connection', {'view_label':"home"}, name='detect-connection'),
    url(r'^contact/delete/(?P<message_id>\w*)/$', 'helmholtz.trackers.views.delete_message', name='delete-message'),
) 
