from __future__ import with_statement
import re
from fabric.api import *
from fabric.contrib import files

from fab_deploy import utils
from fab_deploy import system


__all__ = ['touch', 'apache_restart']


APACHE_PORTS_FILE = '/etc/apache2/ports.conf'
APACHE_FIRST_PORT = 50000 # see http://www.iana.org/assignments/port-numbers
APACHE_LAST_PORT = 60000

def touch(wsgi_file=None):
    """ Reloads source code by touching the wsgi file. """
    if wsgi_file is None:
        wsgi_file = env.conf['ENV_DIR'] + '/var/wsgi/' + env.conf['INSTANCE_NAME'] + '.py'
    run('touch ' + wsgi_file)

def apache_make_wsgi():
    """ Uploads wsgi deployment script. """
    wsgi_dir = env.conf['ENV_DIR'] + '/var/wsgi/'
    run('mkdir -p ' + wsgi_dir)
    file_name = env.conf['INSTANCE_NAME'] + '.py'
    utils.upload_config_template('django_wsgi.py', wsgi_dir + file_name)

@utils.run_as_sudo
def apache_is_running():
    """
    Returns if apache is running
    """
    with settings(hide('running', 'stdout', 'stderr', 'warnings'), warn_only=True):
        output = sudo('invoke-rc.d apache2 status')
    return output.succeeded


@utils.run_as_sudo
def apache_restart():
    """ Restarts apache using init.d script. """
    # restart is not used because it can leak memory in some cases
    # without pty=False restart silently fails on Ubuntu 10.04.
    sudo('invoke-rc.d apache2 stop', pty=False)
    sudo('invoke-rc.d apache2 start', pty=False)

# ==== installation ===

@utils.run_as_sudo
def apache_install():
    """ Installs apache. """
    system.aptitude_install('apache2 libapache2-mod-wsgi libapache2-mod-rpaf')
    sudo('rm -f /etc/apache2/sites-enabled/default')
    sudo('rm -f /etc/apache2/sites-enabled/000-default')
    apache_setup_locale()

@utils.run_as_sudo
def apache_make_config():
    """ Updates apache config. """
    _apache_setup_port()
    name = env.conf['INSTANCE_NAME']
    utils.upload_config_template('apache.config',
                                 '/etc/apache2/sites-available/%s' % name,
                                 use_sudo=True)
    sudo('a2ensite %s' % name)

def apache_setup():
    """ Updates apache config, wsgi script and restarts apache. """
    apache_make_config()
    apache_make_wsgi()
    apache_restart()

@utils.run_as_sudo
def apache_setup_locale():
    """ Setups apache locale. Apache is unable to handle file uploads with
    unicode file names without this. """
    files.append('/etc/apache2/envvars',
                 ['export LANG="en_US.UTF-8"', 'export LC_ALL="en_US.UTF-8"'],
                 use_sudo=True)

# === automatic apache ports management ===

@utils.run_as_sudo
def _ports_lines():
    with settings(hide('stdout')):
        ports_data = sudo('cat ' + APACHE_PORTS_FILE)
    return ports_data.splitlines()

def _used_ports(lines):
    ports_mapping = dict()

    listen_re = re.compile('^Listen (?P<host>.+):\s*(?P<port>\d+)')
    instance_re = re.compile('^# used by (?P<instance>.+)')

    for index, line in enumerate(lines):
        match = re.match(listen_re, line)
        if match:
            instance = None
            if index:
                instance_match = re.match(instance_re, lines[index - 1])
                if instance_match:
                    instance = instance_match.group('instance')
            ports_mapping[match.group('port')] = instance
    return ports_mapping

@utils.run_as_sudo
def _apache_setup_port():
    """
    Makes sure some port is correctly listened in
    :file:`ports.conf` and sets :attr:`env.conf.APACHE_PORT`
    to this port.
    """
    lines = _ports_lines()

    # take over ports.conf
    TAKEOVER_STRING = '# This file is managed by django-fab-deploy. Please do not edit it manually.'
    if lines[0] != TAKEOVER_STRING:
        lines = [TAKEOVER_STRING]

    used_ports = _used_ports(lines)

    for port in used_ports:
        if used_ports[port] == env.conf.INSTANCE_NAME:
            # instance is binded to port
            env.conf.APACHE_PORT = port
            puts('Instance is binded to port ' + str(port))
            return

    # instance is not binded to any port yet;
    # find an empty port and listen to it.
    for port in range(APACHE_FIRST_PORT, APACHE_LAST_PORT):
        if str(port) not in used_ports: # port is found!
            lines.extend([
                '',
                '# used by ' + env.conf.INSTANCE_NAME,
                'Listen 127.0.0.1:' + str(port)
            ])
            env.conf.APACHE_PORT = port
            puts('Instance is not binded to any port. Binding it to port ' + str(port))
            sudo("echo '%s\n' > %s" % ('\n'.join(lines), APACHE_PORTS_FILE))
            return
    warn('All apache ports are used!')
