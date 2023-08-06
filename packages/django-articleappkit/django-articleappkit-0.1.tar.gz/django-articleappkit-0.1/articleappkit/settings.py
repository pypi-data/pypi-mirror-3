from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.core.files.storage import get_storage_class

DEFAULT_STATUS_CHOICES = (
    (0, _(u'DRAFT')),
    (1, _(u'PUBLISHED')),
    (2, _(u'UN-PUBLISHED')),
)


DEFAULT_SETTINGS = {
    'FIELDNAMES': {},
    'UNIQUE_TOGETHER': (),
    'AUTHOR_MODEL': 'auth.User',
    'AUTHOR_MODEL_LIMIT': {'is_staff': True},
    'IMAGE_STORAGE': settings.DEFAULT_FILE_STORAGE,
    'IMAGE_UPLOAD_TO': '',
    'STATUS_CHOICES': DEFAULT_STATUS_CHOICES,
    'DEFAULT_STATUS': 0,
    'PUBLISHED_STATUS': 1,
    'UNPUBLISHED_STATUS': 2,
}

USER_SETTINGS = DEFAULT_SETTINGS.copy()
USER_SETTINGS.update(getattr(settings, 'ARTICLEAPPKIT_SETTINGS', {}))
USER_SETTINGS['IMAGE_STORAGE'] = get_storage_class(USER_SETTINGS['IMAGE_STORAGE'])
globals().update(USER_SETTINGS)
