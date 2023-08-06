from copy import deepcopy

email_constraints = {
    'tableconstraint':{
        'form':'helmholtz.editor.forms.people.EMailForm',
        'displayed_in_navigator':False,
        'in_expansion':[
            {'field':{'identifier':'scientificstructure_set'}},
            {'field':{'identifier':'researcher_set'}},
            {'field':{'identifier':'supplier_set'}},
        ],
        'in_header':[
            {'field':{'identifier':'id'}},
            {'field':{'identifier':'label'}},
            {'field':{'identifier':'identifier'}},
            {'field':{'verbose_name':'structures', 'identifier':'scientificstructure_set.count'}},
            {'field':{'verbose_name':'researchers', 'identifier':'researcher_set.count'}},
            {'field':{'verbose_name':'suppliers', 'identifier':'supplier_set.count'}},
        ],
        'width':'800px',
        'pagination':50
    }
}

email = {
    'content_type':{
       'app_label':'people',
       'model':'email'
    },
    'position':0,
    'constraints':[email_constraints],
}

phone_constraints = {
    'tableconstraint':{
        'form':'helmholtz.editor.forms.people.PhoneForm',
        'displayed_in_navigator':False,
        'in_expansion':[
            {'field':{'identifier':'scientificstructure_set'}},
            {'field':{'identifier':'researcher_set'}},
            {'field':{'identifier':'supplier_set'}},
        ],
        'in_header':[
            {'field':{'identifier':'id'}},
            {'field':{'identifier':'label'}},
            {'field':{'identifier':'identifier'}},
            {'field':{'verbose_name':'structures', 'identifier':'scientificstructure_set.count'}},
            {'field':{'verbose_name':'researchers', 'identifier':'researcher_set.count'}},
            {'field':{'verbose_name':'suppliers', 'identifier':'supplier_set.count'}},
        ],
        'width':'800px',
        'pagination':50
    }
}

phone = {
    'content_type':{
       'app_label':'people',
       'model':'phone'
    },
    'position':1,
    'constraints':[phone_constraints],
}

fax_constraints = {
    'tableconstraint':{
        'form':'helmholtz.editor.forms.people.FaxForm',
        'displayed_in_navigator':False,
        'in_expansion':[
            {'field':{'identifier':'scientificstructure_set'}},
            {'field':{'identifier':'researcher_set'}},
            {'field':{'identifier':'supplier_set'}},
        ],
        'in_header':[
            {'field':{'identifier':'id'}},
            {'field':{'identifier':'label'}},
            {'field':{'identifier':'identifier'}},
            {'field':{'verbose_name':'structures', 'identifier':'scientificstructure_set.count'}},
            {'field':{'verbose_name':'researchers', 'identifier':'researcher_set.count'}},
            {'field':{'verbose_name':'suppliers', 'identifier':'supplier_set.count'}},
        ],
        'width':'800px',
        'pagination':50
    }
}

fax = {
    'content_type':{
       'app_label':'people',
       'model':'fax'
    },
    'position':2,
    'constraints':[fax_constraints],
}

address_constraints = {
    'tableconstraint':{
        'form':'helmholtz.editor.forms.people.AddressForm',
        'displayed_in_navigator':False,
        'in_expansion':[
            {'field':{'identifier':'scientificstructure_set'}},
            {'field':{'identifier':'researcher_set'}},
            {'field':{'identifier':'supplier_set'}},
        ],
        'in_header':[
            {'field':{'identifier':'id'}},
            {'field':{'identifier':'label'}},
            {'field':{'identifier':'__unicode__', 'verbose_name':'complete address'}},
            {'field':{'verbose_name':'structures', 'identifier':'scientificstructure_set.count'}},
            {'field':{'verbose_name':'researchers', 'identifier':'researcher_set.count'}},
            {'field':{'verbose_name':'suppliers', 'identifier':'supplier_set.count'}},
        ],
        'width':'1100px',
        'pagination':50
    }
}

address = {
    'content_type':{
       'app_label':'people',
       'model':'address'
    },
    'position':3,
    'constraints':[address_constraints],
}

website_constraints = {
    'tableconstraint':{
        'form':'helmholtz.editor.forms.people.WebSiteForm',
        'displayed_in_navigator':False,
        'in_expansion':[
            {'field':{'identifier':'scientificstructure_set'}},
            {'field':{'identifier':'researcher_set'}},
            {'field':{'identifier':'supplier_set'}},
        ],
        'in_header':[
            {'field':{'identifier':'id'}},
            {'field':{'identifier':'label'}},
            {'field':{'identifier':'identifier'}},
            {'field':{'verbose_name':'structures', 'identifier':'scientificstructure_set.count'}},
            {'field':{'verbose_name':'researchers', 'identifier':'researcher_set.count'}},
            {'field':{'verbose_name':'suppliers', 'identifier':'supplier_set.count'}},
        ],
        'width':'800px',
        'pagination':50
    }
}

website = {
    'content_type':{
       'app_label':'people',
       'model':'website'
    },
    'position':4,
    'constraints':[website_constraints],
}

contact = {
    'content_type':{
       'app_label':'people',
       'model':'contact'
    },
    'position':1,
    'constraints':[
        {'display_subclasses':True,
         'form':'helmholtz.editor.forms.people.ContactForm',
         'shunt':False 
        }
    ],
    'children':[
        {'entity':email},
        {'entity':phone},
        {'entity':fax},
        {'entity':email},
        {'entity':address},
        {'entity':website},
    ]
}

position_type = {
    'content_type':{
       'app_label':'people',
       'model':'positiontype'
    },
    'position':1,
    'constraints':[
        {
        'form':'helmholtz.editor.forms.people.PositionTypeForm',
        'shunt':True,
        }    
    ],
}

skill = {
    'content_type':{
       'app_label':'people',
       'model':'skilltype'
    },
    'position':2,
    'constraints':[
        {
        'tableconstraint':
        {
         'form':'helmholtz.editor.forms.people.SkillTypeForm',
         'shunt':False,
         'hierarchy':True,
         'displayed_in_navigator':False,
         'in_header':[
             {'field':{'identifier':'name'}},
             {'field':{'identifier':'skilltype_set.count', 'verbose_name':'children'}},
         ],
         'in_expansion':[
             {'field':{'identifier':'id'}},
             {'field':{'identifier':'skilltype_set'}},
         ],
         'width':'600px',
         'pagination':50
        }
        }    
    ]
}

researcher_constraints = {
    'tableconstraint' : {
        'form':'helmholtz.editor.forms.people.ResearcherForm',
        'displayed_in_navigator':False,
        'in_header':[
             {'field':{'identifier':'id'}},
             {'field':{'identifier':'first_name'}},
             {'field':{'identifier':'last_name'}},
             {'field':{'identifier':'user'}},
             {'field':{'verbose_name':'experiments', 'identifier':'experiment_set.count'}},
             {'field':{'verbose_name':'contacts', 'identifier':'contacts.count'}},
             {'field':{'verbose_name':'positions', 'identifier':'position_set.count'}},
        ],
        'in_expansion':[
             {'field':{'identifier':'user'}},
             {'field':{'identifier':'contacts'}},
             {'field':{'identifier':'position_set'}},
             {'field':{'identifier':'photo'}},
             {'field':{'identifier':'notes'}}        
        ],
        'width':'700px',
        'pagination':50
    }
}

researcher_user_link = {
    'content_type':{
        'app_label':'auth',
        'model':'user'
    },
    'position':1,
    'constraints':[
        {
        'form':'helmholtz.editor.forms.access_control.UserForm',
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

researcher_position_link = {
    'content_type':{
        'app_label':'people',
        'model':'position'
    },
    'position':1,
    'constraints':[
        {'tableconstraint':{
             'form':'helmholtz.editor.forms.people.PositionFromResearcherForm',
             'actions':[
                 {'name':'A'},
                 {'name':'M'},
                 {'name':'D'}
             ],
             'in_expansion':[
                 {'field':{'identifier':'notes'}}
             ],
             'in_header':[
                 {'field':{'identifier':'structure'}},
                 {'field':{'identifier':'start'}},
                 {'field':{'identifier':'end'}},
                 {'field':{'identifier':'position_type'}},
             ],
             'width':'500px',
             'pagination':10
         }
        }
    ]
}

email_link = {
    'content_type':{
       'app_label':'people',
       'model':'email'
    },
    'position':0,
    'constraints':[
        {
         'form':'helmholtz.editor.forms.people.EMailForm',
         'shunt':True
        }
    ],
}

phone_link = {
    'content_type':{
       'app_label':'people',
       'model':'phone'
    },
    'position':1,
    'constraints':[
        {
         'form':'helmholtz.editor.forms.people.PhoneForm',
         'shunt':True
        }
    ],
}

fax_link = {
    'content_type':{
       'app_label':'people',
       'model':'fax'
    },
    'position':2,
    'constraints':[
        {
         'form':'helmholtz.editor.forms.people.FaxForm',
         'shunt':True
        }
    ],
}

address_link = {
    'content_type':{
       'app_label':'people',
       'model':'address'
    },
    'position':3,
    'constraints':[
        {
         'form':'helmholtz.editor.forms.people.AddressForm',
         'shunt':True
        }
    ],
}

website_link = {
    'content_type':{
       'app_label':'people',
       'model':'website'
    },
    'position':4,
    'constraints':[
        { 
         'form':'helmholtz.editor.forms.people.WebSiteForm',
         'shunt':True
        }
    ],
}

contact_link = {
    'content_type':{
       'app_label':'people',
       'model':'contact'
    },
    'position':0,
    'constraints':[
        {'display_subclasses':True}
    ],
    'children':[
        {'entity':email_link},
        {'entity':phone_link},
        {'entity':fax_link},
        {'entity':email_link},
        {'entity':address_link},
        {'entity':website_link},
    ]
}

researcher = {
    'content_type':{
       'app_label':'people',
       'model':'researcher'
    },
    'position':2,
    'constraints':[researcher_constraints],
    'children':[
        {'entity':researcher_user_link},
        {'entity':researcher_position_link},
        {'entity':deepcopy(contact_link)}
    ]
}

setup_link = {
    'content_type':{
        'app_label':'equipment',
        'model':'setup'
    },
    'position':1,
    'constraints':[
        {
         'tableconstraint':{
             'form':'helmholtz.editor.forms.equipment.SetupFromStructureForm',
             'shunt':True,
             'actions':[
                 {'name':'A'},
                 {'name':'M'},
                 {'name':'D'},
                 {'name':'L'},
                 {'name':'U'},
             ],
             'in_header' : [
                 {'field':{'identifier':'id'}},
                 {'field':{'identifier':'label'}},
                 {'field':{'verbose_name':'current location', 'identifier':'__unicode__'}}
             ],
             'width':'500px',
             'pagination':25
        } 
        }
    ]
}

structure_group_link = {
    'content_type':{
        'app_label':'auth',
        'model':'group'
    },
    'position':1,
    'constraints':[
        {
         'shunt':True,
         'form':'helmholtz.editor.forms.access_control.GroupForm'
        }
    ]
}

structure_position_link = {
    'content_type':{
        'app_label':'people',
        'model':'position'
    },
    'position':1,
    'constraints':[
        {'tableconstraint':{
             'form':'helmholtz.editor.forms.people.PositionFromStructureForm',
             'actions':[
                 {'name':'A'},
                 {'name':'M'},
                 {'name':'D'}
             ],
             'in_expansion':[
                 {'field':{'identifier':'notes'}},
             ],
             'in_header':[
                 {'field':{'identifier':'researcher'}},
                 {'field':{'identifier':'start'}},
                 {'field':{'identifier':'end'}},
                 {'field':{'identifier':'position_type'}},
             ],
             'width':'500px',
             'pagination':10
         }
        }
    ]
}

structure_link_constraints = [
    {'tableconstraint':{
         'displayed_in_navigator':False,
         'form':'helmholtz.editor.forms.people.ScientificStructureForm',
         'actions':[
             {'name':'A'},
             {'name':'M'},
             {'name':'D'},
             {'name':'L'},
             {'name':'U'},
         ],
         'in_expansion':[
             {'field':{'identifier':'db_group'}},
             {'field':{'identifier':'contacts'}},
             {'field':{'identifier':'logo'}},
             {'field':{'identifier':'is_data_provider'}},
             {'field':{'identifier':'foundation_date'}},
             {'field':{'identifier':'dissolution_date'}},
             {'field':{'identifier':'description'}},
         ],
         'in_header':[
             {'field':{'identifier':'id'}},
             {'field':{'identifier':'diminutive'}},
             {'field':{'identifier':'name'}},
             {'field':{'identifier':'db_group'}},
             {'field':{'verbose_name':'contacts', 'identifier':'contacts.count'}},
         ],
         'width':"1000px",
         'pagination':10
     }
    }
]

structure_link = {
    'content_type':{
       'app_label':'people',
       'model':'scientificstructure'
    },
    'position':1,
    'constraints':structure_link_constraints,
    'children':[
        {'entity':deepcopy(structure_group_link)},
        {'entity':deepcopy(contact_link)}, #do not understand why the copy removing the subclass display problem
    ]
}

structure_constraints = [
    {'tableconstraint':{
         'displayed_in_navigator':False,
         'form':'helmholtz.editor.forms.people.ScientificStructureForm',
         'hierarchy':True,
         'in_expansion':[
             {'field':{'identifier':'db_group'}},
             {'field':{'identifier':'contacts'}},
             {'field':{'identifier':'position_set'}},
             {'field':{'identifier':'scientificstructure_set'}},
             {'field':{'identifier':'setup_set'}},
             {'field':{'identifier':'logo'}},
             {'field':{'identifier':'is_data_provider'}},
             {'field':{'identifier':'dissolution_date'}},
             {'field':{'identifier':'description'}},
         ],
         'in_header':[
             {'field':{'identifier':'id'}},
             {'field':{'identifier':'diminutive'}},
             {'field':{'identifier':'name'}},
             {'field':{'identifier':'db_group'}},
             {'field':{'verbose_name':'teams', 'identifier':'scientificstructure_set.count'}},
             {'field':{'verbose_name':'researchers', 'identifier':'number_of_researchers'}},
             {'field':{'verbose_name':'setups', 'identifier':'setup_set.count'}},
             {'field':{'verbose_name':'contacts', 'identifier':'contacts.count'}},
         ],
         'width':"1100px",
         'pagination':10
     }
    }
]

structure = {
    'content_type':{
       'app_label':'people',
       'model':'scientificstructure'
    },
    'position':3,
    'constraints':structure_constraints,
    'children':[
        {'entity':structure_group_link},
        {'entity':structure_position_link},
        {'entity':deepcopy(contact_link)},
        {'entity':structure_link},
        {'entity':setup_link}
    ]
}

supplier = {
    'content_type':{
       'app_label':'people',
       'model':'supplier'
    },
    'position':5,
    'constraints':[
        {'tableconstraint':
         {
          'displayed_in_navigator':False,
          'shunt':False,
          'form':'helmholtz.editor.forms.people.SupplierForm',
          'in_header':[
              {'field':{'identifier':'name'}},
              {'field':{'verbose_name':'contacts', 'identifier':'contacts.count'}},
          ],
          'in_expansion':[
              {'field':{'identifier':'contacts'}},
          ],
          'width':"500px",
          'pagination':10
         }
        }
    ],
    'children':[
        {'entity':deepcopy(contact_link)},
    ]
}
