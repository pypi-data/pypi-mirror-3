#!/usr/bin/env python
import os

# load virtual environment before executing this file
if os.name == 'nt':
    activate_this = os.path.join(os.path.dirname(__file__), "..", "prod-env", 'Scripts','activate_this.py')
else:
    activate_this = os.path.join(os.path.dirname(__file__), "..", "prod-env", 'bin','activate_this.py')
execfile(activate_this, dict(__file__=activate_this))

import sys
path = os.path.join(os.path.dirname(__file__), "..")
if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.production")

# This application object is used by the development server
# as well as any WSGI server configured to use this file.
try:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
except ImportError:
    import django.core.handlers.wsgi
    application = django.core.handlers.wsgi.WSGIHandler()
