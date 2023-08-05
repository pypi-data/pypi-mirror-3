import django.core.handlers.wsgi
import os
import sys

from app_container import get_site_root, get_site_config


# This file is a shim to expose a Django project as a WSGI application that can
# be run by gunicorn or other things that speak WSGI.  It does a little magic
# and makes some assumptions.  It assumes that there's only one Django project
# in your site root, and that the cwd is somewhere inside your site root.

here = os.getcwd()
root = get_site_root(here)
sys.path.insert(0, root)
site_config = get_site_config(root)
os.environ['DJANGO_SETTINGS_MODULE'] = site_config['django_settings_module']

def is_django_project(folder):
    """Determine whether a folder is a Django project by looking for the
    presence of settings.py, manage.py, and __init__.py"""
    testfiles = ('settings.py', 'manage.py', '__init__.py')
    existences = [os.path.isfile(os.path.join(folder, x)) for x in testfiles]
    return reduce(lambda x, y: x and y, existences)

# Find the first subdirectory in the site that qualifies as a django project,
# and use that as the project path.
for d in [os.path.join(root, x) for x in os.listdir(root)]:
    if is_django_project(d):
        project_path = d
        #add project folder to sys.path
        sys.path.insert(0, d)
        continue

#change dir into the project so that TEMPLATE_DIRS will work
os.chdir(project_path)

app = django.core.handlers.wsgi.WSGIHandler()
