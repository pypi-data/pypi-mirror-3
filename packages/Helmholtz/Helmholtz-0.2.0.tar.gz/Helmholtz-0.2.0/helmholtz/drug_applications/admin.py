#encoding:utf-8
from django.contrib import admin
from helmholtz.drug_applications.models import DiscreteDrugApplication, ContinuousDrugApplication

drug_applications_admin = admin.site

drug_applications_admin.register(ContinuousDrugApplication)
drug_applications_admin.register(DiscreteDrugApplication)
