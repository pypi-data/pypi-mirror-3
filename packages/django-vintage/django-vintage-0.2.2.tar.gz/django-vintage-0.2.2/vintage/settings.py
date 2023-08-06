from django.conf import settings
from django.core.files.storage import get_storage_class
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module
from django.db.models import Q

DEFAULT_SETTINGS = {
    'METADATA_FORM': 'vintage.metadata_form.MetadataForm',
    'STORAGE': settings.DEFAULT_FILE_STORAGE,
    'JAVASCRIPT_URL': getattr(settings, 'STATIC_URL', settings.MEDIA_URL) + 'js/',
    'RELATION_MODELS': [],
}

USER_SETTINGS = DEFAULT_SETTINGS.copy()
USER_SETTINGS.update(getattr(settings, 'VINTAGE_SETTINGS', {}))

if not USER_SETTINGS['METADATA_FORM']:
    raise ImproperlyConfigured('The METADATA_FORM setting should be a python path to a Django Form class.')

bits = USER_SETTINGS['METADATA_FORM'].split('.')
importpath, classname = ".".join(bits[:-1]), bits[-1]
USER_SETTINGS['METADATA_FORM'] = getattr(import_module(importpath), classname)

USER_SETTINGS['STORAGE'] = get_storage_class(USER_SETTINGS['STORAGE'])

globals().update(USER_SETTINGS)

RELATIONS = [Q(app_label=al, model=m) for al, m in [x.split('.') for x in RELATION_MODELS]]
