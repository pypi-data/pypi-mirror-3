# my_project/config.server.py
# config file for environment-specific settings

DEBUG = True
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # TODO: postgres
        'NAME': '{{ DB_NAME }}.sqlite',
    }
}
INSTANCE_NAME = '{{ INSTANCE_NAME }}'
{{ EXTRA }}
