#encoding:utf-8
from django.conf import settings
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
    url(r'^reset/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', 'django.contrib.auth.views.password_reset_confirm', {'post_reset_redirect':'http://%s/visiondb/home/' % settings.SITE_DOMAIN}),
    url(r'^login/$', 'helmholtz.access_control.views.login_session', {'template_name':'login.html'}, name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login', {'login_url':settings.LOGIN_URL}, name='logout'),
    url(r'^download/file/(?P<file_id>\w*)/$', 'helmholtz.access_control.views.download_file', name='download-file'),
) 
