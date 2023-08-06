import sys
import os
import datetime
import time
import posixpath
import random
import re
import copy
import yaml
import pkg_resources

from fabric.api import *
from fabric.colors import green, red, yellow
from fabric.contrib.files import exists, contains, upload_template

import silk.lib

def _join(*args):
    """Convenience wrapper around posixpath.join to make the rest of our
    functions more readable."""
    return posixpath.join(*args)

SRV_ROOT = '/srv'
DEFAULT_ROLLBACK_CAP = 3
DTS_FORMAT = '%Y%m%d_%H%M%S'
NGINX_SITE_DIR = '/etc/nginx/sites-enabled'

def _set_vars():
    """
    Loads deployment settings into Fabric's global 'env' dict
    """
    env.local_root = silk.lib.get_root(os.getcwd())
    env.config = silk.lib.get_site_config(env.local_root)
    env.dts = datetime.datetime.now().strftime(DTS_FORMAT)

    if len(env.roles) == 1:
        env.config.update(silk.lib.get_role_config(env.roles[0]))
    env.site = env.config['site']
    env.deployment = '%s_%s' % (env.site, env.dts)
    env.root = _join(SRV_ROOT, env.deployment)

    env.envdir = _join(env.root, 'env')
    env.rollback_cap = env.config.get('rollback_cap', DEFAULT_ROLLBACK_CAP)

    # Use the default supervisord include location for the deployment's include file.
    env.supd_conf_file = '/etc/supervisor/conf.d/%s.conf' % env.deployment

    # Set up gunicorn config
    env.default_bind = silk.lib.GUNICORN_BIND_PATTERN % env.deployment
    if 'gunicorn' in env.config:
        env.config['bind'] = env.config['gunicorn'].get('bind', env.default_bind)
    else:
        env.config['bind'] = env.default_bind

_set_vars()

# UGLY MAGIC
# Here we're (ab)using Fabric's built in 'role' feature to work with the way
# we're loading context-specific config.  Could possibly use a refactor to
# avoid Fabric roles altogether.
def _get_hosts():
    """Return list of hosts to push to"""
    return env.config['push_hosts']

for role in silk.lib.get_role_list(env.local_root):
    env.roledefs[role] = _get_hosts
# END UGLY MAGIC

def _tmpfile():
    """Generates a random filename in /tmp.  Useful for dumping stdout to a
    file that you want to download or read later.  Assumes the remote host has
    a /tmp directory."""
    chars = "abcdefghijklmnopqrstuvwxyz1234567890"
    length = 20
    randompart = "".join([random.choice(chars) for x in xrange(20)])
    return "/tmp/silk_tmp_%s" % randompart

def _put_dir(local_dir, remote_dir, exclude=''):
    """
    Copies a local directory to a remote one, using tar and put. Silently
    overwrites remote directory if it exists, creates it if it does not
    exist.
    """
    tarball = "%s.tar.bz2" % _tmpfile()

    tar_cmd = 'tar -C "%(local_dir)s" -cjf "%(tarball)s" %(exclude)s .' % locals()
    local(tar_cmd)
    put(tarball, tarball, use_sudo=True)
    local('rm -f "%(tarball)s"' % locals())
    sudo('rm -Rf "{0}"; mkdir -p "{0}"; tar -C "{0}" -xjf "{1}" && rm -f "{1}"'\
        .format(remote_dir, tarball))

def _get_blame():
    """
    Return information about this deployment, to be written as the "blame"
    section in the site.yaml file.
    """
    return {'deployed_by': env.user,
            'deployed_from': os.uname()[1],
            'deployed_at': datetime.datetime.now(),
            'deployed_role': env.roles[0]}

def _write_file(path, contents, use_sudo=True, chown=None):
    file_name = _tmpfile()
    file = open(file_name, 'w')
    file.write(contents)
    file.close()
    put(file_name, path, use_sudo=use_sudo)
    sudo('chmod +r %s' % path)
    if chown:
        sudo('chown %s %s' % (chown, path))
    local('rm %s' % file_name)

def _write_site_yaml():
    """Writes the site.yaml file for the deployed site."""
    # Make a copy of env.config
    site_yaml_dict = copy.copy(env.config)
    # add the blame in
    site_yaml_dict['blame'] = _get_blame()
    # write it to the remote host
    file = _join(env.root, 'site.yaml')
    _write_file(file, yaml.safe_dump(site_yaml_dict, default_flow_style=False))

def _write_template(template, dest, context):
    path = silk.lib.get_template_path(template, env.local_root)
    upload_template(path, dest, context=context, use_sudo=True)

def _ensure_dir(remote_path):
    if not exists(remote_path, use_sudo=True):
        sudo('mkdir -p %s' % remote_path)

def _format_supervisord_env(env_dict):
    """Takes a dictionary and returns a string in form
    'key=val,key2=val2'"""
    try:
      return ','.join(['%s="%s"' % (key, env_dict[key]) for key in env_dict.keys()])
    except AttributeError:
      #env_dict isn't a dictionary, so they must not have included any env vars for us.
      return ''

def _green(text):
    print green(text)

def _red(text):
    print red(text)

def _yellow(text):
    print yellow(text)

def _list_dir(dirname):
    """Given the path for a directory on the remote host, return its contents
    as a python list."""
    txt = sudo('ls -1 %s' % dirname)
    return txt.split('\r\n')

def _is_supervisored(site):
    """Returns True if site 'site' has a supervisord.conf entry, else False."""
    # Check both the default include location and the silk <=0.2.9 location.
    old_conf_file = _join(SRV_ROOT, site, 'conf', 'supervisord.conf')
    new_conf_file = _join('/etc/supervisor/conf.d', '%s.conf' % site)
    return exists(new_conf_file) or exists(old_conf_file)

def _socket_head_request(path):
    """Given a path to a socket, make an HTTP HEAD request on it"""
    # Get the local path for the unix socket http tool
    script = pkg_resources.resource_filename('silk', 'sock_http.py')
    # copy it over to the host
    dest = _tmpfile()
    put(script, dest, use_sudo=True)
    # run it, passing in the path to the socket
    return sudo('python %s %s HEAD / %s' % (dest, path,
                                            env.config['listen_hosts'][0]))

def _port_head_request(port):
    """Given a port number, use curl to make an http HEAD request to it.
    Return response status as integer."""
    return run('curl -I http://localhost:%s' % port)

def returns_good_status():
    """Makes an HTTP request to '/' on the site and returns True if it gets
    back a status in the 200, 300, or 400 ranges.

    You can only use this as a standalone silk command if your site has a
    hard-configured 'bind'."""
    _yellow("Making http request to site to ensure upness.")
    bind = env.config['bind']
    if bind.startswith('unix:'):
        result = _socket_head_request(bind.replace('unix:', ''))
    else:
        result = _port_head_request(bind.split(':')[-1])
    first_line = result.split('\r\n')[0]
    status = int(first_line.split()[1])
    return 200 <= status < 500

def _is_running(procname, tries=3, wait=2):
    """Given the name of a supervisord process, tell you whether it's running
    or not.  If status is 'starting', will wait until status has settled."""
    # Status return from supervisorctl will look something like this::
    # mysite_20110623_162319 RUNNING    pid 628, uptime 0:34:13
    # mysite_20110623_231206 FATAL      Exited too quickly (process log may have details)

    status_parts = sudo('supervisorctl status %s' % procname).split()
    if status_parts[1] == 'RUNNING':
        # For super extra credit, we're actually going to make an HTTP request
        # to the site to verify that it's up and running.  Unfortunately we
        # can only do that if Gunicorn is binding to a different socket or port
        # on each deployment (Silk binds to a new socket on each deployment by
        # default.)  If you've configured your site to bind to a port, we'll
        # just have to wing it.
        if env.config['bind'] == env.default_bind:
            if returns_good_status():
                _green("You're golden!")
                return True
            else:
                _red(":(")
                return False
        else:
            return True
    elif status_parts[1] == "FATAL":
        return False
    elif tries > 0:
        # It's neither running nor dead yet, so try again
        _yellow("Waiting %s seconds for process to settle" % wait)
        time.sleep(wait)

        # decrement the tries and double the wait time for the next check.
        return _is_running(procname, tries - 1, wait * 2)
    else:
        return False

def _is_this_site(name):
    """Return True if 'name' matches our site name (old style Silk deployment
    naming' or matches our name + timestamp pattern."""

    site_pattern = re.compile('%s_\d{8}_\d{6}' % env.site)
    return (name == env.site) or (re.match(site_pattern, name) is not None)

def install_server_deps():
    """
    Installs nginx and supervisord on remote Ubuntu host.
    """
    sudo('apt-get install nginx supervisor --assume-yes --quiet --no-upgrade')

def push_code():
    _green("PUSHING CODE")
    # Push the local site to the remote root, excluding files that we don't
    # want to leave cluttering the production server.  Exclude site.yaml
    # because we'll be writing a new one containing the site config updated
    # with the role config.  Omit roles because they're superfluous at that
    # point and also may contain sensitive connection credentials.
    exclude = "--exclude=site.yaml --exclude=roles"
    _put_dir(env.local_root, env.root, exclude)

def create_virtualenv():
    """Create a virtualenv inside the remote root"""
    if 'runtime' in env.config:
        pyversion = '--python=%s' % env.config['runtime']
    else:
        pyversion = ''

    # Put all the prereq packages into /srv/pip_cache on the remote host, if
    # they're not already there.
    local_dir = pkg_resources.resource_filename('silk', 'prereqs')
    files = pkg_resources.resource_listdir('silk', 'prereqs')

    for f in files:
        remote = posixpath.join('/tmp', f)
        local = posixpath.join(local_dir, f)
        if not exists(remote):
            put(local, remote, use_sudo=True)


    tmpl_vars = vars()
    tmpl_vars.update(env)

    c = ("virtualenv --no-site-packages %(pyversion)s --extra-search-dir=/tmp "
         "--never-download %(envdir)s") % tmpl_vars
    sudo(c)

def pip_deps():
    """Install requirements listed in the site's requirements.txt file."""

    _green("INSTALLING PYTHON DEPENDENCIES")
    reqs_file = os.path.join(env.root, 'requirements.txt')
    pypi = env.config.get('pypi', 'http://pypi.python.org/pypi')
    cachedir = posixpath.join(SRV_ROOT, 'pip_cache')
    _ensure_dir(cachedir)
    sudo('PIP_DOWNLOAD_CACHE="%s" %s/bin/pip install -r %s -i %s ' %
         (cachedir, env.envdir, reqs_file, pypi))

def configure_supervisor():
    """
    Creates and upload config file for supervisord
    """
    _green("WRITING SUPERVISOR CONFIG")

    template_vars = {
        'cmd': silk.lib.get_gunicorn_cmd(env, bin_dir='%s/bin' % (env.envdir)),
        'process_env': _format_supervisord_env(env.config.get('env', '')),
        'srv_root': SRV_ROOT,
    }

    template_vars.update(env)
    template_vars.update(env.config)
    #make sure the logs dir is created
    _ensure_dir(_join(env.root, 'logs'))

    # Put supervisord include in default location
    _write_template('supervisord.conf', env.supd_conf_file, template_vars)

def fix_supd_config_bug():
    """Fixes a bug from an earlier version of Silk that wrote an invalid line
    to the master supervisord.conf"""
    # Silk 0.2.9 and earlier included a command to configure supervisord and
    # nginx to include files in /srv/<site>/conf, in addition to their default
    # include directories.  While this was valid for nginx, supervisord does
    # not allow for multiple "files" lines in its "include" section (it does
    # allow for multiple globs on the single "files" line, though.  This command
    # finds the offending pattern in /etc/supervisor/supervisord.conf and
    # replaces it with the correct equivalent.

    # Note that Silk 0.3.0 and later does not require any changes from the
    # default supervisord.conf that ships with Ubuntu.  All files are included
    # in the supervisord's conf.d directory.

    file = '/etc/supervisor/supervisord.conf'

    if contains(file, "files = /srv/\*/conf/supervisord.conf", use_sudo=True):
        _green("FIXING OLD SUPERVISOR CONFIG BUG")
        _yellow("See http://bits.btubbs.com/silk-deployment/issue/15/incorrect-supervisord-include-config-in")

        bad = "\r\n".join([
            "files = /etc/supervisor/conf.d/*.conf",
            "files = /srv/*/conf/supervisord.conf"
        ])

        good = ("files = /etc/supervisor/conf.d/*.conf "
                "/srv/*/conf/supervisord.conf\n")

        txt = sudo('cat %s' % file)

        if bad in txt:
            txt = txt.replace(bad, good)
            _write_file(file, txt, use_sudo=True, chown='root')

def cleanup():
    """Deletes old versions of the site that are still sitting around."""
    _green("CLEANING UP")

    folders = _list_dir(SRV_ROOT)
    rollbacks = [x for x in folders if _is_this_site(x)]

    if len(rollbacks) > env.rollback_cap:
        # There are more rollbacks than we want to keep around.  See if we can
        # delete some.
        suspects = rollbacks[:-(env.rollback_cap + 1)]
        for folder in suspects:
            if not _is_supervisored(folder):
                fullpath = _join(SRV_ROOT, folder)
                sudo('rm -rf %s' % fullpath)

    # Clean up old socket files in /tmp/ that have no associated site
    # TODO: use our own list dir function and a regular expression to filter
    # the list of /tmp sockets instead of this funky grepping.
    with cd('/tmp'):
        socks = run('ls -1 | grep %s | grep sock | cat -' % env.site).split('\r\n')
    for sock in socks:
        procname = sock.replace('.sock', '')
        if not exists(_join(SRV_ROOT, procname)):
            sudo('rm /tmp/%s' % sock)

    # TODO: clean out the pip-* folders that can build up in /tmp
    # TODO: figure out a way to clean out pybundle files in /srv/_silk_build
    # that aren't needed anymore.

def start_process():
    """Tell supervisord to read the new config, then start the new process."""
    _green('STARTING PROCESS')
    result = sudo('supervisorctl reread')

    sudo('supervisorctl add %s' % env.deployment)

def _get_nginx_static_snippet(url_path, local_path):
    return """
    location %(url_path)s {
        alias %(local_path)s;
    }
    """ % locals()

def configure_nginx():
    """Writes a new nginx config include pointing at the newly-deployed site."""
    _green("WRITING NGINX CONFIG")
    nginx_static = ''
    static_dirs = env.config.get('static_dirs', None)

    # Use the static_dirs values from the site config to set up static file
    # serving in nginx.
    if static_dirs:
      for item in static_dirs:
          nginx_static += _get_nginx_static_snippet(
              item['url_path'],
              _join(env.root, item['system_path'])
          )
    template_vars = {
        'nginx_static': nginx_static,
        'nginx_hosts': ' '.join(env.config['listen_hosts']),
    }
    template_vars.update(env)
    template_vars.update(env.config)

    # Create nginx include here:
    # /etc/nginx/sites-enabled/<sitename>.conf
    nginx_file = _join('/etc', 'nginx', 'sites-enabled', env.site)
    sudo('rm -f %s' % nginx_file)
    _write_template('nginx.conf', nginx_file, template_vars)

def switch_nginx():
    _green("LOADING NEW NGINX CONFIG")

    # Check if there is an old-style version (within the site root) of the
    # nginx config laying around, and rename it to something innocuous if so.
    old_nginx = _join(SRV_ROOT, env.site, 'conf', 'nginx.conf')
    if exists(old_nginx):
        sudo('mv %s %s' % (old_nginx, "%s_disabled" % old_nginx))

    # Tell nginx to rescan its config files
    sudo('/etc/init.d/nginx reload')

def stop_other_versions():
    """Stop other versions of the site that are still running, and disable their
    configs."""
    proclist = sudo('supervisorctl status').split('\r\n')

    # parse each line so we can get at just the proc names
    proclist = [x.split() for x in proclist]

    # filter proclist to include only versions of our site
    proclist = [x for x in proclist if _is_this_site(x[0])]

    live_statuses = ["RUNNING", "STARTING"]

    # stop each process left in proclist that isn't the current one
    for proc in proclist:
        # We assume that spaces are not allowed in proc names
        procname = proc[0]
        procstatus = proc[1]
        if procname != env.deployment:
            # Stop the process
            if procstatus in live_statuses:
                sudo('supervisorctl stop %s' % procname)

            # Remove it from live config
            sudo('supervisorctl remove %s' % procname)

            # Remove its supervisord config file
            conf_file = '/etc/supervisor/conf.d/%s.conf' % procname
            if exists(conf_file):
                sudo('rm %s' % conf_file)

            # Also remove old style supervisord include if it exists
            old_conf_file = _join(SRV_ROOT, procname, 'conf/supervisord.conf')
            if exists(old_conf_file):
                sudo('rm %s' % old_conf_file)

    sudo('supervisorctl reread')

def congrats():
    """Congratulate the user and print a link to the site."""
    link0 = "http://%s" % env.config['listen_hosts'][0]
    msg = ("SUCCESS!  I think.  Check that the site is running by browsing "
           "to this url:\n\n%s" % link0)
    _green(msg)

def push():
    """
    The main function.  This function will put your site on the remote host and get it
    running.
    """
    # Make sure nginx and supervisord are installed
    install_server_deps()

    # Fix an embarrassing config bug from earlier versions
    fix_supd_config_bug()

    # push site code and pybundle to server, in timestamped folder
    push_code()
    # make virtualenv on the server and run pip install on the pybundle
    create_virtualenv()
    pip_deps()
    _write_site_yaml()
    # write supervisord config for the new site
    configure_supervisor()

    ##then the magic

    ##silk starts up supervisord on the new site
    start_process()
    # checks that the new site is running (by using supervisorctl)
    if _is_running(env.deployment):
        _green("Site is running.  Proceeding with nginx switch.")
        # if the site's running fine, then silk configures nginx to forward requests
        # to the new site
        configure_nginx()
        switch_nginx()
        stop_other_versions()
        cleanup()
        congrats()
    else:
        _red("Process failed to start cleanly.  Off to the log files!")
        sys.exit(1)
