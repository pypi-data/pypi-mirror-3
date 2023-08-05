from fab_deploy import *

@define_host('foo@127.0.0.1:2222')
def foo_site():
    return dict(
        DB_USER = 'root',
        DB_PASSWORD = '123',
        VCS = 'none',
        SERVER_NAME = 'foo.example.com'
    )

def bar_site():
    env.hosts = ['foo@127.0.0.1:2222']
    env.conf = dict(
        DB_USER = 'root',
        DB_PASSWORD = '123',
        VCS = 'none',
        SERVER_NAME = 'bar.example.com',
        INSTANCE_NAME = 'bar',
    )
    update_env()

@define_host('foo@127.0.0.1:2222')
def invalid_site():
    return dict(
        DB_USER = 'root',
        DB_PASSWORD = '123',
        VCS = 'none',
        SERVER_NAME = 'invalid.example.com',
        INSTANCE_NAME = 'invalid',
        EXTRA = 'raise Exception()'
    )
