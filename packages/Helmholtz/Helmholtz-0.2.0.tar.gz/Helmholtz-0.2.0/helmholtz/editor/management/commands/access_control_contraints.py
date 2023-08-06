#encoding:utf-8
group_user_researcher_link = {
    'content_type':{
        'app_label':'people',
        'model':'researcher'
    },
    'position':1,
    'constraints':[
        {
        'form':'helmholtz.editor.forms.people.ResearcherForm',
        'shunt':True,
        'actions':[
            {'name':'A'},
            {'name':'M'},
            {'name':'D'},
            {'name':'L'},
            {'name':'U'}
        ]
        }
    ]
}

group_user_constraints = [
    {'tableconstraint':{
         'form':'helmholtz.editor.forms.access_control.UserFormWithoutGroups',
         'width':'750px',
         'actions':[
             {'name':'A'},
             {'name':'M'},
             {'name':'D'},
             {'name':'L'},
             {'name':'U'}
         ],
         'in_header':[
             {'field':{'identifier':'id'}},
             {'field':{'identifier':'username'}},
             {'field':{'identifier':'first_name'}},
             {'field':{'identifier':'last_name'}},
             {'field':{'identifier':'researcher'}},
             {'field':{'verbose_name':'groups', 'identifier':'groups.count'}},
             #{'name':'connections', 'notation':'connections.count'},
             #{'name':'requests', 'notation':'requests.count'},
             #{'name':'responses', 'notation':'responses.count'},
             #{'name':'sent mails', 'notation':'mails_as_sender.count'},
             #{'name':'recieved mails', 'notation':'mails_as_recipient.count'},
             #{'name':'int permissions', 'notation':'integeruserpermission_set.count'},
             #{'name':'char permissions', 'notation':'charuserpermission_set.count'},
         ],
         'in_expansion':[
             {'field':{'identifier':'researcher'}},
             {'field':{'identifier':'groups'}},
         ]
     }
    }
]

group_user_group_link = {
    'content_type':{
        'app_label':'auth',
        'model':'group'
    },
    'position':1,
    'constraints':[
        {
        'form':'helmholtz.editor.forms.access_control.GroupForm',
        'shunt':True,
        'actions':[
            {'name':'A'},
            {'name':'M'},
            {'name':'D'},
            {'name':'L'},
            {'name':'U'}
        ]
        }
    ]
}

group_user_link = {
    'content_type':{
        'app_label':'auth',
        'model':'user'
    },
    'position':1,
    'constraints':group_user_constraints,
    'children':[
        {'entity':group_user_group_link},
        {'entity':group_user_researcher_link}        
#        group_user_iupermission_link,
#        group_user_cupermission_link
    ]
}

group_structure_link = {
    'content_type':{
        'app_label':'people',
        'model':'scientificstructure'
    },
    'position':2,
    'constraints':[
        {'shunt':True,
         'form':'helmholtz.editor.forms.people.ScientificStructureWithoutGroupForm',
         'actions':[
              {'name':'A'},
              {'name':'M'},
              {'name':'D'},
              {'name':'L'},
              {'name':'U'}
         ],
        }  
    ]
}

group_constraints = [
    {'tableconstraint':{
         'form':'helmholtz.editor.forms.access_control.GroupForm',
         'displayed_in_navigator':False,
         'in_header':[
             {'field':{'identifier':'id'}},
             {'field':{'identifier':'name'}},
             {'field':{'identifier':'scientificstructure'}},
             {'field':{'verbose_name':'users', 'identifier':'user_set.count'}},
         ],
         'in_expansion':[
             {'field':{'identifier':'scientificstructure'}},
             {'field':{'identifier':'user_set'}},
         ],
         'width':'850px',
         'pagination':5
     }
    }
]

group = {
    'content_type':{
       'app_label':'auth',
       'model':'group'
    },
    'position':1,
    'constraints':group_constraints,
    'children':[
        {'entity':group_user_link},
        {'entity':group_structure_link},
#        group_igpermission_link,
#        group_cgpermission_link
    ],
}

user_constraints = [
    {'tableconstraint':{
         'form':'helmholtz.editor.forms.access_control.UserForm',
         'displayed_in_navigator':False,
         'in_header':[
             {'field':{'identifier':'id'}},
             {'field':{'identifier':'username'}},
             {'field':{'identifier':'first_name'}},
             {'field':{'identifier':'last_name'}},
             {'field':{'identifier':'email'}},
             {'field':{'identifier':'researcher'}},
             {'field':{'verbose_name':'groups', 'identifier':'groups.count'}},
             {'field':{'verbose_name':'connections', 'identifier':'connections.count'}},
         ],
         'in_expansion':[
             {'field':{'identifier':'researcher'}},
             {'field':{'identifier':'groups'}},
             {'field':{'identifier':'is_staff'}},
             {'field':{'identifier':'is_active'}},
             {'field':{'identifier':'is_superuser'}},
             {'field':{'identifier':'last_login'}},
             {'field':{'identifier':'date_joined'}},
         ],
         'width':'1100px',
         'pagination':50
     }
    }
]

user_group_link = {
    'content_type':{
        'app_label':'auth',
        'model':'group'
    },
    'position':2,
    'constraints':[
        {'shunt':True,
         'form':'helmholtz.editor.forms.access_control.GroupForm',
         'actions':[
              {'name':'A'},
              {'name':'M'},
              {'name':'D'},
              {'name':'L'},
              {'name':'U'}
         ],
        }  
    ]
}

user_researcher_link = {
    'content_type':{
        'app_label':'people',
        'model':'researcher'
    },
    'position':1,
    'constraints':[
        {'shunt':True,
         'form':'helmholtz.editor.forms.people.ResearcherWithoutUserForm',
         'actions':[
              {'name':'A'},
              {'name':'M'},
              {'name':'D'},
              {'name':'L'},
              {'name':'U'}
         ],
        }  
    ]
}

user = {
    'content_type':{
       'app_label':'auth',
       'model':'user'
    },
    'position':2,
    'constraints':user_constraints,
    'children':[
        {'entity':user_researcher_link},
        {'entity':user_group_link}
    ]
#    'links':[
#        user_iupermission_link,
#        user_cupermission_link
#    ],
}

uac_constraints = [
    {
     'form':'helmholtz.editor.forms.access_control.UnderAccessControlEntityForm',
     'shunt':True,
     'actions':[
         {'name':'A'},
         {'name':'M'},
         {'name':'D'},
     ]
    }
]

uac_entity = {
    'content_type':{
       'app_label':'access_control',
       'model':'underaccesscontrolentity'
    },
    'position':3,
    'constraints':uac_constraints,
}

access_request_constraints = [
    {'tableconstraint':{
         'form':'helmholtz.editor.forms.access_request.AccessRequestForm',
         'displayed_in_navigator':False,
         'shunt':True,
         'actions':[
             {'name':'M'},
             {'name':'D'}
         ],
         'in_header':[
             {'field':{'identifier':'id'}},
             {'field':{'identifier':'user'}},
             {'field':{'identifier':'index.content_type', 'verbose_name':'content type'}},
             {'field':{'identifier':'index.object', 'verbose_name':'object'}},
             {'field':{'identifier':'request_date'}},
             {'field':{'identifier':'response_date'}},
             {'field':{'identifier':'response_by'}},
             {'field':{'identifier':'state'}},
         ],
        'width':'800px',
        'pagination':50
    }
   } 
]

access_request = {
    'content_type':{
       'app_label':'access_request',
       'model':'accessrequest'
    },
    'position':4,
    'constraints':access_request_constraints,
}
