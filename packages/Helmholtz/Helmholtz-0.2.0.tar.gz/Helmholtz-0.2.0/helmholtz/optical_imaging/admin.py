#encoding:utf-8
from django.contrib import admin
from helmholtz.optical_imaging.models import ExposedArea, CameraConfiguration, VSDOptical, IntrinsicOptical

optical_imaging_admin = admin.site
optical_imaging_admin.register(ExposedArea)
optical_imaging_admin.register(CameraConfiguration)
optical_imaging_admin.register(VSDOptical)
optical_imaging_admin.register(IntrinsicOptical)
