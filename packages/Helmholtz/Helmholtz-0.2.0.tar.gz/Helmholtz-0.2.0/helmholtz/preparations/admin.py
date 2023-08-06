#encoding:utf-8
from django.contrib import admin
from helmholtz.preparations.models import Animal, InVivoPreparation, InVitroCulture, InSilico, InVitroSlice

class PreparationAdmin(admin.ModelAdmin):
    list_display = ['id', 'animal', 'protocol']

preparations_admin = admin.site

preparations_admin.register(Animal)
preparations_admin.register(InVivoPreparation, PreparationAdmin)
preparations_admin.register(InVitroCulture, PreparationAdmin)
preparations_admin.register(InSilico, PreparationAdmin)
preparations_admin.register(InVitroSlice, PreparationAdmin)
