species_strain_constraints = [
    {'tableconstraint':{
         'actions':[
             {'name':'A'},
             {'name':'M'},
             {'name':'D'},
             {'name':'L'},
             {'name':'U'},
         ],
         'in_header':[
             {'field':{'identifier':'label'}},
             {'field':{'identifier':'nomenclature'}},
             {'field':{'identifier':'url'}},
         ],
         'in_expansion':[
             {'field':{'identifier':'notes'}}
         ],
         'displayed_in_navigator':False,
         'form':'helmholtz.editor.forms.species.StrainForm',
         'width':'1000px',
         'pagination':25
    }
   }  
]

species_strain = {
    'content_type':{
       'app_label':'species',
       'model':'strain'
    },
    'position':0,
    'constraints':species_strain_constraints,
}

species_constraints = [
    {'tableconstraint':{
         'displayed_in_navigator':False,
         'form':'helmholtz.editor.forms.species.SpeciesForm',
         'in_header':[
             {'field':{'identifier':'english_name'}},
             {'field':{'identifier':'scientific_name'}},
             {'field':{'identifier':'url'}},
             {'field':{'identifier':'strain_set.count', 'verbose_name':'strains'}},
         ],
         'in_expansion':[
             {'field':{'identifier':'strain_set'}},
             {'field':{'identifier':'id'}},
             {'field':{'identifier':'codename'}},
             {'field':{'identifier':'lsid'}},
         ],
         'width':"1100px",
         'pagination':50
     }
    }
]

species = {
    'content_type':{
       'app_label':'species',
       'model':'species'
    },
    'position':1,
    'constraints':species_constraints,
    'children':[
        {'entity':species_strain},
    ]
}
