#encoding:utf-8
from django.contrib import admin
from helmholtz.units.models import BaseUnit, DerivedUnit

units_admin = admin.site

units_admin.register(BaseUnit)
units_admin.register(DerivedUnit)
