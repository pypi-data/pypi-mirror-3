#encoding:utf-8
from copy import deepcopy

material_constraints = [
    {
     'displayed_in_navigator':True,
     'shunt':True,
     'form':'helmholtz.editor.forms.equipment.MaterialForm',
    }
]

material = {
    'content_type':{
       'app_label':'equipment',
       'model':'material'
    },
    'position':1,
    'constraints':material_constraints,
}

stereotaxic_type_constraints = {
    'form':'helmholtz.editor.forms.equipment.StereotaxicTypeForm',
    'displayed_in_navigator':True,
    'shunt':True
}

stereotaxic_type = {
    'content_type':{
       'app_label':'equipment',
       'model':'stereotaxictype'
    },
    'position':2,
    'constraints':[
        stereotaxic_type_constraints
    ],
}

base_equipment_type_constraints = {
    'form':'helmholtz.editor.forms.equipment.EquipmentTypeForm',
    'displayed_in_navigator':True,
    'shunt':True
}

base_equipment_type = {
    'content_type':{
       'app_label':'equipment',
       'model':'equipmenttype'
    },
    'position':1,
    'constraints':[
        base_equipment_type_constraints
    ]
}

equipment_type = {
    'content_type':{
       'app_label':'equipment',
       'model':'equipmenttype'
    },
    'position':2,
    'constraints':[
        {
         'displayed_in_navigator':True,
         'display_subclasses':True,
         'display_base_class':True,
        }
    ],
    'children':[
        {'entity':base_equipment_type},
        {'entity':stereotaxic_type},
    ]
}

device_constraints = {
    'tableconstraint':{
        'actions':[
            {'name':'A'},
            {'name':'D'},
            {'name':'M'},
        ],
        'displayed_in_navigator':False,
        'form':'helmholtz.editor.forms.equipment.DeviceForm',
        'in_expansion':[
            {'field':{'identifier':'notes'}},
        ],
        'in_header':[
            {'field':{'identifier':'id'}},
            {'field':{'identifier':'label'}},
            {'field':{'identifier':'serial_or_id'}},
        ],
        'width':"650px",
        'pagination':50
    }
}


device = {
    'force':True,
    'content_type':{
       'app_label':'equipment',
       'model':'device'
    },
    'position':1,
    'constraints':[
        device_constraints
    ]
}

recording_point_constraints = {
    'tableconstraint':{
        'shunt':True,
        'actions':[
            {'name':'A'},
            {'name':'D'},
            {'name':'M'},
        ],
        'displayed_in_navigator':False,
        'form':'helmholtz.editor.forms.equipment.RecordingPointForm',
        'in_header':[
            {'field':{'identifier':'id'}},
            {'field':{'identifier':'label'}},
            {'field':{'identifier':'number'}},
        ],
        'width':"650px",
        'pagination':50
    }
}

recording_point = {
    'force':True,
    'content_type':{
       'app_label':'equipment',
       'model':'recordingpoint'
    },
    'position':1,
    'constraints':[
        recording_point_constraints
    ]
}

generic_constraints = {
    'tableconstraint':{
        'displayed_in_navigator':False,
        'form':'helmholtz.editor.forms.equipment.GenericEquipmentForm',
        'in_expansion':[
            {'field':{'identifier':'recordingpoint_set'}},
            {'field':{'identifier':'device_set'}},
        ],
        'in_header':[
            {'field':{'identifier':'id'}},
            {'field':{'identifier':'model'}},
            {'field':{'identifier':'manufacturer'}},
            {'field':{'identifier':'type'}},
            {'field':{'verbose_name':'recording points', 'identifier':'recordingpoint_set.count'}},
            {'field':{'verbose_name':'devices', 'identifier':'device_set.count'}},
        ],
        'width':"750px",
        'pagination':50
    }
}


generic = {
    'content_type':{
       'app_label':'equipment',
       'model':'genericequipment'
    },
    'position':1,
    'constraints':[
        generic_constraints
    ],
    'children':[
        {'entity':device},
        {'entity':recording_point}
    ]
}

sharp_constraints = {
    'tableconstraint':{
        'displayed_in_navigator':False,
        'form':'helmholtz.editor.forms.electrophysiology.SharpElectrodeForm',
        'in_expansion':[
            {'field':{'identifier':'recordingpoint_set'}},
            {'field':{'identifier':'device_set'}},
        ],
        'in_header':[
            {'field':{'identifier':'id'}},
            {'field':{'identifier':'model'}},
            {'field':{'identifier':'manufacturer'}},
            {'field':{'identifier':'material'}},
            {'field':{'identifier':'external_diameter'}},
            {'field':{'identifier':'internal_diameter'}},
            {'field':{'verbose_name':'recording points', 'identifier':'recordingpoint_set.count'}},
            {'field':{'verbose_name':'devices', 'identifier':'device_set.count'}},
        ],
        'width':"750px",
        'pagination':50
    }
}

sharp = {
    'content_type':{
       'app_label':'electrophysiology',
       'model':'sharpelectrode'
    },
    'position':1,
    'constraints':[
        sharp_constraints
    ],
    'children':[
        {'entity':deepcopy(device)},
        {'entity':deepcopy(recording_point)}
    ]
}

patch_constraints = {
    'tableconstraint':{
        'displayed_in_navigator':False,
        'form':'helmholtz.editor.forms.electrophysiology.PatchElectrodeForm',
        'in_expansion':[
            {'field':{'identifier':'recordingpoint_set'}},
            {'field':{'identifier':'device_set'}},
        ],
        'in_header':[
            {'field':{'identifier':'id'}},
            {'field':{'identifier':'model'}},
            {'field':{'identifier':'manufacturer'}},
            {'field':{'identifier':'material'}},
            {'field':{'identifier':'external_diameter'}},
            {'field':{'identifier':'internal_diameter'}},
            {'field':{'verbose_name':'recording points', 'identifier':'recordingpoint_set.count'}},
            {'field':{'verbose_name':'devices', 'identifier':'device_set.count'}},
        ],
        'width':"750px",
        'pagination':50
    }
}

patch = {
    'content_type':{
       'app_label':'electrophysiology',
       'model':'patchelectrode'
    },
    'position':1,
    'constraints':[
        patch_constraints
    ],
    'children':[
        {'entity':deepcopy(device)},
        {'entity':deepcopy(recording_point)}
    ]
}

solid_constraints = {
    'tableconstraint':{
        'displayed_in_navigator':False,
        'form':'helmholtz.editor.forms.electrophysiology.SolidElectrodeForm',
        'in_expansion':[
            {'field':{'identifier':'recordingpoint_set'}},
            {'field':{'identifier':'device_set'}},
        ],
        'in_header':[
            {'field':{'identifier':'id'}},
            {'field':{'identifier':'model'}},
            {'field':{'identifier':'manufacturer'}},
            {'field':{'identifier':'material'}},
            {'field':{'identifier':'external_diameter'}},
            {'field':{'verbose_name':'recording points', 'identifier':'recordingpoint_set.count'}},
            {'field':{'verbose_name':'devices', 'identifier':'device_set.count'}},
        ],
        'width':"750px",
        'pagination':50
    }
}

solid = {
    'content_type':{
       'app_label':'electrophysiology',
       'model':'solidelectrode'
    },
    'position':1,
    'constraints':[
        solid_constraints
    ],
    'children':[
        {'entity':deepcopy(device)},
        {'entity':deepcopy(recording_point)}
    ]
}

equipment = {
    'content_type':{
       'app_label':'equipment',
       'model':'equipment'
    },
    'position':3,
    'constraints':[
        {
         'displayed_in_navigator':True,
         'display_subclasses':True,
         'display_base_class':False,
         'excluded_subclasses':[
             {'app_label':'electrophysiology', 'model':'electrode'},
             {'app_label':'electrophysiology', 'model':'discelectrode'},
             {'app_label':'electrophysiology', 'model':'hollowelectrode'},
             {'app_label':'electrophysiology', 'model':'multielectrode'},
         ]
        }
    ],
    'children':[
        {'entity':generic},
        {'entity':solid},
        {'entity':sharp},
        {'entity':patch},
    ]
}

setup_constraints = {
    'tableconstraint':{
        'displayed_in_navigator':False,
        'shunt':True,
        'form':'helmholtz.editor.forms.equipment.SetupForm',
        'in_header':[
            {'field':{'identifier':'id'}},
            {'field':{'identifier':'label'}},
            {'field':{'identifier':'place'}},
            {'field':{'identifier':'room'}},
            {'field':{'identifier':'experiment_set.count', 'verbose_name':'experiments'}},
        ],
        'width':"500px",
        'pagination':50
    }
}

setup = {
    'content_type':{
       'app_label':'equipment',
       'model':'setup'
    },
    'position':4,
    'constraints':[
        setup_constraints
    ],
#    'children':[
#        {'entity':subsystem},
#    ]
}

solid = {
    'content_type':{
       'app_label':'electrophysiology',
       'model':'solidelectrodeconfiguration'
    },
    'position':5,
    'constraints':[
        {
         'tableconstraint':{
             'displayed_in_navigator':False,
             'shunt':False,
             'form':'helmholtz.editor.forms.electrophysiology.SolidElectrodeConfigurationForm',
             'in_header':[
                 {'field':{'identifier':'id'}},
                 {'field':{'identifier':'label'}},
                 {'field':{'identifier':'resistance'}},
                 {'field':{'identifier':'amplification'}},
                 {'field':{'identifier':'filtering'}},
             ],
             'in_expansion':[
                 {'field':{'identifier':'notes'}},
             ],
             'width':"700px",
             'pagination':50
         }
        }
    ]
}

sharp = {
    'content_type':{
       'app_label':'electrophysiology',
       'model':'sharpelectrodeconfiguration'
    },
    'position':5,
    'constraints':[
        {
         'tableconstraint':{
             'displayed_in_navigator':False,
             'shunt':False,
             'form':'helmholtz.editor.forms.electrophysiology.SharpElectrodeConfigurationForm',
             'in_header':[
                 {'field':{'identifier':'id'}},
                 {'field':{'identifier':'label'}},
                 {'field':{'identifier':'solution'}},
                 {'field':{'identifier':'resistance'}},
                 {'field':{'identifier':'amplification'}},
                 {'field':{'identifier':'filtering'}},
             ],
             'in_expansion':[
                 {'field':{'identifier':'notes'}},
             ],
             'width':"800px",
             'pagination':50
             
         }
        }
    ]
}

patch = {
    'content_type':{
       'app_label':'electrophysiology',
       'model':'patchelectrodeconfiguration'
    },
    'position':5,
    'constraints':[
        {
         'tableconstraint':{
             'displayed_in_navigator':False,
             'shunt':False,
             'form':'helmholtz.editor.forms.electrophysiology.PatchElectrodeConfigurationForm',
             'in_header':[
                 {'field':{'identifier':'id'}},
                 {'field':{'identifier':'label'}},
                 {'field':{'identifier':'solution'}},
                 {'field':{'identifier':'resistance'}},
                 {'field':{'identifier':'seal_resistance'}},
                 {'field':{'identifier':'contact_configuration'}},
                 {'field':{'identifier':'amplification'}},
                 {'field':{'identifier':'filtering'}},
             ],
             'in_expansion':[
                 {'field':{'identifier':'notes'}},
             ],
             'width':"900px",
             'pagination':50
         }
        }
    ]
}

device_configuration = {
    'content_type':{
       'app_label':'equipment',
       'model':'deviceconfiguration'
    },
    'position':5,
    'constraints':[
        {
         'displayed_in_navigator':True,
         'display_subclasses':True,
         'display_base_class':False,
         'excluded_subclasses':[
             {'app_label':'optical_imaging', 'model':'cameraconfiguration'},
             {'app_label':'optical_imaging', 'model':'vsdoptical'},
             {'app_label':'optical_imaging', 'model':'intrinsicoptical'},
             {'app_label':'electrophysiology', 'model':'electrodeconfiguration'},
             {'app_label':'electrophysiology', 'model':'discelectrodeconfiguration'},
             {'app_label':'electrophysiology', 'model':'hollowelectrodeconfiguration'},
             {'app_label':'electrophysiology', 'model':'eeg'},
             {'app_label':'electrophysiology', 'model':'ekg'},
         ]
        }
    ],
    'children':[
        {'entity':solid},
        {'entity':sharp},
        {'entity':patch},
    ]
}
