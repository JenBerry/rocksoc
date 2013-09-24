# Django settings for rocksoc project.

DEBUG = __import__('os').path.exists('/home/rocksoc/DEBUG_WEBSITE')
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('The webmasters', 'webmaster@rocksoc.org.uk'),
)

MANAGERS = (
    ('The webmasters', 'webmaster@rocksoc.org.uk'),
)
SERVER_EMAIL = 'webmaster@rocksoc.org.uk'
SEND_BROKEN_LINK_EMAILS = True

DATABASES = {
    'default' : {
        'ENGINE' : 'django.db.backends.mysql',
        'NAME' : 'rocksoc',
        'USER' : 'rocksoc',
        'PASSWORD' : 'vaoc22yauv',
        'HOST' : 'mysql-50.int.mythic-beasts.com',
        'OPTIONS' : {
            'read_default_file' : '/home/rocksoc/www/libpython/rocksoc1.0/rocksoc/my.cnf',
        }
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/London'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-gb'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = '/home/rocksoc/www.rocksoc.org.uk_html/media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = 'http://www.rocksoc.org.uk/media/'

# URL to use when referring to static files located in STATIC_ROOT.
# Example: "/site_media/static/" or "http://static.example.com/"
# If not None, this will be used as the base path for media definitions and the staticfiles app.
# It must end in a slash if set to a non-empty value.
STATIC_URL = 'http://www.rocksoc.org.uk/static/'

# The absolute path to the directory where collectstatic will collect static files for deployment.
# Example: "/home/example.com/static/"
# If the staticfiles contrib app is enabled (default) the collectstatic management command will collect
# static files into this directory. See the howto on managing static files for more details about usage.
STATIC_ROOT = '/home/rocksoc/www.rocksoc.org.uk_html/static/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = open('/home/rocksoc/www/etc/django_secret').read().strip()

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#    'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'rocksoc.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.http.ConditionalGetMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'rocksoc.urls'

ALLOWED_HOSTS = [ '.rocksoc.org.uk', '.rocksoc.co.uk' ]
ALLOWED_INCLUDE_ROOTS = ()      # none

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    '/home/rocksoc/www/libpython/rocksoc1.0/rocksoc/templates',
    '/home/rocksoc/www/lib/python2.5/django1.0/django/contrib/admin/templates',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.sites',
    'django.contrib.markup',
    'django.contrib.sitemaps',
    'rocksoc',
    'rocksoc.flatpages',
)

DEFAULT_FROM_EMAIL = 'webmaster@rocksoc.org.uk'
PREPEND_WWW = True
APPEND_SLASH = True

# Caching
USE_ETAGS = True

# For the reStructuredText format
RESTRUCTUREDTEXT_FILTER_SETTINGS = {
    'initial_header_level': 1,
    'doctitle_xform': False,
}

