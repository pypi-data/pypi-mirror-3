#!/usr/bin/env python
import os

# load virtual environment from devel-env before executing this file
if os.name == 'nt':
    activate_this = os.path.join(os.path.dirname(__file__), "..", "devel-env", 'Scripts','activate_this.py')
else:
    activate_this = os.path.join(os.path.dirname(__file__), "..", "devel-env", 'bin','activate_this.py')
execfile(activate_this, dict(__file__=activate_this))

from django.core.management import execute_manager
import imp


is_prod = os.path.exists(os.path.join(os.path.dirname(__file__), 'production.py'))

try:
    if is_prod:
        imp.find_module('production')
    else:
        imp.find_module('development')
except ImportError:
    import sys
    sys.stderr.write("Error: Can't find the file 'development.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n" % __file__)
    sys.exit(1)

if is_prod:
    import production as settings
else:
    import development as settings

if __name__ == "__main__":
    execute_manager(settings)
