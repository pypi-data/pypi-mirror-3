#encoding:utf-8
from django import template
from helmholtz.access_control.models import User
from helmholtz.trackers.models import Message
from helmholtz.people.models import EMail, Phone, Fax, WebSite, Address

register = template.Library()

def get_base_context(context, user) :
    try :
        profile = user.get_profile()
    except :
        profile = None
    request_user = context['user']
    can_modify = (user.pk == request_user.pk) or request_user.is_superuser
    return {
        'MEDIA_URL':context['MEDIA_URL'],
        'can_modify':can_modify,
        'user': request_user,
        'disp_user':user,
        'profile':profile,
        'selection':context['selection'],
    }

def get_last_position_context(researcher, structure):
    context = dict()
    position = researcher.last_position(structure)
    if position :
        main_structure, sub_structure = position.structure.get_main_and_sub_structures()   
    else :
        main_structure = None
        sub_structure = None
    context['position'] = position
    context['since'] = not position or not position.end
    context['main_structure'] = main_structure
    context['sub_structure'] = sub_structure
    return context

@register.inclusion_tag('user_photo.html', takes_context=True)
def user_photo(context, user):
    return get_base_context(context, user)

@register.inclusion_tag('profile_menu.html', takes_context=True)
def profile_menu(context, user):
    return get_base_context(context, user)

@register.inclusion_tag('user_abstract.html', takes_context=True)
def user_abstract(context, user):
    return get_base_context(context, user)

@register.inclusion_tag('last_known_position.html', takes_context=True)
def last_known_position(context, researcher, structure=None):
    _context = dict()
    _context['MEDIA_URL'] = context['MEDIA_URL']
    _context.update(get_last_position_context(researcher, structure))
    return _context

@register.inclusion_tag('user_actions.html', takes_context=True)
def user_actions(context, user):
    return get_base_context(context, user)

@register.inclusion_tag('account_section.html', takes_context=True)
def account_section(context, user):
    return get_base_context(context, user)

@register.inclusion_tag('profile_section.html', takes_context=True)
def profile_section(context, user):
    return get_base_context(context, user)

@register.inclusion_tag('description_section.html', takes_context=True)
def description_section(context, user):
    return get_base_context(context, user)

@register.inclusion_tag('user_positions.html', takes_context=True)
def user_positions(context, user):
    return get_base_context(context, user)

@register.inclusion_tag('position_section.html', takes_context=True)
def position_section(context, user):
    _context = get_base_context(context, user)
    profile = _context['profile']
    _context['positions'] = profile.position_set.order_by('-start') if profile else None
    return _context

@register.inclusion_tag('position_template.html', takes_context=True)
def position_template(context, position):
    _context = get_base_context(context, context['disp_user'])
    if position :
        main_structure, sub_structure = position.structure.get_main_and_sub_structures()   
    else :
        main_structure = None
        sub_structure = None
    _context['main_structure'] = main_structure
    _context['sub_structure'] = sub_structure
    _context['position'] = position
    return _context

@register.inclusion_tag('list_of_contacts.html', takes_context=True)
def list_of_contacts(context, user):
    _context = get_base_context(context, user)
    request_user = _context['user']
    profile = _context['profile']
    if profile :
        #contacts visible by the request user
        proxy_user = User.objects.get(pk=request_user.id)
        queryset = profile.contacts.all()
        _context['emails'] = proxy_user.get_accessible(queryset.cast(EMail))
        _context['phones'] = proxy_user.get_accessible(queryset.cast(Phone))
        _context['faxes'] = proxy_user.get_accessible(queryset.cast(Fax))
        _context['websites'] = proxy_user.get_accessible(queryset.cast(WebSite))
        _context['addresses'] = proxy_user.get_accessible(queryset.cast(Address))
        _context['can_see_contacts'] = bool(_context['emails'] or _context['phones'] or _context['faxes'] or _context['websites'] or _context['addresses'])
    return _context

@register.inclusion_tag('change_access_control.html', takes_context=True)
def change_access_control(context, researcher_id, app_label, model, id):
    return {
        'MEDIA_URL':context['MEDIA_URL'],
        'researcher_id':researcher_id,
        'app_label':app_label,
        'model':model,
        'id':id
    }
    
@register.inclusion_tag('user_collaborators.html', takes_context=True)
def user_collaborators(context, user):
    _context = get_base_context(context, user)
    _context['collaborators'] = User.objects.filter(groups__pk__in=[k.pk for k in user.groups.all()]).exclude(pk=user.pk).order_by('last_name').distinct()
    _context['groups'] = user.groups.all()
    return _context

@register.inclusion_tag('group_section.html', takes_context=True)
def group_section(context, group):
    _context = get_base_context(context, context['disp_user'])
    try :
        structure = group.scientificstructure
    except : 
        structure = None
    main_structure = structure.get_root() if structure else None
    _context['main_structure'] = main_structure
    _context['sub_structure'] = structure if structure and (main_structure != structure) else None
    _context['group'] = group
    _context['display_main_structure'] = not bool(structure)
    return _context

@register.inclusion_tag('user_etiquette.html', takes_context=True)
def user_etiquette(context, user, group, display_main_structure=True):
    _context = get_base_context(context, user)
    profile = _context['profile']
    try :
        structure = group.scientificstructure
    except : 
        structure = None
    if profile :
        if structure :
            position = profile.position_set.filter(structure=structure).latest('start') if structure else None 
        else :
            position = profile.last_position()
        _context['main_structure'], _context['sub_structure'] = position.structure.get_main_and_sub_structures()
        _context['position'] = position
        _context['since'] = not position or not position.end
    _context['structure'] = structure
    _context['display_main_structure'] = display_main_structure
    return _context

@register.inclusion_tag('messages_statistics.html', takes_context=True)
def messages_statistics(context, user):
    _context = get_base_context(context, user)
    _context['received'] = user.mails_as_recipient.count()
    _context['sent'] = user.mails_as_sender.count()
    _context['total'] = Message.objects.filter(sender=user, recipients__isnull=False).count()
    return _context

@register.inclusion_tag('connections_statistics.html', takes_context=True)
def connections_statistics(context, user):
    _context = get_base_context(context, user)
    _context['connection_histogram'] = "connection_chart_of_user_%s.svg" % user.pk
    return _context

@register.inclusion_tag('positions_statistics.html', takes_context=True)
def positions_statistics(context, user):
    _context = get_base_context(context, user)
    proxy_user = User.objects.get(pk=user.pk)
    _context['collaborators'] = proxy_user.get_collaborators().count()
    profile = _context['profile']
    if profile :
        _context['positions'] = profile.position_set.count()
        _context['structures'] = profile.number_of_structures()
    return _context

from django.db.models import Q
from helmholtz.access_request.models import AccessRequest

@register.inclusion_tag('received_requests_statistics.html', takes_context=True)
def received_requests_statistics(context, user):
    _context = get_base_context(context, user)
    q1 = Q(index__object_permissions__userpermission__user=user)
    q2 = Q(index__object_permissions__grouppermission__group__in=user.groups.all())
    objects = AccessRequest.objects.filter(q1 | q2)
    _context['total'] = objects.count()
    _context['pending'] = objects.filter(state="requested").count()
    _context['confirmed'] = objects.filter(state="accepted").count()
    _context['refused'] = objects.filter(state="refused").count()
    return _context

@register.inclusion_tag('sent_requests_statistics.html', takes_context=True)
def sent_requests_statistics(context, user):
    _context = get_base_context(context, user)
    requests = user.requests.all()
    _context['pending'] = requests.filter(state="requested").count()
    _context['confirmed'] = requests.filter(state="accepted").count()
    _context['refused'] = requests.filter(state="refused").count()
    _context['total'] = requests.count()
    return _context

@register.inclusion_tag('other_activities_statistics.html', takes_context=True)
def other_activities_statistics(context, user):
    return get_base_context(context, user)

@register.inclusion_tag('request_etiquette.html', takes_context=True)
def request_etiquette(context, request):
    return get_base_context(context, context['disp_user'])

@register.inclusion_tag('sent_messages.html', takes_context=True)
def sent_messages(context, user):
    _context = get_base_context(context, user)
    _context['messages'] = user.mails_as_sender.all()
    _context['sent'] = True
    return _context

@register.inclusion_tag('received_messages.html', takes_context=True)
def received_messages(context, user):
    _context = get_base_context(context, user)
    _context['messages'] = user.mails_as_recipient.all()
    _context['sent'] = False
    return _context

@register.inclusion_tag('messages_section.html', takes_context=True)
def messages_section(context, messages):
    _context = get_base_context(context, context['disp_user'])
    _context['messages'] = messages
    _context['sent'] = context['sent']
    return _context

@register.inclusion_tag('message_etiquette.html', takes_context=True)
def message_etiquette(context, message):
    _context = get_base_context(context, context['disp_user'])
    _context['message'] = message
    _context['sent'] = context['sent']
    try :
        _context['collaborator'] = message.recipients.get()
    except :
        _context['collaborators'] = message.recipients.all()
    return _context

@register.inclusion_tag('sent_requests.html', takes_context=True)
def sent_requests(context, user):
    return get_base_context(context, user)

@register.inclusion_tag('received_requests.html', takes_context=True)
def received_requests(context, user):
    return get_base_context(context, user)

@register.inclusion_tag('structure_profile.html', takes_context=True)
def structure_profile(context, structure, abstract=False, display_researchers=False, display_hierarchy=False):
    _context = dict()
    _context['MEDIA_URL'] = context['MEDIA_URL']
    _context['user'] = context['user']
    if display_hierarchy :
        root = structure.get_root()
        _context['structure'] = root
        _context['teams'] = root.get_children(True, True)
    else :
        _context['structure'] = structure
        _context['teams'] = structure.scientificstructure_set.all()
        _context['parent'] = structure.parent
    _context['abstract'] = abstract
    _context['display_researchers'] = display_researchers
    _context['display_hierarchy'] = display_hierarchy 
    _context['selection'] = context.get('selection', structure)
    return _context

@register.inclusion_tag('structure_abstract.html', takes_context=True)
def structure_abstract(context, structure):
    _context = dict()
    _context['MEDIA_URL'] = context['MEDIA_URL']
    _context['user'] = context['user']
    _context['structure'] = structure
    _context['manager'] = structure.manager
    return _context

@register.inclusion_tag('structure_description.html', takes_context=True)
def structure_description(context, structure):
    _context = dict()
    _context['MEDIA_URL'] = context['MEDIA_URL']
    _context['user'] = context['user']
    _context['structure'] = structure
    return _context

@register.inclusion_tag('structure_logo.html', takes_context=True)
def structure_logo(context, structure):
    _context = dict()
    _context['MEDIA_URL'] = context['MEDIA_URL']
    _context['structure'] = structure
    _context['selected'] = (structure == context.get('selection', None))
    return _context

@register.inclusion_tag('portrait_grid.html', takes_context=True)
def portrait_grid(context, structure):
    _context = dict()
    _context['structure'] = structure
    _context['MEDIA_URL'] = context['MEDIA_URL']
    return _context

@register.inclusion_tag('researcher_etiquette.html', takes_context=True)
def researcher_etiquette(context, researcher, structure=None):
    _context = dict()
    _context['disp_user'] = researcher.user
    _context['MEDIA_URL'] = context['MEDIA_URL']
    _context['researcher'] = researcher
    _context.update(get_last_position_context(researcher, structure))
    return _context

@register.inclusion_tag('affectation_etiquette.html', takes_context=True)
def affectation_etiquette(context, structure):
    _context = dict()
    _context['structure'] = structure
    _context['manager'] = structure.manager
    _context['MEDIA_URL'] = context['MEDIA_URL']
    return _context

@register.inclusion_tag('structure_manager.html', takes_context=True)
def structure_manager(context, structure):
    _context = dict()
    _context['MEDIA_URL'] = context['MEDIA_URL']
    _context['manager'] = structure.manager
    _context['structure'] = structure
    return _context

@register.inclusion_tag('structure_teams.html', takes_context=True)
def structure_teams(context, structure):
    _context = dict()
    _context['structure'] = structure
    _context['teams'] = structure.get_children(True, True)
    _context['MEDIA_URL'] = context['MEDIA_URL']
    return _context
