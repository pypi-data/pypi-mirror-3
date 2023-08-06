
CHANGES
=======

0.7.4 (2012-03-01)
------------------
- django-fab-deploy now is compatible with fabric 1.4 (and require fabric 1.4);
- nginx and wsgi scripts are now compatible with upcoming django 1.4;
  example of django 1.4 project configuration is added to guide;
- shortcut for passing env defaults in ``define_host`` decorator;
- Ubuntu 10.04 apache restarting fix;
- config_templates/hgrc is removed;
- tests are updated for fabtest >= 0.1;
- ``apache_is_running`` function.

In order to upgrade install fabric >= 1.4 and make sure your custom scripts
work.

0.7.3 (2011-10-13)
------------------

- permanent redirect from www.domain.com to domain.com is added to the default nginx config.
  Previously they were both available and this leads to e.g. authorization issues (user logged
  in at www.domain.com was not logged in at domain.com with default django settings regarding cookie domain).

0.7.2 (2011-06-14)
------------------

- Ubuntu 10.04 (lucid) initial support (this needs more testing);
- backports for Ubuntu 10.04 and 10.10;
- docs are now using default theme;
- remote django management command errors are no longer silinced;
- invoking ``create_linux_account`` with non-default username is fixed;
- ``define_host`` decorator for easier host definition;
- default ``DB_USER`` value ('root') is deprecated;
- default nginx config uses ``INSTANCE_NAME`` for logs.

In order to upgrade please set ``DB_USER`` to 'root' explicitly in
``env.conf`` if it was omitted.

0.7.1 (2011-04-21)
------------------

- DB_ROOT_PASSWORD handling is fixed

0.7 (2011-04-21)
----------------

- requirement for root ssh access is removed: django-fab-deploy is now using
  sudo internally (thanks Vladimir Mihailenco);
- better support for non-root mysql users, ``mysql_create_user`` and
  ``mysql_grant_permissions`` commands were added (thanks Vladimir
  Mihailenco);
- hgrc is no more required;
- 'synccompress' management command is no longer called during ``fab up``;
- ``coverage`` command is disabled;
- ``nginx_setup`` and ``nginx_install`` are now available in
  command line by default;
- ``mysqldump`` no longer requires project dir to be created;
- home dir for root user is corrected;
- ``utils.detect_os`` is now failing loudly if detection fails;
- numerous test running improvements.

In order to upgrade from previous verions of django-fab-deploy,
install sudo on server if it was not installed::

    fab install_sudo

0.6.1 (2011-03-16)
------------------

- ``verify_exists`` argument of ``utils.upload_config_template``
  function was renamed to ``skip_unexistent``;
- ``utils.upload_config_template`` now passes all extra
  kwargs directly to fabric's ``upload_template`` (thanks Vladimir Mihailenco);
- ``virtualenv.pip_setup_conf`` command for uploading pip.conf
  (thanks Vladimir Mihailenco);
- ``deploy.push`` no longer calls 'synccompress' management command;
- ``deploy.push`` accepts 'before_restart' keyword argument -
  that's a callable that will be executed just before code reload;
- fixed regression in ``deploy.push`` command: 'notest' argument
  was incorrectly renamed to 'test';
- customization docs are added.

0.6 (2011-03-11)
----------------
- custom project layouts support (thanks Vladimir Mihailenco):
  standard project layout is no longer required; if the project has
  pip requirements file(s) and a folder with web server config templates
  it should be possible to use django-fab-deploy for deployment;
- git uploads support (thanks Vladimir Mihailenco);
- lxml installation is fixed;
- sqlite deployments are supported (for testing purposes).

If you are planning to migrate to non-default project layout, update the
config templates:

* in ``apache.config`` and ``nginx.config``:
  replace ``{{ SRC_DIR }}`` with ``{{ PROJECT_DIR }}``
* in ``django_wsgi.py``: replace ``{{ SRC_DIR }}`` with
  ``{{ PROJECT_DIR }}`` and make sure DJANGO_SETTINGS_MODULE doesn't
  contain INSTANCE_NAME::

      os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'


0.5.1 (2011-02-25)
------------------
- Python 2.5 support for local machine (it was always supported on servers).
  Thanks Den Ivanov.

0.5 (2011-02-23)
----------------

- OS is now auto-detected;
- Ubuntu 10.10 maverick initial support (needs better testing?);
- `fabtest <https://bitbucket.org/kmike/fabtest>`_ package is extracted
  from the test suite;
- improved tests;
- ``fab_deploy.system.ssh_add_key`` can now add ssh key even
  if it is the first key for user;
- 'print' calls are replaced with 'puts' calls in fabfile commands;
- django management commands are not executed if they are not available.

You'll probably want to remove ``env.conf.OS`` option from your fabfile.

If you're planning to deploy existing project to Ubuntu, add
``NameVirtualHost 127.0.0.1:{{ APACHE_PORT }}`` line to the top of your
``config_templates/apache.conf`` or delete the templates and run
``django-fab-deploy config_templates`` again.

0.4.2 (2011-02-16)
------------------

- tests are included in source distribution

0.4.1 (2011-02-14)
------------------

- don't trigger mysql 5.1 installation on Lenny

0.4 (2011-02-13)
----------------

- ``env.conf.VCS``: mercurial is no longer required;
- undeploy command now removes virtualenv.

0.3 (2011-02-12)
----------------

- Debian Squeeze support;
- the usage of ``env.user`` is discouraged;
- ``fab_deploy.utils.print_env`` command;
- ``fab_deploy.deploy.undeploy`` command;
- better ``run_as`` implementation.

In order to upgrade from 0.2 please remove any usages of ``env.user`` from the
code, e.g. before upgrade::

    def my_site():
        env.hosts = ['example.com']
        env.user = 'foo'
        #...

After upgrade::

    def my_site():
        env.hosts = ['foo@example.com']
        #...


0.2 (2011-02-09)
----------------

- Apache ports are now managed automatically;
- default threads count is on par with mod_wsgi's default value;
- ``env.conf`` is converted to _AttributeDict by ``fab_deploy.utils.update_env``.

This release is backwards-incompatible with 0.1.x because of apache port
handling changes. In order to upgrade,

- remove the first line ('Listen ...') from project's
  ``config_templates/apache.config``;
- remove APACHE_PORT settings from project's ``fabfile.py``;
- run ``fab setup_web_server`` from the command line.

0.1.2 (2011-02-07)
------------------
- manual config copying is no longer needed: there is django-fab-deploy
  script for that

0.1.1 (2011-02-06)
------------------
- cleaner internals;
- less constrains on project structure, easier installation;
- default web server config improvements;
- linux user creation;
- non-interactive mysql installation (thanks Andrey Rahmatullin);
- new documentation.

0.0.11 (2010-01-27)
-------------------
- fab_deploy.crontab module;
- cleaner virtualenv management;
- inside_project decorator.

this is the last release in 0.0.x branch.

0.0.8 (2010-12-27)
------------------
Bugs with multiple host support, backports URL and stray 'pyc' files are fixed.

0.0.6 (2010-08-29)
------------------
A few bugfixes and docs improvements.

0.0.2 (2010-08-04)
------------------
Initial release.
