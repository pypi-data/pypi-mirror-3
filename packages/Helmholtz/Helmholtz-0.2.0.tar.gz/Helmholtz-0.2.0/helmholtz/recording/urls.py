from django.conf import settings
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
    #url(r'^data/(?P<lab>\w+(\s\S+)*)/(?P<expt>\w[\w\-]*)/(?P<block>\w[\w\-]*)/$', 'helmholtz.recording.views.block_detail', {'template':"block_detail.html"}, name='block-detail'),
    url(r'^data/(?P<lab>\w+(\s\S+)*)/(?P<expt>[a-zA-Z0-9- ]+)/(?P<block>[a-zA-Z0-9-, ]+)/$', 'helmholtz.recording.views.block_detail', {'template':"block_detail.html"}, name='block-detail'),
    
    url(r"""^data/(?P<lab>\w+(\s\S+)*)/(?P<expt>\w[\w\-]*)/(?P<block>\w[\w\-]*)/(?P<protocol>\w+[\w\W]*)/(?P<file>\w+[\w\W]*)/(?P<episode>\d+)/(?P<channel>\d+)/(?P<type_name>\w+[\w\W]*)/$""", 'helmholtz.recording.views.signal_detail', {'template':"signal_detail.html"}, name='signal-detail'),

    url(r"""^data/(?P<lab>\w+(\s\S+)*)/(?P<expt>[a-zA-Z0-9-, ]+)/(?P<block>[a-zA-Z0-9-, ]+)/(?P<protocol>[a-zA-Z0-9-., =]+)/$""", 'helmholtz.recording.views.protocol_detail', {'template':"protocol_detail.html"}, name='protocol-detail'),
)
