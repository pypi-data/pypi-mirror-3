from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('',
    url(r'^browser/init_session/(?P<view_id>\w+)/$', 'helmholtz.editor.views.editor.init_session_for_editor', name='init-editor-session'),
    url(r'^browser/(?P<view_id>\w+)/$', 'helmholtz.editor.views.editor.display_view', name='editor'),
    url(r'^browser/(?P<view_id>\w+)/execute_command/$', 'helmholtz.editor.views.editor.execute_command', name='execute-command'),
    #edition commands 
    url(r'^browser/(?P<view_id>\w+)/edit/process_action/$', 'helmholtz.editor.views.editor.process_action', name="process-action"),
    url(r'^browser/(?P<view_id>\w+)/edit/add/$', 'helmholtz.editor.views.editor.get_add_form', name="get-add-form"),
    url(r'^browser/(?P<view_id>\w+)/edit/validate_add_form/$', 'helmholtz.editor.views.editor.validate_add_form', name="validate-add-form"),
    url(r'^browser/(?P<view_id>\w+)/edit/modify/$', 'helmholtz.editor.views.editor.get_modify_form', name="get-modify-form"),
    url(r'^browser/(?P<view_id>\w+)/edit/validate_modify_form/$', 'helmholtz.editor.views.editor.validate_modify_form', name="validate-modify-form"),
    url(r'^browser/(?P<view_id>\w+)/edit/delete/$', 'helmholtz.editor.views.editor.get_delete_form', name="get-delete-form"),
    url(r'^browser/(?P<view_id>\w+)/edit/validate_delete_form/$', 'helmholtz.editor.views.editor.validate_delete_form', name="validate-delete-form"),
    url(r'^browser/(?P<view_id>\w+)/edit/validate_add_form/$', 'helmholtz.editor.views.editor.validate_add_form', name="validate-add-form"),
    url(r'^browser/(?P<view_id>\w+)/edit/process_subclass/$', 'helmholtz.editor.views.editor.process_subclasses_form', name="process-subclasses-form"),
    url(r'^browser/(?P<view_id>\w+)/edit/process_parameter_choice/$', 'helmholtz.editor.views.editor.process_parameter_choice_form', name="process-parameter-choice-form"),
    url(r'^browser/(?P<view_id>\w+)/edit/unlink/$', 'helmholtz.editor.views.editor.unlink_object', name="unlink-object"),
    url(r'^browser/(?P<view_id>\w+)/edit/link/$', 'helmholtz.editor.views.editor.link_object', name="get-link-form"),
    url(r'^browser/(?P<view_id>\w+)/edit/validate_link_form/$', 'helmholtz.editor.views.editor.validate_link_form', name="validate-link-form"),
    url(r'^browser/(?P<view_id>\w+)/edit/tag/$', 'helmholtz.editor.views.editor.get_tag_form', name="get-tag-form"),
)
