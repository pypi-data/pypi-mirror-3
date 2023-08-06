#encoding:utf-8
from django.contrib import admin
from helmholtz.neuralstructures.models import BrainRegion, CellType, Cell

neuralstructures_admin = admin.site

neuralstructures_admin.register(BrainRegion)
neuralstructures_admin.register(CellType)
neuralstructures_admin.register(Cell)
