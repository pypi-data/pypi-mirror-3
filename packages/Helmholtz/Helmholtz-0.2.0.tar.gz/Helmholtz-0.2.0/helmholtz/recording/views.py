#encoding:utf-8
from django.utils.datastructures import SortedDict
from django.template import RequestContext
from django.shortcuts import render_to_response
from helmholtz.core.decorators import memorise_last_page, memorise_last_rendered_page
from helmholtz.access_control.models import User
from helmholtz.access_request.models import AccessRequest
from helmholtz.experiment.models import Experiment
from helmholtz.recording.tools.filters import get_available_methods, get_available_protocols
from helmholtz.recording.models import RecordingBlock, ProtocolRecording
from helmholtz.people.models import ScientificStructure
from helmholtz.storage.models import File
from helmholtz.signals.models import Signal
from helmholtz.analysis.models import Analysis
from helmholtz.elphy.reader import ElphyFile
from helmholtz.elphy.objects import Signal as ElphySignal, Tag as ElphyTag

@memorise_last_page
@memorise_last_rendered_page
def block_detail(request, lab, expt, block, *args, **kwargs):
    laboratory = ScientificStructure.objects.get(diminutive=lab)
    experiment = Experiment.objects.get(label=expt)
    blk = RecordingBlock.objects.get(experiment=experiment, label=block)
    protocols = blk.get_protocols_by_type()
    context = {
        'experiment':experiment,
        'lab':laboratory,
        'blk':blk,
        'protocols':protocols,
        'user':request.user
    }
    return render_to_response(kwargs["template"], RequestContext(request, context))

@memorise_last_page
@memorise_last_rendered_page
def protocol_detail(request, lab, expt, block, protocol, *args, **kwargs):
    laboratory = ScientificStructure.objects.get(diminutive=lab)
    protocol = ProtocolRecording.objects.get(label=protocol, block__label=block, block__experiment__label=expt)
    
    context = {
        'lab':laboratory,
        'protocol':protocol,
        'user':request.user,
    }
    
    return render_to_response(kwargs["template"], RequestContext(request, context))

@memorise_last_page
@memorise_last_rendered_page
def signal_detail(request, lab, expt, block, protocol, file, episode, channel, type_name, *args, **kwargs):
    laboratory = ScientificStructure.objects.get(diminutive=lab)
    file = File.objects.get(name=file)
    
    signal = file.signal_set.get(
        episode=int(episode),
        recording_channel__electricalrecordingchannel__channel__number=int(channel),
        recording_channel__electricalrecordingchannel__channel__type__name=type_name
    )
    channel = signal.recording_channel.electricalrecordingchannel.channel
    context = {
        'lab':laboratory,
        'signal':signal,
        'user':request.user
    }
    
    try :
        elphy_file = ElphyFile(file.hdd_path)
        elphy_file.open()
        signals = elphy_file.get_signals()
        signals.extend(elphy_file.get_tags())
        
        def test(k):
            return (k.episode == signal.episode) and (k.channel == channel.number) and not isinstance(k, ElphyTag)
        
        signals = [k for k in signals if test(k)]
    except:
        signals = None
    
    if signals :
        
        sig_data = signals[0].data
    
        context['duration'] = sig_data['x'].max() - sig_data['x'].min()
        context["min"] = sig_data['y'].min()
        context["max"] = sig_data['y'].max()
        context["mean"] = sig_data['y'].mean()
        context["p2p"] = abs(sig_data['y'].max() - sig_data['y'].min())
        context["amplitude"] = abs(sig_data['y'].max() - sig_data['y'].min()) / 2.0
        context["std"] = sig_data['y'].std()
        context["rms"] = ((1.0 / 2) * (sig_data['y'] ** 2).sum())**(1.0 / 2)
        context["var"] = sig_data['y'].var()
        
        elphy_file.close()

    return render_to_response(kwargs["template"], RequestContext(request, context))
