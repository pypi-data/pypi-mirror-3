# Helmholtz settings for {{ project_name }} project.
import os

#Debug and maintenance options
DEBUG = True
TEMPLATE_DEBUG = DEBUG
DOWN_FOR_MAINTENANCE = False 
LOGS_LOCATION = '%s/logs' % os.getcwd()
LOG_LEVEL_FILE = 'DEBUG'
LOG_LEVEL_CONSOLE = 'INFO'
LOG_DATE_FORMAT = "%Y/%m/%d %H:%M:%S"
LOG_FORMAT = '%(asctime)s, %(name)s [%(levelname)s] : %(message)s'

#Tell if the website tracks user connection
COUNT_CONNECTIONS = True

#Session options
PASSWORD_RESET_TIMEOUT_DAYS = 1
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = DEBUG
SESSION_COOKIE_SECURE = False

#Project options
PROJECT_NAME = "{{ project_name }}"

#Site options
SITE_ID = 1
SITE_DOMAIN = "www.{{ project_name }}.com"
SITE_NAME = "{{ project_name }}".title()
SITE_ROOT = "/%s/" % (SITE_NAME.lower())
SITE_LOGO = "images/logos/{{ project_name }}_logo.png"
SITE_LOGO_ALT = "Your website logo here."

#Some useful urls concerning login and logout
LOGIN_URL = "%saccess_control/login/" % (SITE_ROOT)
LOGIN_REDIRECT_URL = "%s%s/" % (SITE_ROOT, 'trackers/detect_connection' if COUNT_CONNECTIONS else 'home')
LOGOUT_URL = "%saccess_control/logout/" % (SITE_ROOT)

#Contacts
DEFAULT_FROM_EMAIL = "mailbox@{{ project_name }}"
ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)
MANAGERS = ADMINS

#auth and access_control options
AUTH_PROFILE_MODULE = "management.Researcher"
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)
AUTHENTICATION_SERVERS = (
    #{'type':'basic', 'protocol':'http(s)', 'host':'remote.server.domain', 'auth_root':'login page', 'group': 'a group relative to the server'}
)
#Database properties
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '', # Or path to database file if using sqlite3.
        'USER': '', # Not used with sqlite3.
        'PASSWORD': '', # Not used with sqlite3.
        'HOST': '', # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '', # Set to empty string for default. Not used with sqlite3.
    }
}

#Datetime format
DATE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

#FILE_UPLOAD_MAX_MEMORY_SIZE = 
#FILE_UPLOAD_PERMISSIONS = 
FILE_UPLOAD_HANDLERS = ("django.core.files.uploadhandler.MemoryFileUploadHandler",
                        "django.core.files.uploadhandler.TemporaryFileUploadHandler",)

# List of processors used by RequestContext to populate the context.
# Each one should be a callable that takes the request object as its
# only parameter and returns a dictionary to add to the context.
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.contrib.messages.context_processors.messages',
    'helmholtz.core.context_processors.site',
)

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Paris'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory that holds static files.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL that handles the static files served from STATIC_ROOT.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin media -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# A list of locations of additional static files
STATICFILES_DIRS = ()

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = ''

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

#List of middleware
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.doc.XViewMiddleware',
    #'django.middleware.cache.CacheMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware'
)

ROOT_URLCONF = '{{ project_name }}.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = [
    #django apps
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.markup',
    #'tagging',
    #'debug_toolbar',
    #helmholtz apps
    #layer 0
    'helmholtz.core',
    'helmholtz.access_control',
    'helmholtz.access_request',
    'helmholtz.annotation',
    'helmholtz.species',
    'helmholtz.trackers',
    'helmholtz.units',
    #layer 1
    'helmholtz.measurements',
    'helmholtz.neuralstructures',
    'helmholtz.people',
    'helmholtz.preparations',
    'helmholtz.storage',
    'helmholtz.waveforms',
    #layer 2 
    'helmholtz.analysis',
    'helmholtz.chemistry',
    'helmholtz.equipment',
    'helmholtz.reconstruction',
    #layer 3
    'helmholtz.experiment',
    'helmholtz.electrophysiology',
    'helmholtz.location',
    #layer 4
    'helmholtz.drug_applications',
    'helmholtz.histochemistry',
    'helmholtz.optical_imaging',
    'helmholtz.stimulation',
    #layer 5
    'helmholtz.recording',
    'helmholtz.electricalstimulation',
    'helmholtz.visualstimulation',
    #layer 6
    'helmholtz.cells',
    'helmholtz.signals',
    
#    'helmholtz.core',
    'helmholtz.editor',

    #include these applications
    #to enable some management command
]

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request':{
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

os.environ['PYTHON_EGG_CACHE'] = '/srv/www/htdocs/.eggcache' 

from local_settings import *
