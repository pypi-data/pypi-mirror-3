"""
This script will create a test database for Helmholtz and then populate it by
running a series of scripts.

The project directory may be specified on the command line. If no directory is
specified, a temporary directory will be generated.
"""

from __future__ import with_statement
import django.conf
from django.core import management
import os
import shutil

settings = django.conf.settings

def create_db(project_dir):
    test_settings = {
        'PROJECT_NAME': 'helmholtz_test',
        'DEBUG': True,
        'TEMPLATE_DEBUG': True,
        'DATABASE_ENGINE': 'sqlite3',
        'DATABASE_NAME': os.path.join(project_dir, "helmholtz_test.db"),
        'INSTALLED_APPS': (
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.sites',
            'django.contrib.admin',
            'tagging',
            'helmholtz.access_control',
            'helmholtz.people',
            'helmholtz.recording',
			'catdb.vision',
        )
    }
    settings.configure(**test_settings)
    management.setup_environ(settings)
    if not os.path.exists(project_dir):
        os.makedirs(project_dir)
    django_path = os.path.dirname(django.conf.__file__)
    for filename in "manage.py", "__init__.py":
        shutil.copy(os.path.join(django_path, "project_template", filename),
                    project_dir)
    with open(os.path.join(project_dir, "settings.py"), 'w') as f:
        for name, value in test_settings.items():
            if isinstance(value, basestring):
                f.write('%s = "%s"\n' % (name, value))
            else:
                f.write('%s = %s\n' % (name, value))
    if not os.path.exists(settings.DATABASE_NAME):
        management.call_command('syncdb')
    
def run_scenario(file_name):
    execfile(file_name)
    
    
if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        import tempfile
        project_dir = tempfile.mkdtemp()
    else:
        project_dir = sys.argv[1]
    
    create_db(project_dir)
    for filename in os.listdir("scenarios"):
        if filename[-3:] == ".py":
            run_scenario(os.path.join("scenarios", filename))
    
    print "Project created in", project_dir
    
    
    
