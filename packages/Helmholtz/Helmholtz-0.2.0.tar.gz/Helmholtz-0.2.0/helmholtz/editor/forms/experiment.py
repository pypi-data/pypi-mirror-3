#encoding:utf-8
from django import forms
from helmholtz.experiment.models import Experiment

class ExperimentForm(forms.ModelForm):
    class Meta :
        model = Experiment
