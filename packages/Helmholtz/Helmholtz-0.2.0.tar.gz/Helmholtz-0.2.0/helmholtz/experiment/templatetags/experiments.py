#encoding:utf-8
from django import template
from django.db.models import Count
from helmholtz.core.schema import get_subclasses_recursively  
from helmholtz.species.models import Species
from helmholtz.preparations.models import Preparation, Animal
from helmholtz.experiment.models import Experiment
from helmholtz.recording.models import ProtocolRecording
from helmholtz.stimulation.models import StimulationType
from helmholtz.equipment.models import DeviceConfiguration

register = template.Library()

@register.inclusion_tag('experiments_history.html', takes_context=True)
def experiment_list(context, object_list, lab):
    _context = dict()
    _context.update({
        'object_list':context['object_list'],
        'lab':lab,
        'MEDIA_URL':context['MEDIA_URL'],
        'is_paginated':context['is_paginated'],
        'page_range':context['page_range'],
        'page':context['page']
    })
    return  _context

# having_male_animals = qset.filter(preparation__animal__sex='M').annotate(n_animals=Count("preparation__animal", distinct=True)) 

@register.inclusion_tag('experiments_statistics.html', takes_context=True)
def experiments_statistics(context):
    _context = dict()
    _context.update({
        'MEDIA_URL':context['MEDIA_URL'],
    })
      
    # count stimulation types
    stim_types = StimulationType.objects.filter(protocolrecording__isnull=False).annotate(
        n_experiments=Count("protocolrecording__block__experiment", distinct=True),
        # n_blocks=Count("protocolrecording__block", distinct=True),
        # n_protocols=Count("protocolrecording", distinct=True)
    ).values('name', 'n_experiments')
    _context['n_stim_types'] = len(stim_types)
    _context['stim_types'] = stim_types
    
    qset = Experiment.objects.all()
    _context['n_experiments'] = len(qset)
    experiments = qset.aggregate(
        n_experiments=Count("id", distinct=True),
        n_blocks=Count("recordingblock", distinct=True),
        n_protocols=Count("recordingblock__protocolrecording", distinct=True),
        n_researchers=Count("researchers", distinct=True),
        n_files=Count("recordingblock__protocolrecording__file", distinct=True),
        n_signals=Count("recordingblock__protocolrecording__file__signal", distinct=True),
        n_preparations=Count("preparation", distinct=True),
        n_animals=Count("preparation__animal", distinct=True),
        n_invivo=Count("preparation__invivopreparation__id", distinct=True),
        n_invitro_slices=Count("preparation__invitroslice__id", distinct=True),
        n_invitro_cultures=Count("preparation__invitroculture__id", distinct=True),
    )
    _context.update(experiments)
    
    # count male animals
    # n_male_animals = qset.filter(preparation__animal__sex='M').count()
    # _context['n_male_animals'] = n_male_animals
    
    # count female animals
    # n_female_animals = qset.filter(preparation__animal__sex='F').count()
    # _context['n_female_animals'] = n_female_animals
    
    # count species
    species = Species.objects.filter(strain__animal__isnull=False).annotate(
        n_animals=Count("strain__animal")
    ).values('english_name', 'url', 'n_animals')
    _context['species'] = species
   
    # count preparation types
    prep_types = dict()
    subclasses = Preparation.__subclasses__()
    for subclass in subclasses :
        count = subclass.objects.count()
        if count :
            prep_types[subclass._meta.verbose_name] = count
    _context['prep_types'] = prep_types
    
    # define acquisition method, i.e. sharp or patch
    methods = dict()
    subclasses = get_subclasses_recursively(DeviceConfiguration, strict=True)
    for subclass in subclasses :
        if hasattr(subclass, 'method'):
            count = subclass.objects.filter(recordingconfiguration__block__experiment__id__isnull=False).count()
            if count :
                methods[subclass.method] = count
    _context['methods'] = methods
    _context['n_methods'] = len(methods)
    return _context

@register.inclusion_tag('experiment_statistics.html', takes_context=True)
def experiment_statistics(context, experiment):
    _context = dict()

    # count stimulation types
    stim_types = StimulationType.objects.filter(protocolrecording__block__experiment=experiment).annotate(
        n_experiments=Count("protocolrecording__block__experiment", distinct=True),
    ).values('name', 'n_experiments')
    _context['n_stim_types'] = len(stim_types)
    _context['stim_types'] = stim_types
    
    # count methods
    methods = dict()
    subclasses = get_subclasses_recursively(DeviceConfiguration, strict=True)
    for subclass in subclasses :
        if hasattr(subclass, 'method'):
            count = subclass.objects.filter(recordingconfiguration__block__experiment=experiment).count()
            if count :
                methods[subclass.method] = count

    _context.update({
        'MEDIA_URL':context['MEDIA_URL'],
        'experiment':experiment,
        'n_blocks':experiment.recordingblock_set.count(),
        'n_protocols':experiment.protocols.count(),
        'methods':methods,
        'n_methods':len(methods)
        
    })
    return _context

@register.inclusion_tag('experiment_perfusions.html', takes_context=True)
def experiment_perfusions(context, perfusions):
    _context = dict()
    _context.update({
        'MEDIA_URL':context['MEDIA_URL'],
        'perfusions':perfusions
    })
    return _context

@register.inclusion_tag('experiment_injections.html', takes_context=True)
def experiment_injections(context, injections):
    _context = dict()
    _context.update({
        'MEDIA_URL':context['MEDIA_URL'],
        'injections':injections
    })
    return _context
