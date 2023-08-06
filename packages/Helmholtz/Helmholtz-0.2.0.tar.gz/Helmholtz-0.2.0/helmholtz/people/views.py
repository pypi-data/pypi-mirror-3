#encoding:utf-8
from datetime import datetime
from django.db.models import Q
from django.conf import settings
from django.template import RequestContext
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from helmholtz.core.models import Cast
from helmholtz.core.shortcuts import cast_object_to_leaf_class
from helmholtz.core.schema import cast_queryset
from helmholtz.core.decorators import memorise_last_page, memorise_last_rendered_page, check_rendered_page
from helmholtz.access_control.models import User, Group, Permission, UnderAccessControlEntity, ObjectIndex
from helmholtz.people.models import Contact, Address, EMail, Fax, Phone, WebSite, Researcher, ScientificStructure, Position
from helmholtz.people.forms import CreatePositionForm, \
                                   ContactForm, \
                                   EMailForm, \
                                   WebSiteForm, \
                                   AddressForm, \
                                   FaxForm, \
                                   PhoneForm, \
                                   ChangePhotoForm, \
                                   ChangeDescriptionForm, \
                                   ChangeAccessControlForm, \
                                   ChangeEMailForm
from helmholtz.trackers.models import Message
from helmholtz.storage.models import File
from helmholtz.core.shortcuts import get_form_context

def render_to(template_name=None):
    """Decorator that do template rendering from a context."""
    def renderer(func):
        def wrapper(request, *args, **kwargs):
            output = func(request, *args, **kwargs)
            if isinstance(output, RequestContext) :
                context = output
            elif isinstance(output, dict) : 
                context = RequestContext(request, output)
            else :
                return output
            return render_to_response(template_name, context)
        return wrapper
    return renderer

def render(func):
    def wrapper(request, *args, **kwargs):
        output = func(request, *args, **kwargs)
        if isinstance(output, RequestContext) :
            context = output
        elif isinstance(output, dict) : 
            context = RequestContext(request, output)
        else :
            return output
        return render_to_response(kwargs['template'], context)
    return wrapper

@login_required
@memorise_last_page
@memorise_last_rendered_page
def lab_list(request, template):
    """Get all laboratories and teams registered in the database and organise them in a hierarchical manner.
    
    NB :
    
    To simplify the data structure, laboratories and teams are organised on two levels :
    
    - the roots level occupied by laboratories with parent = None
    - the children level occupied by teams with parent = laboratory
    
    """
    laboratories = ScientificStructure.objects.filter(parent__pk__isnull=True)
    context = {'labs':laboratories, 'user':request.user, 'current_page':request.session['last_page']}
    response = render_to_response(template, RequestContext(request, context))
    return response

def send_email(request, form, recipients):
    #ought to give some sort of feedback, and maybe return 
    #to wherever the user was before clicking 'contact'
    cform = form.cleaned_data
    username = "anonymous user" if request.user.is_anonymous() else request.user.username
    subject = "[%s]-[%s] %s" % (settings.PROJECT_NAME, username, cform['subject'])
    #send emails
    emails = [k.email for k in recipients]
    send_mail(subject, cform['message'], cform['sender'], emails, fail_silently=False)
    #finally store message in database
    if not request.user.is_anonymous() :
        message = Message.objects.create(sender=request.user, subject=cform['subject'], message=cform['message'])
        message.recipients.add(*recipients)

def _user(request, recipient_id):
    recipient = User.objects.get(pk=int(recipient_id))
    header = 'Contact %s' % (recipient.get_full_name())
    return [recipient], header

def _group(request, recipient_id):
    if not recipient_id :
        recipient = Group.objects.get(name='admin')
        header = 'Contact the database administrators'
    else :
        recipient = Group.objects.get(pk=int(recipient_id))
        if recipient.name == 'admin' :
            header = 'Contact the database administrators'
        else :
            header = 'Contact all member of group %s' % (recipient.name)
    return recipient.user_set.all(), header

def contact(request, func, **kwargs):
    recipients, header = func(request, kwargs.get('recipient_id', None))
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            send_email(request, form, recipients)
            return HttpResponseRedirect(request.session['last_page'])
    else:
        form = ContactForm(initial={'sender':getattr(request.user, 'email', None)})
    context = get_form_context(request, form, header)
    context.update(kwargs)
    return context

@render
def contact_admins(request, **kwargs):
    return contact(request, _group, **kwargs)

@render
def contact_user(request, **kwargs):
    return contact(request, _user, **kwargs)

@render
def contact_group(request, **kwargs):
    return contact(request, _group, **kwargs)

#@render
#def contact(request, receiver_id=None, group_id=None, **kwargs):
#    """
#    Display or process the contact form useful for users 
#    to ask information about catdb or helmholtz.
#    """
#    if receiver_id :
#        recipient = User.objects.get(pk=int(receiver_id))
#        header = 'Contact %s' % (recipient.get_full_name())
#    else :
#        if group_id :
#            recipient = Group.objects.get(pk=int(group_id))
#            if recipient.name == 'admin' :
#                header = 'Contact the database administrators'
#            else :
#                header = 'Contact all member of group %s' % (recipient.name)
#        else :
#            recipient = Group.objects.get(name='admin')
#            header = 'Contact the database administrators'
#    
#    recipients = [recipient]
#    
#    if request.method == 'POST':
#        form = ContactForm(request.POST)
#        if form.is_valid():
#            send_mail(request, form, recipients)
#            return HttpResponseRedirect(request.session['last_page'])
#    else:
#        form = ContactForm(initial={'sender':request.user.email})
#    context = get_form_context(request, form, header)
#    context.update(kwargs)
#    return context

    #return render_to_response(kwargs['template'], RequestContext(request, context))

def contact_owners(request, cto_id, **kwargs):
    cto = ObjectIndex.objects.get(pk=int(cto_id)).cast()
    header = "Contact owners of %s" % cto
    if request.method == 'POST' :
        pk_users = [k.user.pk for k in Permission.objects.get_user_permissions(cto.object)]
        groups = [k.group for k in Permission.objects.get_group_permissions(cto.object)]
        q1 = Q(pk__in=pk_users)
        q2 = Q(group__in=groups)
        users = User.objects.filter(q1 | q2)
        assert users, "this object hasn't got owners"
        form = ContactForm(request.POST)
        if form.is_valid():
            send_mail(request, form, users)
            return HttpResponseRedirect(request.session['last_page'])
    else :
        form = ContactForm(initial={'sender':request.user.email})
        
    context = get_form_context(request, form, header)
    context.update(kwargs)
    return render_to_response(kwargs['template'], RequestContext(request, context))

def common_contact(request, form_type, user, subclass, contact=None, **kwargs):
    global contact_map
    if request.method == 'POST':
        form = form_type(request.POST, instance=contact)
        if form.is_valid() :
            instance = form.save()
            #add the new instance to the users list of contacts
            #and the default permission for the user
            if not contact :
                _ct = ContentType.objects.get_for_model(instance.__class__)
                can_download = UnderAccessControlEntity.objects.get(entity=_ct).can_be_downloaded
                default_permission = {
                    'can_view':True,
                    'can_modify':True,
                    'can_delete':True,
                    'can_modify_permission':True,
                    'can_download':can_download
                }
                Permission.objects.create_user_permission(instance, user, **default_permission)
                profile, created = Researcher.objects.get_or_create(user=user, first_name=user.first_name, last_name=user.last_name)
                profile.contacts.add(instance)
            return HttpResponseRedirect(request.session['last_page'])
        else :
            form_header = 'Create a new %s' % subclass
    else:
        form = form_type(instance=contact)
        if contact :
            form_header = 'Update an existing %s' % subclass
        else :
            form_header = 'Create a new %s' % subclass
    context = get_form_context(request, form, form_header)
    context.update(kwargs)
    return render_to_response(kwargs['template'], RequestContext(request, context))

contact_map = {'email':EMailForm,
               'phone':PhoneForm,
               'fax':FaxForm,
               'website':WebSiteForm,
               'address':AddressForm
}

@login_required
def create_contact(request, subclass, user_id, **kwargs):
    """display or process the contact form."""
    global contact_map
    user = User.objects.get(pk=int(user_id))
    form_type = contact_map[subclass]
    return common_contact(request, form_type, user, subclass, **kwargs)

@login_required
def update_contact(request, user_id, contact_id, **kwargs):
    user = User.objects.get(pk=int(user_id))
    contact = cast_object_to_leaf_class(Contact.objects.get(pk=int(contact_id)))
    subclass = contact.__class__.__name__.lower()
    form_map = {'email':EMailForm,
                'phone':PhoneForm,
                'fax':FaxForm,
                'website':WebSiteForm,
                'address':AddressForm}
    form_type = form_map[subclass]
    return common_contact(request, form_type, user, subclass, contact, **kwargs)

@login_required
def delete_contact(request, user_id, contact_id):
    user = User.objects.get(pk=int(user_id))
    profile = user.get_profile()
    contact = profile.contacts.get(pk=int(contact_id))
    contact.delete()
    redirection = request.session['last_page']
    return HttpResponseRedirect(redirection)

def subtract_months(dt, m):
    years = m / 12
    months = m - 12 * years
    if dt.month <= months :
        years += 1
    year = dt.year - years
    month = (dt.month - months - 1) % 12 + 1
    return datetime(year, month, 1)#here day is fixed because just year and month is interesting

def get_user_context(request, user):
    dct = dict()
    request_user = request.user
    proxy_user = User.objects.get(pk=user.pk)
    
    try :
        profile = user.researcher
    except :
        profile = None
    
    #by weeks
    dct['now'] = datetime.now()
    dct['disp_user'] = user
    dct['can_modify'] = (user == request_user) or request_user.is_superuser
    dct['proxy_user'] = proxy_user
    dct['request_user'] = request_user
    dct['profile'] = profile
    dct['downloadables'] = proxy_user.get_downloadable(File.objects.all())
    return dct

def compute_histogram_data(user, reverse=True, ignore_void=False):
    """Compute data useful to draw the connection histogram."""
    by_months = list()
    connections = user.connections.all().order_by('-date')
    today = datetime.now()
    month_range = 6
    month_map = {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun', 7:'Jul', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'}
    last_date = today
    for m in range(0, month_range + 1) :
        new_date = subtract_months(today, m)
        if ignore_void and new_date < datetime(user.date_joined.year, user.date_joined.month, 1) : 
            break
        c_filtered = connections.filter(date__gte=new_date).filter(date__lt=last_date)
        data = {'quantity':c_filtered.count(), 'label':"%s %s" % (month_map[new_date.month], str(new_date.year)[2:])}
        by_months.append(data)
        last_date = new_date
    if reverse :
        by_months.reverse()
    return by_months

def generate_connections_histogram(user):
    """
    Generate an histogram displaying the number of
    connections done by a user for the 6 last months.
    """ 
    import matplotlib
    matplotlib.use('Agg')
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_agg import FigureCanvasAgg 
    
    #set up histogram data
    data = compute_histogram_data(user)
    values = [k['quantity'] for k in data]
    months = [k['label'] for k in data]
    positions = [k + 0.5 for k in xrange(len(months))]
    #set up the figure to draw on a canvas
    figure = Figure()
    figure.set_size_inches(1.5, 1.5)
    figure.subplots_adjust(left=0.3, bottom=0, right=0.99, top=0.99)
    subplot = figure.add_subplot(111)
    bars = subplot.barh(positions, values, height=0.6, align='center', linewidth=1.5, color='b')
    subplot.set_yticks(positions)
    subplot.set_yticklabels(tuple(months))
    subplot.set_ylim([0, max(positions) + 0.5])
    #subplot.set_xlabel('Connections')
    subplot.yaxis.set_ticks_position('none')
    for tick in subplot.yaxis.get_major_ticks():
        tick.set_visible(True)
        position = tick.label1.get_position()
        tick.label1.set_position((position[0] - 0.075, position[1]))
    for tick in subplot.yaxis.get_major_ticks():
        tick.label1.set_fontsize(6)
    ticklocs = subplot.xaxis.get_ticklocs()
    subplot.set_xlim([0, max(values) + 3 * (max(ticklocs) / len(ticklocs))])
    subplot.xaxis.set_visible(False)
    subplot.grid(False)
    
    #label each bar of the histogram
    def autolabel(rects):
        # attach some text labels
        for rect in [k for k in rects if k.get_width()]:
            height = rect.get_height()
            width = rect.get_width()
            pos_x = width + 0.5
            pos_y = rect.get_y() + height / 2.0
            subplot.text(pos_x, pos_y , '%d' % int(width), ha='left', va='center', color="black", fontsize=12, weight='bold', style='italic')
    autolabel(bars)
    
    #draw the histogram
    canvas = FigureCanvasAgg(figure)
    canvas.draw()
    
    #finally save histogram
    path = "%simages/charts/connection_chart_of_user_%s.svg" % (settings.DOCUMENT_ROOT, user.pk)
    figure.savefig(str(path))

@login_required
@memorise_last_page
@memorise_last_rendered_page
def show_profile(request, user_id, template):
    selection = request.GET.get('selection', 'profile')
    user = User.objects.get(pk=int(user_id))
    generate_connections_histogram(user)
    #first compute the user connections for each months
    context = get_user_context(request, user)
    #context['current_page'] = request.get_full_path()
    context['enable_scroll_position'] = True
    context['selection'] = selection
    return render_to_response(template, RequestContext(request, context))
#    if request.user.username == username:
#        user = get_object_or_404(User,username=username)
#        #files = DownloadStack.objects.filter(user=user)
##        have_access = files.filter(state="accepted")
##        access_requested = files.filter(state="requested")
##        access_denied = files.filter(state="rejected")
#        return render_to_response("user_profile.html",
#                                  {'user': user,
##                                   'files': {'have_access': have_access,
##                                             'access_requested': access_requested,
##                                             'access_denied': access_denied},
#                                   })
#    else:
#        return render_to_response("permission_denied.html",
#                                  context_instance=RequestContext(request))

def create_profile(request, user_id):
    user = User.objects.get(pk=int(user_id))
    Researcher.objects.create(user=user, first_name=user.first_name, last_name=user.last_name)
    return HttpResponseRedirect(request.session['last_page'])

def render_position_context(request, user, form, action=None, next_step=None, **kwargs):
    context = {'action':action,
               'enable_scroll_position':True,
               'form':form,
               'cancel_redirect_to':reverse('user-profile', args=[user.pk]),
               'next_step':next_step}
    context.update(kwargs)
    context.update(get_user_context(request, user))
    return render_to_response("position.html", RequestContext(request, context))

@check_rendered_page
@login_required
def create_position(request, user_id, *args, **kwargs):
    """display or process the first form of position creation."""
    user = User.objects.get(pk=int(user_id))
    if request.method == 'POST':
        form = CreatePositionForm(request.POST)
        if form.is_valid() :
            researcher, created = Researcher.objects.get_or_create(user=user, first_name=user.first_name, last_name=user.last_name)
            instance = form.save(commit=False)
            instance.researcher = researcher
            instance.save()
            return HttpResponseRedirect(request.session['last_page'])
    else:
        form = CreatePositionForm()
    context = get_form_context(request, form, "Create a new position for user %s" % user.get_full_name())
    context.update(kwargs)
    return render_to_response(kwargs['template'], RequestContext(request, context))

@check_rendered_page
@login_required
def update_position(request, position_id, **kwargs):
    """display or process the form updating a position."""
    position = Position.objects.get(pk=int(position_id))
    user = position.researcher.user
    if request.method == 'POST':
        form = CreatePositionForm(request.POST, instance=position)
        if form.is_valid() :
            form.save()  
            return HttpResponseRedirect(request.session['last_page'])     
    else :
        form = CreatePositionForm(instance=position)
    context = get_form_context(request, form, "Update an existing position for user %s" % user.get_full_name())
    context.update(kwargs)
    return render_to_response(kwargs['template'], RequestContext(request, context))

@login_required
def delete_position(request, position_id):
    position = Position.objects.get(pk=position_id)
    position.delete()
    redirection = request.session['last_page']
    return HttpResponseRedirect(redirection)

@check_rendered_page
def change_password(request, user_id, **kwargs):
    user = User.objects.get(pk=int(user_id))
    if request.method == 'POST' :
        form = PasswordChangeForm(user, request.POST)
        if form.is_valid() :
            user.set_password(form.cleaned_data['new_password2'])
            user.save()
            redirection = request.session['last_page']
            return HttpResponseRedirect(redirection) 
    else :
        form = PasswordChangeForm(user)
    context = get_form_context(request, form, "Change the password of %s" % user.get_full_name())
    context.update(kwargs)
    return render_to_response(kwargs['template'], RequestContext(request, context))

@check_rendered_page
def change_photo(request, user_id, **kwargs):
    user = User.objects.get(pk=int(user_id))
    if request.method == 'POST' :
        form = ChangePhotoForm(request.POST, request.FILES)
        if form.is_valid() :
            researcher, created = Researcher.objects.get_or_create(user=user, first_name=user.first_name, last_name=user.last_name)
            researcher.photo = form.cleaned_data['photo']
            researcher.save() 
            redirection = request.session['last_page']
            return HttpResponseRedirect(redirection) 
    else :
        form = ChangePhotoForm()
    context = get_form_context(request, form, "Change the photo of %s" % user.get_full_name())
    context.update(kwargs)
    return render_to_response(kwargs['template'], RequestContext(request, context))

@check_rendered_page
def change_description(request, user_id, **kwargs):
    user = User.objects.get(pk=int(user_id))
    if request.method == 'POST' :
        form = ChangeDescriptionForm(request.POST)
        if form.is_valid() :
            researcher, created = Researcher.objects.get_or_create(user=user, first_name=user.first_name, last_name=user.last_name)
            researcher.notes = form.cleaned_data['description']
            researcher.save() 
            redirection = request.session['last_page']
            return HttpResponseRedirect(redirection) 
    else :
        try :
            description = user.researcher.notes
        except :
            description = None
        form = ChangeDescriptionForm(initial={'description':description})
    context = get_form_context(request, form, "Change the description of %s" % user.get_full_name())
    context.update(kwargs)
    return render_to_response(kwargs['template'], RequestContext(request, context))

def delete_profile(request, user_id):
    user = User.objects.get(pk=int(user_id))
    profile = user.get_profile()
    profile.delete()
    return HttpResponseRedirect(request.session['last_page'])

@check_rendered_page
def change_access_control(request, user_id, app_label, model, object_id, **kwargs):
    user = User.objects.get(pk=int(user_id))
    model = ContentType.objects.get(app_label=app_label, model=model).model_class()
    try :
        instance = model.objects.get(pk=int(object_id))
    except :
        instance = model.objects.get(pk=object_id) 
    if request.method == 'POST' :
        form = ChangeAccessControlForm(request.POST)
        if form.is_valid() :
            #create all group permissions on the instance
            #and remove permissions for unselected groups
            old_groups = [k.group for k in Permission.objects.get_group_permissions(instance)]
            new_groups = form.cleaned_data['groups']
            for group in new_groups :
                if not group in old_groups :
                    Permission.objects.create_group_permission(instance, group, can_view=True)
            for group in old_groups :
                if not group in new_groups :
                    Permission.objects.remove_group_permission(instance, group)
            
            #create all user permissions on the instance
            #and remove permissions for unselected users
            old_users = [k.user for k in Permission.objects.get_user_permissions(instance)]
            new_users = form.cleaned_data['users']
            for user in new_users :
                if not user in old_users :
                    Permission.objects.create_user_permission(instance, user, can_view=True)
            for user in old_users :
                if not user in new_users :
                    Permission.objects.remove_user_permission(instance, user)
            redirection = request.session['last_page']
            return HttpResponseRedirect(redirection) 
    else :
        form = ChangeAccessControlForm()
        form.fields['users'].queryset = form.fields['users'].queryset.exclude(pk=user.pk)
        if contact :
            form.fields['groups'].initial = [k.group.pk for k in Permission.objects.get_group_permissions(instance)]
            form.fields['users'].initial = [k.user.pk for k in Permission.objects.get_user_permissions(instance)]
    form_header = "Change access control on %s %s" % (instance.__class__._meta.verbose_name.lower(), instance.label)
    context = get_form_context(request, form, form_header)
    context.update(kwargs)
    return render_to_response(kwargs['template'], RequestContext(request, context))

@check_rendered_page
def change_email(request, user_id, **kwargs):
    user = User.objects.get(pk=int(user_id))
    if request.method == 'POST' :
        form = ChangeEMailForm(request.POST)
        if form.is_valid() :
            user.email = form.cleaned_data['email']
            user.save()
            redirection = request.session['last_page']
            return HttpResponseRedirect(redirection) 
    else :
        form = ChangeEMailForm(initial={'email':user.email})
    context = get_form_context(request, form, "Change the email of %s" % user.get_full_name())
    context.update(kwargs)
    return render_to_response(kwargs['template'], RequestContext(request, context))

@login_required
@memorise_last_page
@memorise_last_rendered_page
def lab_profile(request, structure_id, template):
    structure = ScientificStructure.objects.get(pk=int(structure_id))
    selection_id = request.GET.get('selection')
    if selection_id :
        selection = structure.scientificstructure_set.get(pk=int(selection_id))
    else :
        selection = structure
    context = {'structure':structure, 'selection':selection, 'teams':structure.get_children(True, True)}
    context['enable_scroll_position'] = True
    return render_to_response(template, RequestContext(request, context))

def change_logo(request, structure_id):
    pass
