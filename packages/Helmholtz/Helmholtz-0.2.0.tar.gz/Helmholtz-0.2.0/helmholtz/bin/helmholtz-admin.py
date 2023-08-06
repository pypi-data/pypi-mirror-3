#!/usr/bin/env python
from django.core import management
from django.core.management import _commands, find_commands
import helmholtz

"""
This module provides a way to override the django-admin in order
to create projects based on the Helmholtz's directory structure. 
"""

if __name__ == "__main__":
    # same as django-admin but init ``_commands`` global
    # parameter with commands in helmholtz.core
    path = "%s/core/management" % helmholtz.__path__[0] 
    management._commands = dict([(name, 'helmholtz.core') for name in find_commands(path)])
    management.execute_from_command_line()
