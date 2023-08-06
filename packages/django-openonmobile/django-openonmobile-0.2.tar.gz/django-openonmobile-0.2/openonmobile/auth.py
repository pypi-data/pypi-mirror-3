
from django.contrib.auth.models import User
from django.core.cache import cache


class AuthOnMobileBackend(object):

    def authenticate(self, openonmobile=None):
        if openonmobile:
            user_id = cache.get(openonmobile)
            if user_id:
                try:
                    user = User.objects.get(pk=user_id)
                    return user
                except User.DoesNotExist:
                    pass
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
