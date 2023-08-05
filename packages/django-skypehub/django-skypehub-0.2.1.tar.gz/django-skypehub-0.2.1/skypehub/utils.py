try:
    import simplejson as json
except ImportError:
    try:
        import json
    except ImportError:
        from django.utils import simplejson as json

import Skype4Py
from Skype4Py.errors import SkypeError

SKYPE_HOOK_OPTIONS = {
    'Transport': 'x11',
}


def get_skype(**kwargs):
    """return skype object.
    """
    options = kwargs or {}
    return Skype4Py.Skype(**options)


def get_skype_hook_options():
    """return SKYPE_HOOK_OPTIONS
    """
    from django.conf import settings
    if hasattr(settings, 'SKYPE_HOOK_OPTIONS'):
        return settings.SKYPE_HOOK_OPTIONS
    if is_windows():
        return {}
    return SKYPE_HOOK_OPTIONS


def is_windows():
    """Detect Windows platform.
    """
    import platform
    return platform.system() == 'Windows'
