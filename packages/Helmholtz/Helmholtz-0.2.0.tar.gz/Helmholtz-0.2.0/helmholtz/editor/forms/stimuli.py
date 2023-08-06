#encoding:utf-8
from django import forms
from helmholtz.stimulation.models import Stimulus
from catdb.vision.models.stimuli import RevCor, Mulstistim, MovingBar, FlashBar

class StimulusForm(forms.ModelForm):
    class Meta :
        model = Stimulus

class RevCorForm(forms.ModelForm):
    class Meta :
        model = RevCor

class MultistimForm(forms.ModelForm):
    class Meta :
        model = Multistim

class MovingBarForm(forms.ModelForm):
    
    class Meta :
        model = MovingBar

class FlashBarForm(forms.ModelForm):

    class Meta :
        model = FlashBar
