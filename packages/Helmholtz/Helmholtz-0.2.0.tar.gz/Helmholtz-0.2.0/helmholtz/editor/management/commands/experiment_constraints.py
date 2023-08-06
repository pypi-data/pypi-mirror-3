from django.conf import settings
from copy import deepcopy

researcher = {
    'content_type':{
       'app_label':'people',
       'model':'researcher'
    },
    'position':1,
    'constraints':[
        {
         'displayed_in_navigator':False,
         'shunt':True,
         'form':'helmholtz.editor.forms.people.ResearcherForm',
        }
    ],
}

area_centralis_constraints = {
    'tableconstraint':{
        'displayed_in_navigator':False,
        'shunt':True,
        'form':'helmholtz.editor.forms.preparations.AreaCentralisForm',
        'actions':[
            {'name':'A'},
            {'name':'M'},
            {'name':'D'},
        ],
        'in_header':[
            {'field':{'identifier':'id'}},
            {'field':{'identifier':'left_x'}},
            {'field':{'identifier':'left_y'}},
            {'field':{'identifier':'right_x'}},
            {'field':{'identifier':'right_y'}},
        ],
        'width':"500px",
        'max_objects':1,
        'pagination':1
    }
}

area_centralis = {
    'content_type':{
       'app_label':'preparations',
       'model':'areacentralis'
    },
    'position':1,
    'constraints':[
        area_centralis_constraints
    ],
}

eye_correction_constraints = {
    'tableconstraint':{
        'displayed_in_navigator':False,
        'shunt':True,
        'actions':[
            {'name':'A'},
            {'name':'M'},
            {'name':'D'},
        ],
        'form':'helmholtz.editor.forms.preparations.EyeCorrectionForm',
        'in_header':[
            {'field':{'identifier':'id'}},
            {'field':{'identifier':'left'}},
            {'field':{'identifier':'right'}},
        ],
        'width':"300px",
        'max_objects':1,
        'pagination':1
    }
}

eye_correction = {
    'content_type':{
       'app_label':'preparations',
       'model':'eyecorrection'
    },
    'position':1,
    'constraints':[
        eye_correction_constraints
    ],
}

preparation_information = {
    'content_type':{
       'app_label':'preparations',
       'model':'preparationinformation'
    },
    'position':1,
    'constraints':[
        {
            'displayed_in_navigator':False,
            'display_subclasses':True,
            'display_base_class':False,
        }
    ],
    'children':[
        {'entity':area_centralis},
        {'entity':eye_correction},
    ]
}

bool_measurement = {
    'content_type':{
       'app_label':'measurements',
       'model':'boolmeasurement'
    },
    'position':1,
    'constraints':[
        {'form':'helmholtz.editor.forms.measurements.BoolMeasurementForm', }
    ],
}

integer_measurement = {
    'content_type':{
       'app_label':'measurements',
       'model':'integermeasurement'
    },
    'position':1,
    'constraints':[
        {'form':'helmholtz.editor.forms.measurements.IntegerMeasurementForm', }
    ],
}

float_measurement = {
    'content_type':{
       'app_label':'measurements',
       'model':'floatmeasurement'
    },
    'position':1,
    'constraints':[
        {'form':'helmholtz.editor.forms.measurements.FloatMeasurementForm', }
    ],
}

string_measurement = {
    'content_type':{
       'app_label':'measurements',
       'model':'stringmeasurement'
    },
    'position':1,
    'constraints':[
        {'form':'helmholtz.editor.forms.measurements.StringMeasurementForm'}
    ],
}

measurements = {
    'content_type':{
       'app_label':'measurements',
       'model':'genericmeasurement'
    },
    'position':1,
    'constraints':[
        {
        'tableconstraint':{
            'displayed_in_navigator':False,
            'shunt':True,
            'actions':[
                {'name':'A'},
                {'name':'M'},
                {'name':'D'},
            ],
            'in_header':[
                {'field':{'identifier':'id'}},
                {'field':{'identifier':'timestamp'}},
                {'field':{'identifier':'parameter'}},
                {'field':{'identifier':'cast.value', 'verbose_name':'value'}},
                {'field':{'identifier':'unit'}},
            ],
            'width':"500px",
            'pagination':10
        }
       }
    ],
    'children':[
        {'entity':float_measurement},
        {'entity':integer_measurement},
        {'entity':bool_measurement},
        {'entity':string_measurement},
    ]
}

preparation_constraints = {
    'displayed_in_navigator':False,
    'shunt':False,
    'form':'helmholtz.editor.forms.preparations.PreparationForm',
    'in_expansion':[
        {'field':{'identifier':'animal'}},
        {'field':{'identifier':'preparationinformation_set'}},
        {'field':{'identifier':'observations'}},
        {'field':{'identifier':'id'}},
        {'field':{'identifier':'protocol'}},
    ],
}

preparation = {
    'content_type':{
       'app_label':'preparations',
       'model':'preparation'
    },
    'position':1,
    'constraints':[
        preparation_constraints
    ],
    'children':[
        {'entity':preparation_information},
        {'entity':deepcopy(measurements)},
    ]
}

injection_constraints = {
    'tableconstraint':{
        'displayed_in_navigator':False,
        'shunt':False,
        'actions':[
            {'name':'A'},
            {'name':'M'},
            {'name':'D'},
        ],
        'form':'helmholtz.editor.forms.drug_applications.DiscreteDrugApplicationForm',
        'in_header':[
            {'field':{'identifier':'id'}},
            {'field':{'identifier':'solution'}},
            {'field':{'identifier':'volume'}},
            {'field':{'identifier':'time'}},
        ],
        'in_expansion':[
            {'field':{'identifier':'notes'}},
        ],
        'width':"500px",
        'pagination':10
    }
}

injection = {
    'content_type':{
       'app_label':'drug_applications',
       'model':'discretedrugapplication'
    },
    'position':1,
    'constraints':[
        injection_constraints
    ],
}

perfusion_constraints = {
    'tableconstraint':{
        'displayed_in_navigator':False,
        'shunt':False,
        'actions':[
            {'name':'A'},
            {'name':'M'},
            {'name':'D'},
        ],
        'form':'helmholtz.editor.forms.drug_applications.ContinuousDrugApplicationForm',
        'in_header':[
            {'field':{'identifier':'id'}},
            {'field':{'identifier':'solution'}},
            {'field':{'identifier':'start'}},
            {'field':{'identifier':'end'}},
            {'field':{'identifier':'rate'}},
        ],
        'in_expansion':[
            {'field':{'identifier':'notes'}},
        ],
        'width':"650px",
        'pagination':10
    }
}

perfusion = {
    'content_type':{
       'app_label':'drug_applications',
       'model':'continuousdrugapplication'
    },
    'position':1,
    'constraints':[
        perfusion_constraints
    ],
}

drug_application = {
    'content_type':{
       'app_label':'drug_applications',
       'model':'drugapplication'
    },
    'position':1,
    'constraints':[
        {
            'displayed_in_navigator':False,
            'display_subclasses':True,
            'display_base_class':False,
        }
    ],
    'children':[
        {'entity':injection},
        {'entity':perfusion},
    ]
}

#screen = {
#    'content_type':{
#       'app_label':'visualstimulation',
#       'model':'screenphotometry'
#    },
#    'position':1,
#    'constraints':[
#        {
#         'form':'helmholtz.editor.forms.stimuli.ScreenPhotometryForm',
#         'in_expansion':[
#             {'field':{'identifier':'id'}},
#             {'field':{'identifier':'luminance_high'}},
#             {'field':{'identifier':'luminance_low'}},
#             {'field':{'identifier':'luminance_background'}},
#             {'field':{'identifier':'gray_levels'}},
#         ]
#        }
#    ]
#}
#
#screen_area = {
#    'content_type':{
#       'app_label':'visualstimulation',
#       'model':'screenarea'
#    },
#    'position':1,
#    'constraints':[
#        {
#         'form':'helmholtz.editor.forms.stimuli.ScreenAreaForm',
#         'in_expansion':[
#             {'field':{'identifier':'id'}},
#             {'field':{'identifier':'position_x'}},
#             {'field':{'identifier':'position_y'}},
#             {'field':{'identifier':'width'}},
#             {'field':{'identifier':'length'}},
#             {'field':{'identifier':'orientation'}},
#         ]
#        }
#    ]
#}
#
#bar = {
#    'content_type':{
#       'app_label':'visualstimulation',
#       'model':'bar'
#    },
#    'position':1,
#    'constraints':[
#        {
#         'form':'helmholtz.editor.forms.stimuli.BarForm',
#         'in_expansion':[
#             {'field':{'identifier':'id'}},
#             {'field':{'identifier':'excursion'}},
#             {'field':{'identifier':'speed'}},
#             {'field':{'identifier':'length'}},
#             {'field':{'identifier':'width'}}
#         ]
#        }
#    ]
#}
#
#grid = {
#    'content_type':{
#       'app_label':'vision',
#       'model':'grid'
#    },
#    'position':1,
#    'constraints':[
#        {
#         'form':'helmholtz.editor.forms.stimuli.GridForm',
#         'in_expansion':[
#             {'field':{'identifier':'id'}},
#             {'field':{'identifier':'n_div_x'}},
#             {'field':{'identifier':'n_div_y'}},
#             {'field':{'identifier':'expansion'}},
#             {'field':{'identifier':'scotoma'}},
#             {'field':{'identifier':'type'}}
#         ]
#        }
#    ]
#}

flashbar_constraints = {
    'displayed_in_navigator':False,
    'shunt':False,
    'form':'helmholtz.editor.forms.stimuli.FlashBarForm',
    'in_expansion':[
        {'field':{'identifier':'id'}},
        {'field':{'identifier':'stimulus_generator'}},
        {'field':{'identifier':'driven_eye'}},
        {'field':{'identifier':'viewing_distance'}},
        {'field':{'identifier':'number_of_repetitions'}},
        {'field':{'identifier':'number_of_orientations'}},
        {'field':{'identifier':'orientations'}},
        {'field':{'identifier':'title'}},
        # {'field':{'identifier':'stimulation_area'}},
        # {'field':{'identifier':'excursion'}},
        {'field':{'identifier':'dt_on'}},
    ]
}

flashbar = {
    'content_type':{
       'app_label':'vision',
       'model':'flashbar'
    },
    'position':1,
    'constraints':[
        flashbar_constraints
    ],
    'children':[
        # {'entity':deepcopy(screen_area)},
    ]
}

movingbar_constraints = {
    'displayed_in_navigator':False,
    'shunt':False,
    'form':'helmholtz.editor.forms.stimuli.MovingBarForm',
    'in_expansion':[
        {'field':{'identifier':'id'}},
        {'field':{'identifier':'stimulus_generator'}},
        {'field':{'identifier':'driven_eye'}},
        {'field':{'identifier':'viewing_distance'}},
        {'field':{'identifier':'number_of_repetitions'}},
        {'field':{'identifier':'number_of_orientations'}},
        {'field':{'identifier':'orientations'}},
        {'field':{'identifier':'title'}},
        # {'field':{'identifier':'stimulation_area'}},
        # {'field':{'identifier':'bar'}},
    ]
}

movingbar = {
    'content_type':{
       'app_label':'vision',
       'model':'movingbar'
    },
    'position':1,
    'constraints':[
        movingbar_constraints
    ],
    'children':[
        # {'entity':deepcopy(screen_area)},
        # {'entity':deepcopy(bar)},
    ]
}


densenoise_constraints = {
    'displayed_in_navigator':False,
    'shunt':False,
    'form':'helmholtz.editor.forms.stimuli.DenseNoiseForm',
    'in_expansion':[
        {'field':{'identifier':'id'}},
        {'field':{'identifier':'stimulus_generator'}},
        {'field':{'identifier':'driven_eye'}},
        {'field':{'identifier':'viewing_distance'}},
        {'field':{'identifier':'type'}},
        {'field':{'identifier':'number_of_sequences'}},
        {'field':{'identifier':'stimulus_duration'}},
        {'field':{'identifier':'pretrigger_duration'}},
        {'field':{'identifier':'seed'}},
        {'field':{'identifier':'dt_on'}},
        {'field':{'identifier':'dt_off'}},
        {'field':{'identifier':'title'}},
        # {'field':{'identifier':'screen'}},
        # {'field':{'identifier':'stimulation_area'}},
        # {'field':{'identifier':'grid'}},
    ]
}

densenoise = {
    'content_type':{
       'app_label':'vision',
       'model':'densenoise'
    },
    'position':1,
    'constraints':[
        densenoise_constraints
    ],
    'children':[
        # {'entity':deepcopy(screen)},
        # {'entity':deepcopy(screen_area)},
        # {'entity':deepcopy(grid)},
    ]
    
}

sparsenoise_constraints = {
    'displayed_in_navigator':False,
    'shunt':False,
    'form':'helmholtz.editor.forms.stimuli.RevCorForm',
    'in_expansion':[
        {'field':{'identifier':'id'}},
        {'field':{'identifier':'stimulus_generator'}},
        {'field':{'identifier':'driven_eye'}},
        {'field':{'identifier':'viewing_distance'}},
        {'field':{'identifier':'seed'}},
        {'field':{'identifier':'dt_on'}},
        {'field':{'identifier':'dt_off'}},
        {'field':{'identifier':'title'}},
        # {'field':{'identifier':'screen'}},
        # {'field':{'identifier':'stimulation_area'}},
        # {'field':{'identifier':'grid'}},
    ]
}

sparsenoise = {
    'content_type':{
       'app_label':'vision',
       'model':'revcor'
    },
    'position':1,
    'constraints':[
        sparsenoise_constraints
    ],
    'children':[
        # {'entity':deepcopy(screen)},
        # {'entity':deepcopy(screen_area)},
        # {'entity':deepcopy(grid)},
    ]
}

stimulus_constraints = {
    'displayed_in_navigator':False,
    'shunt':False,
    #'form':'helmholtz.editor.forms.stimuli.StimulusForm',
    'display_subclasses':True,
    'in_expansion':[
        
    ],
    'excluded_subclasses':[
        {'app_label':'visualstimulation', 'model':'visualstimulus'},
        {'app_label':'stimulation', 'model':'nullstimulus'},
        {'app_label':'vision', 'model':'centersurroundstimulus'},
        {'app_label':'vision', 'model':'sparsenoisesurround'},
        {'app_label':'vision', 'model':'densenoisesurround'},
        {'app_label':'vision', 'model':'gratingsurround'},
        {'app_label':'vision', 'model':'gratingcenter'},
        {'app_label':'vision', 'model':'naturenoisenetwork'},
        {'app_label':'electricalstimulation', 'model':'electricalstimulus'},
        {'app_label':'vision', 'model':'gaby'},
        {'app_label':'vision', 'model':'gabornoise'},
        {'app_label':'vision', 'model':'spatialfrequencyandphase'},
        {'app_label':'vision', 'model':'temporalfrequency'},
        {'app_label':'vision', 'model':'evoquedresponse'},
        {'app_label':'vision', 'model':'thetaburst'},
        {'app_label':'vision', 'model':'orientation'},
        {'app_label':'vision', 'model':'saccadeflik'},
        {'app_label':'vision', 'model':'pairinggabor'},
        {'app_label':'vision', 'model':'pairingposition'},
        {'app_label':'vision', 'model':'hybrid'},
        {'app_label':'vision', 'model':'tuning'},
        {'app_label':'vision', 'model':'ivcurve'},
        {'app_label':'vision', 'model':'lgnstimulation'},
        {'app_label':'vision', 'model':'currentstepstimulus'},
        {'app_label':'vision', 'model':'saccademove'},
        {'app_label':'vision', 'model':'hexagabor'},
        
    ]
}

stimulus = {
    'content_type':{
       'app_label':'stimulation',
       'model':'stimulus'
    },
    'position':1,
    'constraints':[
        stimulus_constraints
    ],
    'children':[
        {'entity':sparsenoise},
        {'entity':densenoise},
        {'entity':movingbar},
        {'entity':flashbar}
    ]
}

preparation_constraints = {
    'displayed_in_navigator':False,
    'shunt':False,
    'form':'helmholtz.editor.forms.preparations.PreparationForm',
    'in_expansion':[
        {'field':{'identifier':'animal'}},
        {'field':{'identifier':'preparationinformation_set'}},
        {'field':{'identifier':'id'}},
        {'field':{'identifier':'protocol'}},
    ],
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
        'form':'helmholtz.editor.forms.electrophysiology.ElectricalSignalFromProtocolForm',
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
    'position':1,
    'constraints':[
        {
         'displayed_in_navigator':False,
         'display_base_class':False,
         'display_subclasses':True,
        }
    ],
    'children':[
        {'entity':electrical_signal},
        #{'entity':position},
    ]
}

protocol_rec_constraints = {
    'tableconstraint':{
        'displayed_in_navigator':False,
        'shunt':False,
        'actions':[
            {'name':'A'},
            {'name':'M'},
            {'name':'D'},
        ],
        'form':'helmholtz.editor.forms.recording.ProtocolRecordingForm',
        'in_header':[
            {'field':{'identifier':'id'}},
            {'field':{'identifier':'label'}},
            {'field':{'identifier':'type', 'verbose_name':'type'}},
            {'field':{'identifier':'signal_set.count', 'verbose_name':'signals'}},
        ],
        'in_expansion':[
            {'field':{'identifier':'measurements'}},
            {'field':{'identifier':'stimulus'}},
            {'field':{'identifier':'signal_set'}},
            {'field':{'identifier':'notes'}},
        ],
        'width':"800px",
        'pagination':25
    }
}

protocol_rec = {
    'content_type':{
       'app_label':'recording',
       'model':'protocolrecording'
    },
    'position':1,
    'constraints':[
        protocol_rec_constraints
    ],
    'children':[
        {'entity':deepcopy(measurements)},
        #{'entity':stimulus},
        {'entity':signal}
    ]
}

sharp = {
    'content_type':{
       'app_label':'electrophysiology',
       'model':'sharpelectrodeconfiguration'
    },
    'constraints':[
        {
         'actions':[
             {'name':'A'},
             {'name':'D'},
             {'name':'M'},
             {'name':'L'},
             {'name':'U'},
         ],
         'displayed_in_navigator':False,
         'shunt':False,
         'form':'helmholtz.editor.forms.electrophysiology.SharpElectrodeConfigurationForm',
         'in_expansion':[
             {'field':{'identifier':'id'}},
             {'field':{'identifier':'label'}},
             {'field':{'identifier':'resistance'}},
             {'field':{'identifier':'amplification'}},
             {'field':{'identifier':'filtering'}},
             {'field':{'identifier':'solution'}},
             {'field':{'identifier':'notes'}}
         ]
        }
    ]
}

patch = {
    'content_type':{
       'app_label':'electrophysiology',
       'model':'patchelectrodeconfiguration'
    },
    'constraints':[
        {
         'actions':[
             {'name':'A'},
             {'name':'D'},
             {'name':'M'},
             {'name':'L'},
             {'name':'U'},
         ],
         'displayed_in_navigator':False,
         'shunt':False,
         'form':'helmholtz.editor.forms.electrophysiology.PatchElectrodeConfigurationForm',
         'in_expansion':[
             {'field':{'identifier':'id'}},
             {'field':{'identifier':'label'}},
             {'field':{'identifier':'resistance'}},
             {'field':{'identifier':'seal_resistance'}},
             {'field':{'identifier':'contact_configuration'}},
             {'field':{'identifier':'amplification'}},
             {'field':{'identifier':'filtering'}},
             {'field':{'identifier':'solution'}},
             {'field':{'identifier':'notes'}}
         ]
        }
    ]
}

solid = {
    'content_type':{
       'app_label':'electrophysiology',
       'model':'solidelectrodeconfiguration'
    },
    'constraints':[
        {
         'actions':[
             {'name':'A'},
             {'name':'D'},
             {'name':'M'},
             {'name':'L'},
             {'name':'U'},
         ],
         'displayed_in_navigator':False,
         'shunt':False,
         'form':'helmholtz.editor.forms.electrophysiology.SolidElectrodeConfigurationForm',
         'in_expansion':[
             {'field':{'identifier':'id'}},
             {'field':{'identifier':'label'}},
             {'field':{'identifier':'resistance'}},
             {'field':{'identifier':'amplification'}},
             {'field':{'identifier':'filtering'}},
             {'field':{'identifier':'notes'}}
         ]
        }
    ]
}

device_configuration = {
    'content_type':{
       'app_label':'equipment',
       'model':'deviceconfiguration'
    },
    'constraints':[
        {
         'actions':[
             {'name':'A'},
             {'name':'M'},
             {'name':'L'}
         ],
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
        {'entity':patch}
    ]
}

position = {
    'content_type':{
       'app_label':'location',
       'model':'position'
    },
    'constraints':[
        {
         'form':'helmholtz.editor.forms.location.PositionForm',
         'shunt':False,
         'in_expansion':[
             {'field':{'identifier':'id'}},
             {'field':{'identifier':'label'}},
             {'field':{'identifier':'brain_region'}},
             {'field':{'identifier':'apparatus'}},
             {'field':{'identifier':'ap', 'verbose_name':'anterior-posterior axis'}},
             {'field':{'identifier':'dv', 'verbose_name':'dorsal-ventral axis'}},
             {'field':{'identifier':'lt', 'verbose_name':'lateral axis'}},
             {'field':{'identifier':'depth'}},
             {'field':{'identifier':'intra'}},
         ]
        } 
    ]
}

base_configuration_constraints = {
    'tableconstraint':{
        'displayed_in_navigator':False,
        'shunt':False,
        'actions':[
            {'name':'A'},
            {'name':'M'},
            {'name':'D'},
        ],
        'form':'helmholtz.editor.forms.recording.RecordingConfigurationForm',
        'in_header':[
            {'field':{'identifier':'id'}},
            {'field':{'identifier':'label'}},
            #{'field':{'identifier':'signal_set.count', 'verbose_name':'signals'}},
        ],
        'in_expansion':[
            {'field':{'identifier':'configuration'}},
            {'field':{'identifier':'position'}},
            {'field':{'identifier':'measurements'}},
            #{'field':{'identifier':'signal_set'}},
        ],
        'width':"900px",
        'pagination':25
    }
}

base_configuration = {
    'content_type':{
       'app_label':'recording',
       'model':'recordingconfiguration'
    },
    'constraints':[
        base_configuration_constraints
    ],
    'children':[
        {'entity':deepcopy(device_configuration)},
        {'entity':deepcopy(position)},
        {'entity':deepcopy(measurements)},
    ]
}

electrode_configuration_constraints = {
    'tableconstraint':{
        'displayed_in_navigator':False,
        'shunt':False,
        'actions':[
            {'name':'A'},
            {'name':'M'},
            {'name':'D'},
        ],
        'form':'helmholtz.editor.forms.electrophysiology.ElectrodeRecordingConfigurationForm',
        'in_header':[
            {'field':{'identifier':'id'}},
            {'field':{'identifier':'label'}},
            {'field':{'identifier':'device'}},
            #{'field':{'identifier':'recording_point'}},
            #{'field':{'identifier':'signal_set.count', 'verbose_name':'signals'}},
        ],
        'in_expansion':[
            {'field':{'identifier':'configuration'}},
            {'field':{'identifier':'position'}},
            {'field':{'identifier':'measurements'}},
            #{'field':{'identifier':'signal_set'}},
        ],
        'width':"900px",
        'pagination':25
    }
}

electrode_configuration = {
    'content_type':{
       'app_label':'electrophysiology',
       'model':'electroderecordingconfiguration'
    },
    'constraints':[
        electrode_configuration_constraints        
    ],
    'children':[
        {'entity':deepcopy(device_configuration)},
        {'entity':deepcopy(position)},
        {'entity':deepcopy(measurements)},
    ]
}

configuration = {
    'content_type':{
       'app_label':'recording',
       'model':'recordingconfiguration'
    },
    'position':1,
    'constraints':[
        {
         'displayed_in_navigator':False,
         'display_subclasses':True,
         'display_base_class':True,
        } 
    ],
    'children':[
        {'entity':base_configuration},
        {'entity':electrode_configuration},
        #{'entity':position},
    ]
}

block_constraints = {
    'tableconstraint':{
        'displayed_in_navigator':False,
        'shunt':False,
        'actions':[
            {'name':'A'},
            {'name':'M'},
            {'name':'D'},
        ],
        'form':'helmholtz.editor.forms.recording.RecordingBlockForm',
        'in_header':[
            {'field':{'identifier':'id'}},
            {'field':{'identifier':'label'}},
            {'field':{'identifier':'start'}},
            {'field':{'identifier':'end'}},
            {'field':{'identifier':'protocolrecording_set.count', 'verbose_name':'protocols'}},
            {'field':{'identifier':'recordingconfiguration_set.count', 'verbose_name':'configurations'}},
        ],
        'in_expansion':[
            {'field':{'identifier':'recordingconfiguration_set'}},
            {'field':{'identifier':'protocolrecording_set'}},
            {'field':{'identifier':'notes'}},
        ],
        'width':"1000px",
        'pagination':25
    }
}

block = {
    'content_type':{
       'app_label':'recording',
       'model':'recordingblock'
    },
    'position':1,
    'constraints':[
        block_constraints
    ],
    'children':[
        {'entity':protocol_rec},
        {'entity':configuration},
    ]
}

experiment_constraints = {
    'tableconstraint':{
        'displayed_in_navigator':False,
        'form':'helmholtz.editor.forms.experiment.ExperimentForm',
        'in_header':[
            {'field':{'identifier':'id'}},
            {'field':{'identifier':'label'}},
            {'field':{'identifier':'setup'}},
            {'field':{'identifier':'start'}},
            {'field':{'identifier':'end'}},
            {'field':{'identifier':'preparation'}},
            {'field':{'verbose_name':'researchers', 'identifier':'researchers.count'}},
            {'field':{'verbose_name':'recording blocks', 'identifier':'recordingblock_set.count'}},
            {'field':{'verbose_name':'drug applications', 'identifier':'drugapplication_set.count'}},
        ],
        'in_expansion':[
            {'field':{'identifier':'preparation'}},
            {'field':{'identifier':'researchers'}},
            {'field':{'identifier':'drugapplication_set'}},
            {'field':{'identifier':'recordingblock_set'}},
            {'field':{'identifier':'notes'}}
        ],
        'width':"1100px",
        'pagination':50
    }
}

experiment = {
    'content_type':{
       'app_label':'experiment',
       'model':'experiment'
    },
    'position':1,
    'constraints':[
        experiment_constraints
    ],
    'children':[
        {'entity':researcher},
        {'entity':preparation},
        {'entity':drug_application},
        {'entity':block},
    ]
}
