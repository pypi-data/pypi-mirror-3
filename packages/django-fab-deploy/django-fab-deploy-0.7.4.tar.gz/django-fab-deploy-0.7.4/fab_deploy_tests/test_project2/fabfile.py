from fab_deploy import *

LAYOUT_OPTIONS = dict(
    PROJECT_PATH = 'src',
    LOCAL_CONFIG = 'local_settings.py',
    REMOTE_CONFIG_TEMPLATE = 'staging_settings.py',
    PIP_REQUIREMENTS_PATH = '',
    PIP_REQUIREMENTS = 'requirements.txt',
    PIP_REQUIREMENTS_ACTIVE = 'requirements.txt',
    CONFIG_TEMPLATES_PATHS = ['hosting/staging', 'hosting'],
)

@define_host('foo2@127.0.0.1:2222', LAYOUT_OPTIONS)
def foo_site():
    return dict(
        VCS = 'git',
        SERVER_NAME = 'foo.example.com',

        SUDO_USER = 'sudouser',

        DB_ROOT_PASSWORD = '123',
        DB_USER = 'foouser',
        DB_PASSWORD = 'foo123',
    )