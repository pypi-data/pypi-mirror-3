import yaml
import os
import sys

def get_site_root(start_dir):
    testfile = os.path.join(start_dir, 'site.yaml')
    if os.path.isfile(testfile):
        return start_dir
    else:
        parent_dir = os.path.split(start_dir)[0]
        if parent_dir != start_dir:
            return get_site_root(parent_dir)
        else:
            return None

def get_role_list(local_root):
    """Return a list of the role names defined by yaml roles/*.yaml"""
    return [file[:-5] for file in os.listdir(os.path.join(local_root, 'roles')) if file.endswith('.yaml')]

def get_role():
    try:
        #if '-R rolename' found in sys.argv, use that
        return sys.argv[sys.argv.index('-R')+1]
    except:
        #role not found in sys.argv, try env var
        #return None if no role there either
        return os.environ.get('SILK_ROLE', None)

def get_role_config(role, root=None):
    if role:
        start = os.environ.get('SILK_START', os.getcwd())
        root = root or get_site_root(start)
        role_file = '%s/roles/%s.yaml' % (root, role)
        config =  yaml.safe_load(open(role_file, 'r').read())
        return config

def get_site_config(site_root):
    """Parses and returns site.yaml"""
    site_config_file = os.path.join(site_root, 'site.yaml')
    config = yaml.safe_load(open(site_config_file, 'r').read())
    return config

def get_config(site_root, role=None):
    """Returns merged site and role config.
    Falls back to site.yaml if no role given."""

    if role:
        config = get_site_config(site_root)
        config.update(get_role_config(role))
        return config
    else:
        return get_site_config(site_root)

