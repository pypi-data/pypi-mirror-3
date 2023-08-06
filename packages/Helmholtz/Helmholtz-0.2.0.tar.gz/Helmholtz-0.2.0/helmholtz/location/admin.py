#encoding:utf-8
from django.contrib import admin
from helmholtz.location.models import Position, SpatialConfiguration

location_admin = admin.site

location_admin.register(Position)
location_admin.register(SpatialConfiguration)
