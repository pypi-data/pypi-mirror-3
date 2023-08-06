# my_project/config.server.py
# config file for environment-specific settings

DEBUG = True
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': '{{ DB_NAME }}',
        'USER': '{{ DB_USER }}',
        'PASSWORD': '{{ DB_PASSWORD }}',
        'OPTIONS': {
            "init_command": "SET storage_engine=INNODB"
        },
    }
}
INSTANCE_NAME = '{{ INSTANCE_NAME }}'
