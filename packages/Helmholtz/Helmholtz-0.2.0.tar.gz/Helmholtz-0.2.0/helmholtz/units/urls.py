#encoding:utf-8
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
    url(r'^base/$', 'helmholtz.units.views.base_units', name='base-units'),
    url(r'^derived/$', 'helmholtz.units.views.derived_units', name='derived-units'),
    url(r'^tree/$', 'helmholtz.units.views.unit_tree', name='unit-tree'),
)
