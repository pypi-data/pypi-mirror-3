#encoding:utf-8
electrical_channel_type_constraints = {
    'tableconstraint':{
        'form':'helmholtz.editor.forms.electrophysiology.ElectricalChannelTypeForm',
        'displayed_in_navigator':False,
        'shunt':True,
        'in_header':[
            {'field':{'identifier':'id'}},
            {'field':{'identifier':'name'}},
            {'field':{'identifier':'symbol'}},
        ],
        'width':'600px',
        'pagination':10
    }
}

electrical_channel_type = {
    'content_type':{
       'app_label':'electrophysiology',
       'model':'electricalchanneltype'
    },
    'position':1,
    'constraints':[
        electrical_channel_type_constraints
    ]
}

channel_type = {
    'content_type':{
       'app_label':'signals',
       'model':'channeltype'
    },
    'position':1,
    'constraints':[
        {
         'displayed_in_navigator':True,
         'display_subclasses':True,
         'display_base_class':False,
        }
    ],
    'children':[
        {'entity':electrical_channel_type},
    ]
}

electrical_recording_mode_constraints = {
    'tableconstraint':{
        'form':'helmholtz.editor.forms.electrophysiology.ElectricalRecordingModeForm',
        'displayed_in_navigator':False,
        'shunt':True,
        'in_header':[
            {'field':{'identifier':'id'}},
            {'field':{'identifier':'name'}},
        ],
        'width':'600px',
        'pagination':10
    }
}

electrical_recording_mode = {
    'content_type':{
       'app_label':'electrophysiology',
       'model':'electricalrecordingmode'
    },
    'position':1,
    'constraints':[
        electrical_recording_mode_constraints
    ]
}

recording_mode = {
    'content_type':{
       'app_label':'signals',
       'model':'recordingmode'
    },
    'position':2,
    'constraints':[
        {
         'displayed_in_navigator':True,
         'display_subclasses':True,
         'display_base_class':False,
         'excluded_subclasses':[
             {'app_label':'optical_imaging', 'model':'opticalrecordingmode'}
         ]
        }
    ],
    'children':[
        {'entity':electrical_recording_mode},
    ]
}

electrical_channel_constraints = {
    'tableconstraint':{
        'form':'helmholtz.editor.forms.electrophysiology.ElectricalChannelForm',
        'displayed_in_navigator':False,
        'shunt':True,
        'in_header':[
            {'field':{'identifier':'id'}},
            {'field':{'identifier':'number'}},
            {'field':{'identifier':'label'}},
            {'field':{'identifier':'type'}},
        ],
        'width':'650px',
        'pagination':10
    }
}

electrical_channel = {
    'content_type':{
       'app_label':'electrophysiology',
       'model':'electricalchannel'
    },
    'position':1,
    'constraints':[
        electrical_channel_constraints
    ]
}

channel = {
    'content_type':{
       'app_label':'signals',
       'model':'channel'
    },
    'position':3,
    'constraints':[
        {
         'displayed_in_navigator':True,
         'display_subclasses':True,
         'display_base_class':False,
        }
    ],
    'children':[
        {'entity':electrical_channel},
    ]
}

electrical_signal_constraints = {
    'tableconstraint':{
        'displayed_in_navigator':False,
        'shunt':True,
        'actions':[
            {'name':'A'},
            {'name':'M'},
            {'name':'D'},
        ],
        'form':'helmholtz.editor.forms.electrophysiology.ElectricalSignalForm',
        'in_header':[
            {'field':{'identifier':'id'}},
            {'field':{'identifier':'label'}},
            {'field':{'identifier':'file'}},
            {'field':{'identifier':'episode'}},
            {'field':{'identifier':'channel'}},
            {'field':{'identifier':'mode'}},
            {'field':{'identifier':'x_unit', 'verbose_name':'x unit'}},
            {'field':{'identifier':'y_unit', 'verbose_name':'y unit'}},
            {'field':{'identifier':'quality'}},
        ],
        'width':"800px",
        'pagination':50
    }
}

electrical_signal = {
    'content_type':{
       'app_label':'electrophysiology',
       'model':'electricalsignal'
    },
    'position':1,
    'constraints':[
        electrical_signal_constraints
    ]
}

signal = {
    'content_type':{
       'app_label':'signals',
       'model':'signal'
    },
    'position':4,
    'constraints':[
        {
         'display_base_class':False,
         'display_subclasses':True,
         'excluded_subclasses':[
             {'app_label':'optical_imaging', 'model':'opticalsignal'},
         ]
        }
    ],
    'children':[
        {'entity':electrical_signal},
    ]
}
