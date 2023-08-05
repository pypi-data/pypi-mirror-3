import os
from lib import *

# set up config dictionary
start = os.environ.get('SILK_START', os.getcwd())
root = get_site_root(start)
_site_config = get_config(root, get_role())
if 'app_config' in _site_config:
    config = _site_config['app_config']
else:
    config = {}
