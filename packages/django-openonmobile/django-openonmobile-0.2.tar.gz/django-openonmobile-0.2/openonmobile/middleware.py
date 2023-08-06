
from django.contrib.auth import authenticate, login
from django.core.exceptions import ImproperlyConfigured

import settings


class AuthOnMobileMiddleware(object):

    def process_request(self, request):

        if not hasattr(request, 'user'):
            raise ImproperlyConfigured()

        if request.user.is_authenticated():
            return None

        key = request.GET.get(settings.OPENONMOBILE_KEY)
        if key:
            user = authenticate(openonmobile=key)
            if user:
                request.user = user
                request.GET = request.GET.copy()
                del request.GET[settings.OPENONMOBILE_KEY]
                login(request, user)

        return None
