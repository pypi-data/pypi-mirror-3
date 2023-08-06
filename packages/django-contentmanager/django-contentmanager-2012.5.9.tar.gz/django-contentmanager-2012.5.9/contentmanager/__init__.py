# Ensure the user is running the version of python we require.
import sys
if not hasattr(sys, "version_info") or sys.version_info < (2, 4):
    raise RuntimeError("contentmanager requires Python 2.4 or later.")
del sys

VERSION = (2012, 5, 9)
__version__ = '.'.join(map(str, VERSION))

from registry import registry


# A flag to tell us if autodiscover is running.  autodiscover will set this to
# True while running, and False when it finishes.
REVE_LOADING = False
REVE_LOADED = False


def autodiscover():
    """
    Automatically find reveplugins

    Taken from django.contrib.admin for consistency."
    """
    # Bail out if autodiscover didn't finish loading from a previous call so
    # that we avoid running autodiscover again when the URLconf is loaded by
    # the exception handler to resolve the handler500 view.  This prevents an
    # reveplugins.py module with errors from re-registering models and raising a
    # spurious AlreadyRegistered exception (see #8245).
    global REVE_LOADING, REVE_LOADED
    if REVE_LOADING or REVE_LOADED:
        return
    REVE_LOADING = True

    import imp
    from django.conf import settings

    for app in settings.INSTALLED_APPS:
        # For each app, we need to look for an admin.py inside that app's
        # package. We can't use os.path here -- recall that modules may be
        # imported different ways (think zip files) -- so we need to get
        # the app's __path__ and look for admin.py on that path.

        # Step 1: find out the app's __path__ Import errors here will (and
        # should) bubble up, but a missing __path__ (which is legal, but weird)
        # fails silently -- apps that do weird things with __path__ might
        # need to roll their own admin registration.
        from django.utils.importlib import import_module
        try:
            app_path = import_module(app).__path__
        except AttributeError:
            continue

        # Step 2: use imp.find_module to find the app's reveplugins.py. For some
        # reason imp.find_module raises ImportError if the app can't be found
        # but doesn't actually try to import the module. So skip this app if
        # reveplugins.py doesn't exist
        try:
            imp.find_module('reveplugins', app_path)
        except ImportError:
            continue

        # Step 3: import the app's reveblocks. If this has errors we
        # want them to bubble up.
        __import__("%s.reveplugins" % app)
    # autodiscover was successful, reset loading flag.
    REVE_LOADED = True
    REVE_LOADING = False


def blockpath_rename(oldpath, newpath):
    from models import BlockPath
    affected_blockpaths = BlockPath.objects.filter(path__startswith=oldpath)
    cut_at = len(oldpath)
    for blockpath in affected_blockpaths:
        blockpath.path = newpath+blockpath.path[cut_at:]
        blockpath.save()
