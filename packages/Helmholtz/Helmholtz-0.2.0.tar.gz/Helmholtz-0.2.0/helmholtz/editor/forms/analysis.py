#encoding:utf-8
from django import forms
from helmholtz.analysis.models import PinType, AnalysisType, Pin, Analysis

class AnalysisTypeForm(forms.ModelForm):
    class Meta :
        model = AnalysisType
        exclude = ['inputs', 'outputs', 'parameters']

class PinTypeFromAnalysisForm(forms.ModelForm):
    class Meta :
        model = PinType
        exclude = ['analysis_type']

class PinTypeForm(forms.ModelForm):
    class Meta :
        model = PinType

class AnalysisForm(forms.ModelForm):
    class Meta :
        model = Analysis
        exclude = ['analysis_type']

