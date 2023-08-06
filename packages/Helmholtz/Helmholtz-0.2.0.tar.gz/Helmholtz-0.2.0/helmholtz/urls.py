from django.conf.urls.defaults import patterns, url, include

urlpatterns = patterns('',
    url(r'^home/$', 'helmholtz.views.home', {'template':"index.html"}, name='home'),
    ('^access_control/', include('helmholtz.access_control.urls')),
    ('^access_request/', include('helmholtz.access_request.urls')),
    ('^editor/', include('helmholtz.editor.urls')),
    ('^experiment/', include('helmholtz.experiment.urls')),
    ('^people/', include('helmholtz.people.urls')),
    ('^recording/', include('helmholtz.recording.urls')),
    ('^trackers/', include('helmholtz.trackers.urls')),
    ('^units/', include('helmholtz.units.urls')),
)
