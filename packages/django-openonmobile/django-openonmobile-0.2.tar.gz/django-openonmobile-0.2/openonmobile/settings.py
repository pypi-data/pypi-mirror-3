

from django.conf import settings

OPENONMOBILE_KEY = getattr(settings, 'OPENONMOBILE_KEY', 'openonmobile_key')

OPENONMOBILE_KEY_LENGTH = getattr(settings, 'OPENONMOBILE_KEY_LENGTH', 32)

OPENONMOBILE_KEY_TIMEOUT = getattr(settings, 'OPENONMOBILE_KEY_TIMEOUT', 300)
