#encoding:utf-8
from django.contrib import admin
from helmholtz.histochemistry.models import HistoChemistryStep,BathStep,CuttingStep

histochemistry_admin = admin.site

histochemistry_admin.register(HistoChemistryStep)
histochemistry_admin.register(BathStep)
histochemistry_admin.register(CuttingStep)