#encoding:utf-8
from django import forms
from django.forms.extras import SelectDateWidget
from django.contrib.contenttypes.models import ContentType
from helmholtz.stimulation.models import Stimulus
from helmholtz.equipment.models import DeviceConfiguration, Setup
from helmholtz.species.models import Strain
from helmholtz.preparations.models import Preparation
from helmholtz.stimulation.models import Stimulus
from helmholtz.recording.models import RecordingBlock, RecordingConfiguration

time_units = (
    ('H', 'hours'),
    ('D', 'days'),
    ('W', 'weeks'),
    ('M', 'months'),
    ('Y', 'years'),
)

class StimModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return dct['name']

class ConfigModelMultipleChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.model_class().method

class DateFilter(forms.Form):
    date_from = forms.DateField(required=False)
    date_to = forms.DateField(required=False)

choices = (
    ('M', 'male'),
    ('F', 'female'),
    ('B', 'both')
)

prep_cls = [k for k in Preparation.__subclasses__()]
prep_models = [k.__name__.lower() for k in prep_cls]
prep_apps = [k._meta.app_label for k in prep_cls]

class PreparationFilter(forms.Form):
    type = forms.ModelChoiceField(required=False, queryset=ContentType.objects.filter(app_label__in=prep_apps, model__in=prep_models))
    strain = forms.ModelChoiceField(required=False, queryset=Strain.objects.all())
    sex = forms.ChoiceField(required=False, choices=choices)
    age_from = forms.IntegerField(required=False)
    age_to = forms.IntegerField(required=False)    

stim_cls = [k for k in Stimulus.get_subclasses_recursively()]
stim_models = [k.__name__.lower() for k in stim_cls]
stim_apps = [k._meta.app_label for k in stim_cls]

conf_cls = [k for k in DeviceConfiguration.get_subclasses_recursively() if hasattr(k, 'method')]
conf_models = [k.__name__.lower() for k in conf_cls]
conf_apps = [k._meta.app_label for k in conf_cls]

class ProtocolFilter(forms.Form):
    #stim_protocol = forms.ModelChoiceField(label="protocol", required=False, queryset=ContentType.objects.filter(app_label__in=stim_apps, model__in=stim_models))
    #config_types = ConfigModelMultipleChoiceField(label="methods", required=False, queryset=ContentType.objects.filter(app_label__in=conf_apps, model__in=conf_models))

    def __init__(self, *args, **kwargs):
        experiments = kwargs.pop('experiments')
        #get only setup, stimulation and configuration types
        #that are actually used by a set of experiments
        q1 = Setup.objects.filter(experiment__in=experiments).distinct()
        if q1 :
            if len(q1) > 1 :
                self.base_fields['setup'] = forms.ModelMultipleChoiceField(queryset=q1, required=False)
            else :
                self.base_fields['setup'] = forms.ModelChoiceField(queryset=q1, required=False)
        
        #get only stimulus types that are 
        #actually used by a set of experiments
        stimuli = Stimulus.objects.filter(protocolrecording__block__experiment__in=experiments)#pk__in=dev_conf_ids)
        stim_ids = list()
        stim_cls = [k for k in Stimulus.get_subclasses_recursively() if hasattr(k, 'method')]
        for cls in stim_cls :
            if stimuli.cast(cls) :
                stim_ids.append(ContentType.objects.get_for_model(cls).pk)
        #create the field if there is one stimulus type  at least
        stim_qset = ContentType.objects.filter(pk__in=stim_ids)
        if stim_qset :
            self.base_fields['protocol'] = ConfigModelMultipleChoiceField(required=False, queryset=stim_qset)
        
        #get all device configurations related to provided experiments
        #dev_conf_ids = [k.configuration.pk for k in RecordingConfiguration.objects.filter(block__in=blocks).distinct()]
        dev_conf = DeviceConfiguration.objects.filter(recordingconfiguration__block__experiment__in=experiments)#pk__in=dev_conf_ids)
        conf_ids = list()
        dev_conf_cls = [k for k in DeviceConfiguration.get_subclasses_recursively() if hasattr(k, 'method')]
        for cls in dev_conf_cls :
            if dev_conf.cast(cls) :
                conf_ids.append(ContentType.objects.get_for_model(cls).pk)
        #create the field if there is one configuration type  at least
        conf_qset = ContentType.objects.filter(pk__in=conf_ids)
        if conf_qset :
            self.base_fields['protocol'] = ConfigModelMultipleChoiceField(required=False, queryset=conf_qset)
        
        super(ProtocolFilter, self).__init__(*args, **kwargs)
