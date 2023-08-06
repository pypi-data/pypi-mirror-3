protocol_constraints = [
    {'tableconstraint':{
         'shunt':True,
         'displayed_in_navigator':False,
         'form':'helmholtz.editor.forms.storage.CommunicationProtocolForm',
         'in_header':[
             {'field':{'identifier':'initials'}},
             {'field':{'identifier':'name'}}
         ],
         'width':"500px",
         'pagination':25
     }
    }
]

protocol = {
    'content_type':{
       'app_label':'storage',
       'model':'communicationprotocol'
    },
    'position':1,
    'constraints':protocol_constraints,
}

mimetype_constraints = [
    {'tableconstraint':{
         'shunt':True,
         'displayed_in_navigator':False,
         'form':'helmholtz.editor.forms.storage.MimeTypeForm',
         'in_expansion':[
             
         ],
         'in_header':[
             {'field':{'identifier':'name'}},
             {'field':{'identifier':'extension'}},
         ],
         'width':"500px",
         'pagination':25
     }
    }
]

mimetype = {
    'content_type':{
       'app_label':'storage',
       'model':'mimetype'
    },
    'position':2,
    'constraints':mimetype_constraints,
}

location_constraints = [
    {'tableconstraint':{
         'form':'helmholtz.editor.forms.storage.FileLocationForm',
         'actions' : [
             {'name':'A'},
             {'name':'M'},
             {'name':'D'},
         ],
         'in_expansion':[
             {'field':{'identifier':'file_set'}},
         ],
         'in_header':[
             {'field':{'identifier':'id'}},
             #{'field':{'verbose_name':'complete path', 'identifier':'get_path'}},
             {'field':{'identifier':'root'}},
             {'field':{'identifier':'path'}},
             {'field':{'verbose_name':'files', 'identifier':'file_set.count'}}    
         ],
         'width':"800px",
         'pagination':25
     }
    }
]

location_file_link_constraints = [
    {'tableconstraint':{
         'displayed_in_navigator':False,
         'form':'helmholtz.editor.forms.storage.FileFromLocationForm',
         'actions' : [
             {'name':'A'},
             {'name':'M'},
             {'name':'D'},
             {'name':'L'},
             {'name':'U'},
         ],
         'in_header':[
             {'field':{'identifier':'id'}},
             {'field':{'identifier':'name'}},
             {'field':{'identifier':'mimetype'}},
             {'field':{'identifier':'original'}},
             {'field':{'verbose_name':'signals', 'identifier':'signal_set.count'}}
         ],
         'in_expansion':[
             {'field':{'identifier':'notes'}},
         ],
         'width':"700px",
         'pagination':50
     }
    }
]

location_file_link = {
    'content_type':{
       'app_label':'storage',
       'model':'file'
    },
    'position':1,
    'constraints':location_file_link_constraints,
}

location_link = {
    'content_type':{
       'app_label':'storage',
       'model':'filelocation'
    },
    'position':1,
    'constraints':location_constraints,
    'children':[
        {'entity':location_file_link}
    ]
}

server_constraints = [
    {'tableconstraint':{
         'displayed_in_navigator':False,
         'form':'helmholtz.editor.forms.storage.FileServerForm',
         'in_header':[
             {'field':{'identifier':'id'}},
             {'field':{'identifier':'label'}},
             {'field':{'identifier':'protocol'}},
             {'field':{'identifier':'ip_address'}},
             {'field':{'identifier':'port'}},
             {'field':{'verbose_name':'file locations', 'identifier':'filelocation_set.count'}}    
         ],
         'in_expansion':[
             {'field':{'identifier':'filelocation_set'}},
         ],
         'width':"900px",
         'pagination':25
     }
    }
]

server = {
    'content_type':{
       'app_label':'storage',
       'model':'fileserver'
    },
    'position':3,
    'constraints':server_constraints,
    'children':[
        {'entity':location_link},
    ]
}

file_constraints = [
    {'tableconstraint':{
         'displayed_in_navigator':False,
         'form':'helmholtz.editor.forms.storage.FileForm',
         'actions' : [
             {'name':'A'},
             {'name':'M'},
             {'name':'D'},
         ],
         'in_header':[
             {'field':{'identifier':'id'}},
             {'field':{'verbose_name':'signals', 'identifier':'signal_set.count'}}
         ],
         'in_expansion':[
             
         ],
         'width':"700px",
         'pagination':50
     }
    }
]

file_constraints = [
    {'tableconstraint':{
         'displayed_in_navigator':False,
         'form':'helmholtz.editor.forms.storage.FileForm',
         'actions' : [
             {'name':'A'},
             {'name':'M'},
             {'name':'D'},
         ],
         'in_header':[
             {'field':{'identifier':'id'}},
             {'field':{'verbose_name':'location', 'identifier':'location.url'}},
             {'field':{'identifier':'name'}},
             {'field':{'identifier':'mimetype'}},
             {'field':{'identifier':'original'}},
             {'field':{'verbose_name':'signals', 'identifier':'signal_set.count'}}
         ],
         'in_expansion':[
             {'field':{'identifier':'notes'}},
             {'field':{'identifier':'object_permissions'}},
             {'field':{'identifier':'tag_set'}},
         ],
         'width':"700px",
         'pagination':50,
         #'display_permissions':True,
         #'display_tags':True,
         #'display_annotations':True,
         #'display_attachments':True
     }
    }
]

group_permission_constraints = {
    'tableconstraint':{
        'displayed_in_navigator':False,
        'shunt':True,
        'actions' : [
             {'name':'A'},
             {'name':'M'},
             {'name':'D'},
         ],
        'form':'helmholtz.editor.forms.access_control.GroupPermissionForm',
        'in_header':[
            {'field':{'identifier':'id'}},
            {'field':{'identifier':'group'}},
            {'field':{'identifier':'can_view'}},
            {'field':{'identifier':'can_modify'}},
            {'field':{'identifier':'can_delete'}},
            {'field':{'identifier':'can_download'}},
            {'field':{'identifier':'can_modify_permission'}},
        ],
        'width':"800px",
        'pagination':50
    }
}

group_permission = {
    'content_type':{
       'app_label':'access_control',
       'model':'grouppermission'
    },
    'position':1,
    'constraints':[
        group_permission_constraints
    ]
}

user_permission_constraints = {
    'tableconstraint':{
        'displayed_in_navigator':False,
        'shunt':True,
        'actions' : [
             {'name':'A'},
             {'name':'M'},
             {'name':'D'},
         ],
        'form':'helmholtz.editor.forms.access_control.UserPermissionForm',
        'in_header':[
            {'field':{'identifier':'id'}},
            {'field':{'identifier':'user'}},
            {'field':{'identifier':'can_view'}},
            {'field':{'identifier':'can_modify'}},
            {'field':{'identifier':'can_delete'}},
            {'field':{'identifier':'can_download'}},
            {'field':{'identifier':'can_modify_permission'}},
        ],
        'width':"800px",
        'pagination':50
    }
}

user_permission = {
    'content_type':{
       'app_label':'access_control',
       'model':'userpermission'
    },
    'position':2,
    'constraints':[
        user_permission_constraints
    ]
}

permission = {
    'content_type':{
       'app_label':'access_control',
       'model':'permission'
    },
    'position':1,
    'constraints':[
        {'display_subclasses':True}
    ],
    'children':[
        {'entity':group_permission},
        {'entity':user_permission},
    ]
}

base_tag = {
    'content_type':{
       'app_label':'annotation',
       'model':'tag'
    },
    'position':1,
    'constraints':[
        {
         'tableconstraint':{
             'shunt':True,
             'form':'helmholtz.editor.forms.annotation.TagForm',
             'in_header':[
                 {'field':{'identifier':'id'}},
                 {'field':{'identifier':'label'}},
             ],
             'width':'500px',
             'pagination':50
         }
        }
    ]
}

annotation = {
    'content_type':{
       'app_label':'annotation',
       'model':'annotation'
    },
    'position':1,
    'constraints':[
        {
         'tableconstraint':{
             'shunt':False,
             'form':'helmholtz.editor.forms.annotation.AnnotationForm',
             'in_header':[
                 {'field':{'identifier':'id'}},
                 {'field':{'identifier':'label'}},
             ],
             'in_expansion':[
                 {'field':{'identifier':'text'}},
             ],
             'width':'500px',
             'pagination':50
         }
        }
    ]
}

attachment = {
    'content_type':{
       'app_label':'annotation',
       'model':'attachment'
    },
    'position':1,
    'constraints':[
        {
         'tableconstraint':{
             'shunt':True,
             'form':'helmholtz.editor.forms.annotation.AttachmentForm',
             'in_header':[
                 {'field':{'identifier':'id'}},
                 {'field':{'identifier':'label'}},
                 {'field':{'identifier':'document'}},
             ],
             'width':'600px',
             'pagination':50
         }
        }
    ]
}

tag = {
    'content_type':{
       'app_label':'annotation',
       'model':'tag'
    },
    'position':2,
    'constraints':[
        {
         'display_subclasses':True,
         'display_base_class':True
         }
    ],
    'children':[
        {'entity':base_tag},
        {'entity':annotation},
        {'entity':attachment},
    ]
}

data_file = {
    'content_type':{
       'app_label':'storage',
       'model':'file'
    },
    'position':4,
    'constraints':file_constraints,
    'children':[
        {'entity':permission},
        {'entity':tag}
    ]
}

