from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
    url(r'^lab_list/$', 'helmholtz.people.views.lab_list', {'template':"lab_list.html"}, name='lab-list'),
    url(r'^lab_profile/(?P<structure_id>\w*)/$', 'helmholtz.people.views.lab_profile', {'template':"lab_profile.html"}, name='lab-profile'),
    url(r'^profile/(?P<user_id>\w*)/$', 'helmholtz.people.views.show_profile', {'template':"user_profile.html"}, name='user-profile'),
    #create
    url(r'^profile/create_profile/(?P<user_id>\w*)/$', 'helmholtz.people.views.create_profile', name='create-profile'),
    url(r'^profile/create_position/(?P<user_id>\w*)/$', 'helmholtz.people.views.create_position', {'template':"dialog_form.html"}, name='create-position'),
    #update
    url(r'profile/change_email/(?P<user_id>\w*)/$', 'helmholtz.people.views.change_email', {'template':"dialog_form.html"}, name="change-email"),
    url(r'profile/change_password/(?P<user_id>\w*)/$', 'helmholtz.people.views.change_password', {'template':"dialog_form.html"}, name="change-password"),
    url(r'profile/change_photo/(?P<user_id>\w*)/$', 'helmholtz.people.views.change_photo', {'template':"dialog_form.html"}, name="change-photo"),
    url(r'profile/change_logo/(?P<structure_id>\w*)/$', 'helmholtz.people.views.change_logo', {'template':"dialog_form.html"}, name="change-logo"),
    url(r'profile/change_description/(?P<user_id>\w*)/$', 'helmholtz.people.views.change_description', {'template':"dialog_form.html"}, name="change-description"),
    url(r'profile/change_access_control/(?P<user_id>\w*)/(?P<app_label>\w*)/(?P<model>\w*)/(?P<object_id>\w*)/$', 'helmholtz.people.views.change_access_control', {'template':"dialog_form.html"}, name="change-access-control"),
    url(r'^profile/update_position/(?P<position_id>\d+)/$', 'helmholtz.people.views.update_position', {'template':"dialog_form.html"}, name='update-position'),
    url(r'^profile/delete_position/(?P<position_id>\d+)/$', 'helmholtz.people.views.delete_position', name='delete-position'),
    url(r'^profile/delete_profile/(?P<user_id>\w*)/$', 'helmholtz.people.views.delete_profile', name='delete-profile'),
    #contacts
    url(r'^contact_admins/$', 'helmholtz.people.views.contact_admins', {'template':"dialog_form.html"}, name='contact'),
    url(r'^contact_user/(?P<recipient_id>\w*)/$', 'helmholtz.people.views.contact_user', {'template':"dialog_form.html"}, name='contact-user'),
    url(r'^contact_group/(?P<recipient_id>\w*)/$', 'helmholtz.people.views.contact_group', {'template':"dialog_form.html"}, name='contact-group'),
    url(r'^contact_owners/(?P<index_id>\w*)/$', 'helmholtz.people.views.contact_owners', {'template':"dialog_form.html"}, name='contact-owners'),
    url(r'^contact/create/(?P<subclass>\w*)/(?P<user_id>\w*)/$', 'helmholtz.people.views.create_contact', {'template':"dialog_form.html"}, name='create-contact'),
    url(r'^contact/update/(?P<user_id>\w*)/(?P<contact_id>\w*)/$', 'helmholtz.people.views.update_contact', {'template':"dialog_form.html"}, name='update-contact'),
    url(r'^contact/delete/(?P<user_id>\w*)/(?P<contact_id>\w*)/$', 'helmholtz.people.views.delete_contact', name='delete-contact'),
    
) 
