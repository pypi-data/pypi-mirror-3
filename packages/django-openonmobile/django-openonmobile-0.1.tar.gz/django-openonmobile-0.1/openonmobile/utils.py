import random
from django.core.cache import cache
import string
import urllib

import settings


key_chars = string.ascii_letters + string.digits


def create_random_auth_key(key_length=None):
    if not key_length:
        key_length = settings.OPENONMOBILE_KEY_LENGTH

    key = [random.choice(key_chars) for i in range(key_length)]
    return "".join(key)


def mobile_url(request):
    # set auth key
    params = {}
    if request.user.is_authenticated():
        key = create_random_auth_key()
        cache.set(key, request.user.id, settings.OPENONMOBILE_KEY_TIMEOUT)
        params[settings.OPENONMOBILE_KEY] = key

    url = request.GET.get('url', '/')
    absolute_uri = request.build_absolute_uri(url)
    if params:
        absolute_uri = absolute_uri + "?" + urllib.urlencode(params)
    return absolute_uri
