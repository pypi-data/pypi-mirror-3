import os

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'scaler',
    }
}

ROOT_URLCONF = 'scaler.urls'

INSTALLED_APPS = (
    'scaler',
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
)

MIDDLEWARE_CLASSES = (
    'scaler.middleware.ScalerMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.request',
)

DJANGO_SCALER = {
    'server_busy_url_name': 'server-busy',
    # How many response times to consider for an URL. A small value means slow
    # response times are quickly acted upon, but it may be overly aggressive.
    # A large value means an URL must be slow for a number of requests before
    # it is acted upon.
    'trend_size': 10,
    # How much slower than average the trend must be before redirection kicks
    # in.
    'slow_threshold': 2.0,
    # How many seconds to keep redirecting an URL before serving normally.
    'redirect_for': 60,
    # A function that returns how many of the slowest URLs must be redirected.
    # Depending on the site, data and load on the server this may be a large
    # number.  This allows external processes to instruct the middleware to
    # redirect.
    'redirect_n_slowest_function': lambda: 0
}
