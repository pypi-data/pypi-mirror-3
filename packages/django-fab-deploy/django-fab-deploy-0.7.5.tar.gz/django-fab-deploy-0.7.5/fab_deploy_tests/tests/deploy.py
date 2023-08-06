from __future__ import absolute_import
import os
from fabric.api import *
from fabtest import fab, vbox_urlopen, FabricAbortException
from fab_deploy.utils import run_as
from fab_deploy.deploy import deploy_project, push, undeploy
from fab_deploy.mysql import mysql_create_db
from fab_deploy.apache import (apache_make_config, apache_make_wsgi,
                               apache_restart, apache_install)
from fab_deploy.django_commands import command_is_available
from .base import FabDeployTest
from ..utils import setup_ssh, setup_sudo
from ..test_project.fabfile import foo_site, bar_site, invalid_site
from ..test_project2.fabfile import foo_site as foo_site2
from ..test_project3.fabfile import baz_site

def get_file_content(remote_file):
    @run_as('root')
    def cat():
        with(hide('stdout')):
            return run('cat '+remote_file)
    return fab(cat)

def get_ports():
    @run_as('root')
    def ports():
        return run('netstat -A inet -lnp')
    return fab(ports)

def is_local_port_binded(port):
    port_string = '127.0.0.1:%s' % port
    ports = get_ports()
    return port_string in ports

class FabDeployProjectTest(FabDeployTest):
    snapshot = 'fabtest-prepared-server'
    project = 'test_project'

    def assertResponse(self, url, data):
        self.assertEqual(vbox_urlopen(url).read(), data)

    def assertHttpError(self, url):
        # FIXME: this should only catch BadStatusLine and urllib2.HttpError
        self.assertRaises(Exception, vbox_urlopen, url)

    def assertNoFile(self, path):
        with(settings(warn_only=True)):
            res = get_file_content(path)
        self.assertFalse(res.succeeded)

    def assertFileExists(self, path):
        with(settings(warn_only=True)):
            self.assertTrue(get_file_content(path))

    def assertCommandAvailable(self, command):
        result = fab(command_is_available, command)
        self.assertTrue(result)

    def assertCommandNotAvailable(self, command):
        result = fab(command_is_available, command)
        self.assertFalse(result)

    def assertCommandFails(self, command):
        self.assertRaises(FabricAbortException, fab,
                          command_is_available, command)

    def setup_conf(self):
        self.cwd = os.getcwd()
        os.chdir(self.project)
        fab(foo_site)

    def tearDown(self):
        os.chdir(self.cwd)
        super(FabDeployProjectTest, self).tearDown()


class ApacheSetupTest(FabDeployProjectTest):

    def assertPortBinded(self, port):
        self.assertTrue(is_local_port_binded(port))

    def assertPortNotBinded(self, port):
        self.assertFalse(is_local_port_binded(port))

    def test_apache_config(self):
        fab(apache_install)

        # first site
        fab(foo_site)
        fab(apache_make_config)

        foo_port = env.conf.APACHE_PORT
        self.assertPortNotBinded(foo_port)
        self.assertFileExists('/etc/apache2/sites-enabled/foo')

        fab(apache_restart)
        self.assertPortBinded(foo_port)

        # second site
        fab(bar_site)
        fab(apache_make_config)

        bar_port = env.conf.APACHE_PORT
        self.assertNotEqual(foo_port, bar_port)
        self.assertPortNotBinded(bar_port)

        fab(apache_restart)
        self.assertPortBinded(bar_port)

        # re-configuring doesn't lead to errors
        fab(apache_make_config)
        fab(apache_restart)
        self.assertPortBinded(bar_port)

    def test_apache_make_wsgi(self):
        self.assertNoFile(env.conf.ENV_DIR+'/var/wsgi/foo.py')
        fab(apache_make_wsgi)
        self.assertFileExists(env.conf.ENV_DIR+'/var/wsgi/foo.py')


class DeployTest(FabDeployProjectTest):

    def assertInstanceWorks(self, instance):
        url = 'http://%s.example.com/instance/' % instance
        self.assertResponse(url, instance)

    def assertInstanceDoesntWork(self, instance):
        url = 'http://%s.example.com/instance/' % instance
        self.assertHttpError(url)

    def test_deploy(self):
        self.assertCommandFails('syncdb')

        # deploy first site
        fab(foo_site)
        fab(deploy_project)

        self.assertCommandAvailable('syncdb')
        self.assertCommandNotAvailable('syncddb')

        self.assertInstanceWorks('foo')

        # deploy second site
        fab(bar_site)
        fab(deploy_project)

        self.assertInstanceWorks('bar')
        self.assertInstanceWorks('foo')

        # deploy improperly configured site
        fab(invalid_site)

        # config errors should not be silenced
        self.assertRaises(FabricAbortException, fab, deploy_project)

        # old sites still work
        self.assertInstanceWorks('bar')
        self.assertInstanceWorks('foo')
        self.assertInstanceDoesntWork('invalid')


class CustomLayoutDeployTest(FabDeployProjectTest):
    project = 'test_project2'

    def setUp(self):
        super(CustomLayoutDeployTest, self).setUp()

    def test_deploy(self):
        url = 'http://foo.example.com/instance/'
        fab(foo_site2)

        setup_sudo()
        setup_ssh()

        fab(mysql_create_db)
        fab(deploy_project)
        self.assertResponse(url, 'foo2')

        # just check that blank push doesn't break anything
        # TODO: proper push tests
        fab(push, 'pip_update', 'syncdb')
        self.assertResponse(url, 'foo2')

        # check that updeploy disables the site
        # TODO: more undeploy tests
        fab(undeploy, confirm=False)
        self.assertHttpError(url)

        # deploying project again should be possible
        fab(deploy_project)
        self.assertResponse(url, 'foo2')

    def test_push_callback(self):

        def before_restart():
            before_restart.called = True
        before_restart.called = False

        def my_push(*args):
            return push(*args, before_restart=before_restart)

        fab(foo_site2)

        setup_sudo()
        setup_ssh()

        fab(mysql_create_db)
        fab(deploy_project)
        fab(my_push)
        self.assertTrue(before_restart.called)


class Django14LayoutDeployTest(FabDeployProjectTest):
    project = 'test_project3'

    def test_deploy(self):
        url = 'http://baz.example.com/instance/'
        fab(baz_site)

        setup_sudo()
        setup_ssh()
        fab(deploy_project)
        self.assertResponse(url, 'baz')
