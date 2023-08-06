#encoding:utf-8
from copy import deepcopy
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.db.models import Count
from django.views.generic.list_detail import object_list
from helmholtz.core.decorators import memorise_last_page, memorise_last_rendered_page
from helmholtz.experiment.models import Experiment
from helmholtz.people.models import ScientificStructure

@memorise_last_page
@memorise_last_rendered_page
def experiment_list(request, lab, *args, **kwargs):
    laboratory = ScientificStructure.objects.get(diminutive=lab)
    
    # TODO: include in experiment_list.html a form to filter experiment
    
    # date_form = DateFilter(prefix="date_filter")
    # preparation_form = PreparationFilter(prefix="preparation_filter")
    # protocol_form = ProtocolFilter(prefix="protocol_filter", experiments=laboratory.experiments)
    
    kw = deepcopy(kwargs)
    kw['queryset'] = laboratory.experiments.annotate(
        n_blocks=Count("recordingblock", distinct=True),
        n_protocols=Count("recordingblock__protocolrecording", distinct=True),
        n_researchers=Count("researchers", distinct=True),
        n_files=Count("recordingblock__protocolrecording__file", distinct=True),
        n_signals=Count("recordingblock__protocolrecording__file__signal", distinct=True),
        n_preparations=Count("preparation", distinct=True),
        n_animals=Count("preparation__animal", distinct=True)
    )
    
    context = {
        'lab':laboratory,
        'user':request.user,
        # 'date_form':date_form,
        # 'protocol_form':protocol_form,
        # 'preparation_form':preparation_form
    }
    kw['extra_context'].update(context)
    return object_list(request, *args, **kw) 

@memorise_last_page
@memorise_last_rendered_page
def experiment_detail(request, lab, expt, *args, **kwargs):
    laboratory = ScientificStructure.objects.get(diminutive=lab) 
    experiment = Experiment.objects.get(label=expt)
    context = {'experiment':experiment,
               'lab':laboratory,
               'user':request.user,
    }
    return render_to_response(kwargs['template'], RequestContext(request, context))
