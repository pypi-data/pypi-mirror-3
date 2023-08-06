#encoding:utf-8
from django.contrib import admin
from helmholtz.reconstruction.models import Reconstruction

reconstruction_admin = admin.site

reconstruction_admin.register(Reconstruction)
