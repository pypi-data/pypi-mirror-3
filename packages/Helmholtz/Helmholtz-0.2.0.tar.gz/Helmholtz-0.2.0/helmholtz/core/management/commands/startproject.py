#!/usr/bin/env python
import os
import re
import sys
import shutil
import django
from django.core.management import execute_manager
from django.core.management.base import _make_writeable, CommandError, LabelCommand
from django.utils.importlib import import_module
from random import choice
import helmholtz

"""
This module provides commands that mimic django's ones in order to
create projects based on the Helmholtz's directory structure and files
stored into the helmholtz/conf/project_template.
"""

def copy_helper(style, app_or_project, name, directory, other_name='', media_url=None):
    """
    See django's copy_helper for more detail.
    Same function but replacing the hardcoded
    django path by the helmholtz one in order
    to have a custom settings.py with interesting
    parameters, see later how to do it cleaner.
    """
    # style -- A color style object (see django.core.management.color).
    # app_or_project -- The string 'app' or 'project'.
    # name -- The name of the application or project.
    # directory -- The directory to which the layout template should be copied.
    # other_name -- When copying an application layout, this should be the name
    #               of the project.
    other = {'project': 'app', 'app': 'project'}[app_or_project]
    if not re.search(r'^[_a-zA-Z]\w*$', name): # If it's not a valid directory name.
        # Provide a smart error message, depending on the error.
        if not re.search(r'^[_a-zA-Z]', name):
            message = 'make sure the name begins with a letter or underscore'
        else:
            message = 'use only numbers, letters and underscores'
        raise CommandError("%r is not a valid %s name. Please %s." % (name, app_or_project, message))
    top_dir = os.path.join(directory, name)
    try:
        os.mkdir(top_dir)
    except OSError, e:
        raise CommandError(e)

    # Determine where the app or project templates are. Use
    # helmholtz.__path__[0] because we don't know into which directory
    # django has been installed.
    template_dir = os.path.join(helmholtz.__path__[0], 'conf', '%s_template' % app_or_project)

    for d, subdirs, files in os.walk(template_dir):
        relative_dir = d[len(template_dir) + 1:].replace('%s_name' % app_or_project, name)
        if relative_dir:
            os.mkdir(os.path.join(top_dir, relative_dir))
        for subdir in subdirs[:]:
            if subdir.startswith('.'):
                subdirs.remove(subdir)
        for f in files:
            if f.endswith('.pyc') or f.endswith('.pyo')or f.endswith('.pyd') or f.endswith('.pyw') or f.endswith('.py.class'):
                # Ignore .pyc, .pyo, .py.class etc, as they cause various
                # breakages.
                continue
            path_old = os.path.join(d, f)
            path_new = os.path.join(top_dir, relative_dir, f.replace('%s_name' % app_or_project, name))
            if f.endswith('.py') :
                fp_old = open(path_old, 'r')
                fp_new = open(path_new, 'w')
                fp_new.write(fp_old.read().replace('{{ %s_name }}' % app_or_project, name).replace('{{ %s_name }}' % other, other_name))
                fp_old.close()
                fp_new.close()
            else :
                #avoid manipulating files 
                #that are not python files
                shutil.copy(path_old, path_new)
            try:
                shutil.copymode(path_old, path_new)
                _make_writeable(path_new)
            except OSError:
                sys.stderr.write(style.NOTICE("Notice: Couldn't set permission bits on %s. You're probably using an uncommon filesystem setup. No problem.\n" % path_new))

class Command(LabelCommand):
    help = "Creates a Helmholtz project directory structure for the given project name in the current directory."
    args = "[projectname]"
    label = 'project name'

    requires_model_validation = False
    can_import_settings = False

    def handle_label(self, project_name, **options):
        # Determine the project_name by looking at the name of the parent directory.
        directory = os.getcwd()

        # Check that the project_name cannot be imported.
        try:
            import_module(project_name)
        except ImportError:
            pass
        else:
            raise CommandError("%r conflicts with the name of an existing Python module and cannot be used as a project name. Please try another name." % project_name)

#        #reuse the copy_helper function but replacing the django path
#        #by the helmholtz one in order to have a custom settings.py 
#        #with interesting parameters, see later how to do it cleaner 
#        _file = open("%s/core/management/base.py" % (django.__path__[0]), 'r')
#        txt = '\n'.join(_file.readlines()[359:432])
#        pattern = """template_dir = os.path.join(django.__path__[0], 'conf', '%s_template' % app_or_project)"""
#        new_pattern = """template_dir = os.path.join(helmholtz.__path__[0], 'conf', '%s_template' % app_or_project)"""
#        modified_txt = txt.replace(pattern, new_pattern)
#        exec (modified_txt)
        copy_helper(self.style, 'project', project_name, directory)

        # Create a random SECRET_KEY hash, and put it in the main settings.
        main_settings_file = os.path.join(directory, project_name, 'settings.py')
        settings_contents = open(main_settings_file, 'r').read()
        fp = open(main_settings_file, 'w')
        secret_key = ''.join([choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)])
        settings_contents = re.sub(r"(?<=SECRET_KEY = ')'", secret_key + "'", settings_contents)
        fp.write(settings_contents)
        fp.close()
