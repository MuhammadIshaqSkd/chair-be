from config.settings.base import * # noqa

DEBUG = True
ALLOWED_HOSTS = ['*']

if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']

    # Debug toolbar settings
    INTERNAL_IPS = ['127.0.0.1']