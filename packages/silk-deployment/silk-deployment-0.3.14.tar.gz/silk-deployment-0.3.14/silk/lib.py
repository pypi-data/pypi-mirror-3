import copy
import os
import pkg_resources
import subprocess
import sys
import time
import shutil
import hashlib
from signal import SIGTERM, SIGINT

import app_container

from app_container import *


# Format for the 'bind' string we'll be making later, sticking the site name +
# timestamp in the wildcard part.  Used here for generating the gunicorn cmd,
# and in the fabfile for plugging into the nginx config.
GUNICORN_BIND_PATTERN = 'unix:/tmp/%s.sock'

def get_gunicorn_cmd(site_env, bin_dir=''):
    """Given a copy of Fabric's state in site_env, configure and return the
    gunicorn cmd line needed to run the site"""
    site_config = site_env['config']

    GUNICORN_DEFAULTS = {
        'workers': 1,
        'log-level': 'info',
        'name': 'gunicorn',
        'debug': 'false',
    }

    # Make a copy here because we're going to be modifying this dict, and we
    # don't want to mess it up for later functions, or later runs of this
    # function if we're going to deploy to more than one host.
    gconfig = copy.copy(site_config.get('gunicorn', GUNICORN_DEFAULTS))

    # Default to using a unix socket for nginx->gunicorn
    if 'deployment' in site_env:
        default_bind = GUNICORN_BIND_PATTERN % site_env.deployment
        # Default to using the site name and timestamp in the procname
        gconfig['name'] = site_env['deployment']
    else:
        default_bind = 'localhost:8000'
        gconfig['name'] = site_config['site']

    gconfig['bind'] = gconfig.get('bind', default_bind)


    debug = gconfig.pop('debug', None)
    options = ' '.join(['--%s %s' % (x, y) for x, y in gconfig.iteritems()])
    if debug:
        options += ' --debug'
    gconfig['options'] = options
    gconfig['bin_dir'] = bin_dir
    gconfig.update(site_config)
    cmd = 'gunicorn %(options)s %(wsgi_app)s' % gconfig
    if bin_dir:
        cmd = '%s/%s' % (bin_dir, cmd)
    return cmd

def get_root(start_dir):
    testfile = os.path.join(start_dir, 'site.yaml')
    if os.path.isfile(testfile):
        return start_dir
    else:
        parent_dir = os.path.split(start_dir)[0]
        if parent_dir != start_dir:
            return get_root(parent_dir)
        else:
            return None

def get_template_path(template, root=None):
    """
    Returns path of template from site conf_templates dir, if found there, else
    returns template path from silk's conf_templates dir.
    """
    if root:
        localpath=os.path.join(root, 'conf_templates', template)
        if os.path.isfile(localpath):
            return localpath
    pkgpath=pkg_resources.resource_filename('silk', 'conf_templates/%s' % template)
    if os.path.isfile(pkgpath):
        return pkgpath
    else:
        raise Exception("Template not found: %s" % template)

def get_rendered_template(template_name, context):
    """
    Returns text of named template, with keyword substitutions pulled from
    'context'
    """
    template_path = get_template_path(template_name)
    txt = open(template_path, 'r').read()
    return txt % context

def _run(args, kill_signal, cwd=os.getcwd(), env={}):
    env.update(os.environ)
    proc = subprocess.Popen(args, cwd=cwd, env=env)
    try:
        proc.wait()
    except KeyboardInterrupt as e:
        print "KeyboardInterrupt"
        proc.send_signal(kill_signal)
    except Exception as e:
        print e
        proc.send_signal(kill_signal)

def run_fab(args):
    args[0] = 'fab'
    _run(args, SIGTERM)

def run_devserver():
    # Overwrite the wsgi_app config var to point to our internal app that will
    # also mount the static dirs.
    root = os.environ['SILK_ROOT']
    role = os.environ['SILK_ROLE']
    config = app_container.get_config(root, role)
    config['wsgi_app'] = 'silk.devserver:app'

    cmd = get_gunicorn_cmd({'config': config})

    subproc_env = {
        'SILK_ROOT': root,
        'SILK_ROLE': app_container.get_role(),
    }

    # By adding our current subproc_environment to that used for the subprocess, we
    # ensure that the same paths will be used (such as those set by virtualenv)
    subproc_env.update(os.environ)

    _run(cmd.split(), SIGINT, cwd=root, env=subproc_env)

    # This 1 second sleep lets the gunicorn workers exit before we show the
    # prompt again.
    time.sleep(1)

def install_skel(sitename):
    """Copies the contents of site_templates into the named directory (within cwd)"""
    root = os.environ['SILK_ROOT']
    #get the dir from pkg_resources
    src = pkg_resources.resource_filename('silk', 'site_templates')
    try:
        shutil.copytree(src, os.path.join(os.getcwd(), sitename))
    except OSError, e:
        print e

def get_local_archive_dir():
    return os.path.join(os.path.expanduser('~'), '.silk')

def get_pybundle_name(reqs):
    """Hash the requirements list to create a pybundle name."""
    # Strip leading and trailing whitespace
    reqs = reqs.strip()

    # put the lines in order to ensure consistent hashing
    lines = reqs.split()
    lines.sort()
    reqs = '\n'.join(lines)

    hash = hashlib.md5(reqs).hexdigest()
    return "%s.pybundle" % hash

def get_pybundle_path(reqs):
    """Return the name of the pybundle file that corresponds to the passed-in
    requirements text."""
    return os.path.join(get_local_archive_dir(), get_pybundle_name(reqs))

cmd_map = {
    'run': run_devserver,
    'skel': install_skel,
}

def cmd_dispatcher():
    """wraps 'fab', handles 'silk run'"""
    args = sys.argv
    try:
        cmd = args[1]

        # If a command is provided by cmd_map, use that.  Else pass through to
        # fabric.
        if cmd in cmd_map:
            # Stick some information about the role and root into the current env,
            # then call the local function in cmd_map.
            os.environ['SILK_ROLE'] = app_container.get_role() or ''
            os.environ['SILK_ROOT'] = app_container.get_site_root(os.getcwd()) or ''
            cmd_map[cmd]()
        else:
            # Use project-provided fabfile if present, else the one built into
            # Silk.  We'll have to trust that the project file imports ours.
            root = get_root(os.getcwd())
            site_fab = os.path.join(root, 'fabfile.py')
            if os.path.isfile(site_fab):
                fabfile = site_fab
            else:
                fabfile = pkg_resources.resource_filename('silk', 'fabfile.py')
            args.extend(['--fabfile', fabfile])
            run_fab(args)

    except IndexError:
        # Print out help text.  Currently just prints it for the cmds specified
        # in the fabfile, which isn't great because it omits things like 'silk
        # run' and 'silk deps'.  Would be better to inspect the fabfile and
        # list the cmds/docstrings myself, right along the non-fabfile cmds
        # that Silk provides.  Or I could just make all the things I provide as
        # fab cmds.  That might be the simpler approach.
        run_fab(['fab', '-l'])
