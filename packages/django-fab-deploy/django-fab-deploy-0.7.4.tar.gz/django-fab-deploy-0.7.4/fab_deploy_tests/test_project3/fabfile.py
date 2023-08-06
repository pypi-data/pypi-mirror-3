from fab_deploy.utils import define_host

@define_host('baz@127.0.0.1:2222')
def baz_site():
    return dict(
        CONFIG_TEMPLATES_PATHS=['test_project3/config_templates'],
        LOCAL_CONFIG = 'test_project3/config.py',
        REMOTE_CONFIG_TEMPLATE = 'test_project3/config.server.py',
        PIP_REQUIREMENTS_PATH = 'test_project3/reqs/',

        DB_USER = 'baz',
        DB_PASSWORD = '123',
        VCS = 'none',
        SERVER_NAME = 'baz.example.com'
    )
