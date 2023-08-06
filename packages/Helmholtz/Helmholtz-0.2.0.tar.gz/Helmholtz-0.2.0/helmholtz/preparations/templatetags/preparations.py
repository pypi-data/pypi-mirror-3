#encoding:utf-8
from django import template
from helmholtz.experiment.models import Experiment

register = template.Library()

@register.inclusion_tag('preparation_details.html', takes_context=True)
def preparation_details(context, preparation):
    _context = dict()
    all_ec = preparation.preparationinformation_set.cast('EyeCorrection')
    all_ac = preparation.preparationinformation_set.cast('AreaCentralis')
    _context.update({
        'MEDIA_URL':context['MEDIA_URL'],
        'preparation':preparation,
        'animal':preparation.animal,
        'all_eye_corrections':all_ec,
        'all_area_centralis':all_ac
    })
    return  _context

@register.inclusion_tag('preparation_observations.html', takes_context=True)
def preparation_observations(context, observations):
    _context = dict()
    _context.update({
        'MEDIA_URL':context['MEDIA_URL'],
        'observations':observations
    })
    return _context

@register.inclusion_tag('preparation_extra_details.html', takes_context=True)
def preparation_extra_details(context, preparation):
    _context = dict()
    perfusions = preparation.experiment_set.get().drugapplication_set.cast('ContinuousDrugApplication')
    injections = preparation.experiment_set.get().drugapplication_set.cast('DiscreteDrugApplication')
    _context.update({
        'MEDIA_URL':context['MEDIA_URL'],
        'preparation':preparation,
        'observations':preparation.cast().observations.all(),
        'perfusions':perfusions,
        'injections':injections
    })
    return  _context

@register.inclusion_tag('preparation_more_details.html', takes_context=True)
def preparation_more_details(context, preparation):
    _context = dict()
    experiment = preparation.experiment_set.get()
    ani_experiments = Experiment.objects.filter(preparation__animal=preparation.animal).exclude(pk=experiment.pk).distinct()
    prep_experiments = preparation.experiment_set.exclude(pk=experiment.pk)
    _context.update({
        'MEDIA_URL':context['MEDIA_URL'],
        'preparation':preparation,
        'animal':preparation.animal,
        'prep_experiments':prep_experiments,
        'ani_experiments':ani_experiments
    })
    return _context
