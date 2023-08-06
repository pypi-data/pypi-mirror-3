#encoding:utf-8
from django.contrib import admin
from helmholtz.experiment.models import Experiment

experiment_admin = admin.site
experiment_admin.register(Experiment)