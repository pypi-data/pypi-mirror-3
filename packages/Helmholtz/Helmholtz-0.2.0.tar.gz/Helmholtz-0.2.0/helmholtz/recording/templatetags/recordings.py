#encoding:utf-8
import os
from copy import copy
from django.conf import settings
from django import template
from django.db.models import Count
from helmholtz.core.schema import get_subclasses_recursively
from helmholtz.access_control.models import User
from helmholtz.annotation.models import Annotation, Attachment, Tag
from helmholtz.equipment.models import DeviceConfiguration
from helmholtz.stimulation.models import StimulationType
from helmholtz.elphy.reader import ElphyFile
from helmholtz.elphy.objects import Signal as ElphySignal, Tag as ElphyTag

register = template.Library()

@register.inclusion_tag('block_list.html', takes_context=True)
def block_list(context, lab, blocks):
    _context = dict()
    _context.update({
        'lab':lab,
        'blocks':blocks,
        'MEDIA_URL':context['MEDIA_URL'],
    })
    return _context

@register.inclusion_tag('block_statistics.html', takes_context=True)
def block_statistics(context, block):
    _context = dict()
    protocols = block.protocolrecording_set.all()
    _context['n_protocols'] = len(protocols)
    _context['n_files'] = block.files.count()
    _context['n_signals'] = block.signals.count() 
    
    # count stimulation types
    stim_types = StimulationType.objects.filter(protocolrecording__block=block).annotate(
        n_experiments=Count("protocolrecording", distinct=True),
    ).values('name', 'n_experiments')
    _context['n_stim_types'] = len(stim_types)
    _context['stim_types'] = stim_types
    
    # count recording configurations and methods
    # methods are recording configurations having
    # a 'method' attribute
    methods = dict()
    rec_conf = dict()
    subclasses = get_subclasses_recursively(DeviceConfiguration, strict=True)
    for subclass in subclasses :
        count = subclass.objects.filter(recordingconfiguration__block=block).count()
        if count :
            rec_conf[subclass._meta.verbose_name] = count
            if hasattr(subclass, 'method'):
                methods[subclass.method] = count
            
    _context['n_methods'] = len(methods)
    _context['methods'] = methods
    _context['n_rec_conf'] = len(methods)
    _context['rec_conf'] = methods
    
    _context.update({
        'blk':block,
        'MEDIA_URL':context['MEDIA_URL'],
    })
    return _context

@register.inclusion_tag('protocol_list.html', takes_context=True)
def protocol_list(context, lab, protocol_types, protocols):
    _context = dict()
    _context.update({
        'prot_types':protocol_types,
        'all_protocols':protocols,
        'lab':lab,
        'user':context['user'],
        'MEDIA_URL':context['MEDIA_URL'],
    })
    return _context

@register.inclusion_tag('protocol_properties.html', takes_context=True)
def protocol_properties(context, protocol):
    _context = dict()
    _context.update({
        'lab':context['lab'],
        'protocol':protocol,
        'user':context['user'],
        'MEDIA_URL':context['MEDIA_URL'],
    })
    return _context

@register.inclusion_tag('stim_properties.html', takes_context=True)
def stim_properties(context, protocol):
    _context = dict()
    stim_type = protocol.stimulation_type.name
    _context.update({
        'stim_type':stim_type,
        'stimulus':protocol.stimulus.cast() if protocol.stimulus else protocol.stimulus,
        'annotations':Annotation.objects.annotations(protocol),
        'attachments':Attachment.objects.attachments(protocol),
        'MEDIA_URL':context['MEDIA_URL'],
    })
    return _context

@register.inclusion_tag('list_of_signals.html', takes_context=True)
def list_of_signals(context, protocol):
    _context = dict()
    user = context['user']
    proxy_user = User.objects.get(pk=user.pk)
    is_accessible = proxy_user.can_view(protocol.file)
    
    try :
        file = ElphyFile(protocol.file.hdd_path)
        file.open()
        all_signals = file.get_signals()
        all_signals.extend(file.get_tags())
    except:
        all_signals = None

    data = list()
    # TODO: convert tag and event channels
    type_ord = 'recording_channel__electricalrecordingchannel__channel__type__name'
    num_ord = 'recording_channel__electricalrecordingchannel__channel__number'
    for signal in protocol.file.signal_set.all().order_by('episode', type_ord, num_ord) :
        signals = copy(all_signals)
        dct = dict()
        dct['object'] = signal
        rec_channel = signal.recording_channel.electricalrecordingchannel
        pth = "%s/thumbnails/%s_ep%s_%s%s.png" % (settings.MEDIA_ROOT, signal.file.name.lower(), signal.episode, rec_channel.channel.type.abbr, rec_channel.channel.number)
        dct['thumbnail_exists'] = os.path.exists(pth)
        
        # compute simple analyses
        # TODO: use the new analyses
        # model to store them
        if signals :
            channel = rec_channel.channel
            signals = [k for k in signals if (k.episode == signal.episode) and (k.channel == channel.number)]
            abbr = channel.type.abbr
            if abbr == 'tag_ch' :
                signals = [k for k in signals if isinstance(k, ElphyTag)]
            else :
                signals = [k for k in signals if isinstance(k, ElphySignal)]
            
            if len(signals) == 1 :
            
                sig_data = signals[0].data
            
                dct['analyses'] = dict()
                dct['analyses']['duration'] = sig_data['x'].max() - sig_data['x'].min()
                dct['analyses']["min"] = sig_data['y'].min()
                dct['analyses']["max"] = sig_data['y'].max()
                dct['analyses']["mean"] = sig_data['y'].mean()
                dct['analyses']["p2p"] = abs(sig_data['y'].max() - sig_data['y'].min())
                dct['analyses']["amplitude"] = abs(sig_data['y'].max() - sig_data['y'].min()) / 2.0
                dct['analyses']["std"] = sig_data['y'].std()
                dct['analyses']["rms"] = ((1.0 / 2) * (sig_data['y'] ** 2).sum())**(1.0 / 2)
                dct['analyses']["var"] = sig_data['y'].var()

        data.append(dct)
    
    if all_signals :
        file.close()
    
    _context.update({
        'lab':context['lab'],
        'protocol':protocol,
        'is_accessible':is_accessible,
        'signals':data,
        'MEDIA_URL':context['MEDIA_URL'],
    })
    
    return _context

@register.inclusion_tag('sharp_configuration.html', takes_context=True)
def sharp_configuration(context, protocol):
    _context = dict()
    
    rec_conf = protocol.block.recordingconfiguration_set.filter(
        configuration__electrodeconfiguration__hollowelectrodeconfiguration__sharpelectrodeconfiguration__isnull=False
    ).cast('ElectrodeRecordingConfiguration').get()
    
    _context.update({
        'lab':context['lab'],
        'rec_conf':rec_conf,
        'config':rec_conf.configuration.cast(),
        'position':rec_conf.position,
        'block_measurements':rec_conf.measurements.all().order_by('parameter__label'),
        'protocol_measurements':protocol.measurements.all().order_by('parameter__label'),
        'MEDIA_URL':context['MEDIA_URL'],
    })
    return _context

@register.inclusion_tag('sharp_configuration.html', takes_context=True)
def sharp_configuration_block(context, block):
    _context = dict()
    
    rec_conf = block.recordingconfiguration_set.filter(
        configuration__electrodeconfiguration__hollowelectrodeconfiguration__sharpelectrodeconfiguration__isnull=False
    ).cast('ElectrodeRecordingConfiguration').get()
    
    _context.update({
        'lab':context['lab'],
        'rec_conf':rec_conf,
        'config':rec_conf.configuration.cast(),
        'position':rec_conf.position,
        'block_measurements':rec_conf.measurements.all().order_by('parameter__label'),
        # 'protocol_measurements':protocol.measurements.all().order_by('parameter__label'),
        'MEDIA_URL':context['MEDIA_URL'],
    })
    return _context
