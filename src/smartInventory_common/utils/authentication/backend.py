import hashlib

from rest_framework import authentication
from django.contrib.auth.models import AnonymousUser
from django.conf import settings


class ServerUser(AnonymousUser):
    def save(self):
        pass

    def delete(self):
        pass

    def set_password(self, raw_password):
        pass

    def check_password(self, raw_password):
        pass

    @property
    def is_authenticated(self):
        # Always return True. This is a way to tell if
        # the user has been authenticated in permissions
        return True

    @property
    def role(self):
        return "AD" if hasattr(settings, "TESTING") else "SYS"


class BackendAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        value = request.headers.get("X-AUTH-VALUE")
        challenge = request.headers.get("X-AUTH-CHALLENGE")
        if not challenge or not value or not hasattr(settings, "JWT_SECRET"):
            return None

        hash_value = hashlib.sha512(str(settings.JWT_SECRET).encode("UTF-8") + str(value).encode("UTF-8")).hexdigest()

        if str(hash_value) == str(challenge):
            user = ServerUser()

            return user, None

        return None
