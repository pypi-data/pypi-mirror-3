#encoding:utf-8
from django.contrib import admin
from helmholtz.species.models import Species, Strain

species_admin = admin.site

species_admin.register(Species)
species_admin.register(Strain)
