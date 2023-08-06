#encoding:utf-8
from django.contrib import admin
from helmholtz.cells.models import RecordedCell, StainedCell

cells_admin = admin.site

cells_admin.register(RecordedCell)
cells_admin.register(StainedCell)
