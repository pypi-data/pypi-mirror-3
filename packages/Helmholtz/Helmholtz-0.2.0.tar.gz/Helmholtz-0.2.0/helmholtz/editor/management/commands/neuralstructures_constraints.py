brain_region_cell_type_constraints = [
    {'tableconstraint':{
         'shunt':True,
         'actions':[
             {'name':'A'},
             {'name':'M'},
             {'name':'D'},
             {'name':'L'},
             {'name':'U'},
         ],
         'displayed_in_navigator':False,
         'form':'helmholtz.editor.forms.neuralstructures.CellTypeFromBrainRegionForm',
         'width':"750px",
         'pagination':50
     }
    }
]

brain_region_cell_type = {
    'content_type':{
       'app_label':'neuralstructures',
       'model':'celltype'
    },
    'position':0,
    'constraints':brain_region_cell_type_constraints,
}

brain_region_species_constraints = [
    {
     'shunt':True,
     'actions':[
         {'name':'A'},
         {'name':'M'},
         {'name':'D'},
         {'name':'L'},
         {'name':'U'},
     ],
     'form':'helmholtz.editor.forms.neuralstructures.SpeciesFromBrainRegionForm',
    }
]

brain_region_species = {
    'content_type':{
       'app_label':'species',
       'model':'species'
    },
    'position':1,
    'constraints':brain_region_species_constraints,
}

brain_region_constraints = [
    {'tableconstraint':{
         'displayed_in_navigator':False,
         'form':'helmholtz.editor.forms.neuralstructures.BrainRegionForm',
         'hierarchy':True,
         'in_header':[
             {'field':{'identifier':'id'}},
             {'field':{'identifier':'name'}},
             {'field':{'identifier':'abbreviation'}},
             {'field':{'identifier':'url'}},
             {'field':{'verbose_name':'brain regions', 'identifier':'brainregion_set.count'}},
             {'field':{'verbose_name':'cell types', 'identifier':'celltype_set.count'}},
             {'field':{'verbose_name':'species', 'identifier':'species.count'}}
         ],
         'in_expansion':[
             {'field':{'identifier':'species'}},
             {'field':{'identifier':'brainregion_set'}},
             {'field':{'identifier':'celltype_set'}},
         ],
         'width':"900px",
         'pagination':50
     }
    }
]

brain_region = {
    'content_type':{
       'app_label':'neuralstructures',
       'model':'brainregion'
    },
    'position':1,
    'constraints':brain_region_constraints,
    'children':[
        {'entity':brain_region_cell_type},
        {'entity':brain_region_species}
    ]
}

cell_type_brain_region_constraints = [
    {
     'shunt':True,
     'actions':[
         {'name':'A'},
         {'name':'M'},
         {'name':'D'},
         {'name':'L'},
         {'name':'U'},
     ],
     'displayed_in_navigator':False,
     'form':'helmholtz.editor.forms.neuralstructures.BrainRegionFromCellTypeForm'
    }
]

cell_type_brain_region = {
    'content_type':{
       'app_label':'neuralstructures',
       'model':'brainregion'
    },
    'position':0,
    'constraints':cell_type_brain_region_constraints,
}

cell_type_constraints = [
    {'tableconstraint':{
         'displayed_in_navigator':False,
         'form':'helmholtz.editor.forms.neuralstructures.CellTypeForm',
         'in_header':[
             {'field':{'identifier':'id'}},
             {'field':{'identifier':'name'}},
             {'field':{'identifier':'url'}},
             {'field':{'verbose_name':'brain regions', 'identifier':'brain_regions.count'}},
         ],
         'in_expansion':[
             {'field':{'identifier':'brain_regions'}},
         ],
         'width':"750px",
         'pagination':50
     }
    }
]

cell_type = {
    'content_type':{
       'app_label':'neuralstructures',
       'model':'celltype'
    },
    'position':2,
    'constraints':cell_type_constraints,
    'children':[
        {'entity':cell_type_brain_region},
    ]
}
