#!/usr/bin/python2.5

import sys, site

# Website code
sys.path.insert (0, '/home/rocksoc/www/libpython/rocksoc1.0')

# Django, Python image library and other locally installed packages
site.addsitedir ('/home/rocksoc/www/lib/python2.5/site-packages')

from django.core.management import execute_manager
try:
    import settings # Assumed to be in the same directory.
except ImportError:
    import sys
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
    sys.exit(1)

if __name__ == "__main__":
    execute_manager(settings)
