#encoding:utf-8
from django import forms
from helmholtz.drug_applications.models import ContinuousDrugApplication, DiscreteDrugApplication

class ContinuousDrugApplicationForm(forms.ModelForm):
    class Meta :
        model = ContinuousDrugApplication
        exclude = ['experiment']

class DiscreteDrugApplicationForm(forms.ModelForm):
    class Meta :
        model = DiscreteDrugApplication
        exclude = ['experiment']
