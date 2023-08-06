#!/usr/bin/env python

#from distutils.core import setup
from setuptools import setup, find_packages

setup(
    name = "Helmholtz",
    version = "0.2.0",
    packages = find_packages(), #['helmholtz', 'helmholtz.access_control', 'helmholtz.access_control.templatetags', 'helmholtz.annotation',
                #'helmholtz.chemistry', 'helmholtz.core', 'helmholtz.core.management.commands',
                #'helmholtz.drug_applications', 'helmholtz.editor', 'helmholtz.editor.forms', 'helmholtz.electrophysiology',
                #'helmholtz.electricalstimulation',
                #'helmholtz.equipment', 'helmholtz.experiment', 'helmholtz.histochemistry',
                #'helmholtz.location',
                #'helmholtz.measurements', 'helmholtz.neuralstructures', 'helmholtz.optical_imaging',
                #'helmholtz.people', 'helmholtz.preparations', 'helmholtz.recording',
                #'helmholtz.signals', 'helmholtz.species', 'helmholtz.stimulation',
                #'helmholtz.storage', 'helmholtz.units', 'helmholtz.waveforms'],
    #package_data = {'helmholtz': ['people/fixtures/*.json', 'templates/*.html',
    #                              'media/css/helmholtz.css'],
    #                'helmholtz.access_control': ['templates/*.html', 'templates/registration/*.html']},
    author = "Neuroinformatics research group, UNIC, CNRS",
    author_email = "andrew.davison@unic.cnrs-gif.fr",
    description = "A framework for creating neuroscience databases",
    license = "CeCILL http://www.cecill.info",
    keywords = "neuroscience database Django metadata",
    url = "http://www.dbunic.cnrs-gif.fr/helmholtz/",
    classifiers = ['Development Status :: 3 - Alpha',
                   'Environment :: Web Environment',
                   'Intended Audience :: Science/Research',
                   'License :: Other/Proprietary License',
                   'Natural Language :: English',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Framework :: Django',
                   'Topic :: Scientific/Engineering',
                   'Topic :: Database'],
)

