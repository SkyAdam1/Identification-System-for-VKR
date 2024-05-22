from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from rest_framework import HTTP_HEADER_ENCODING, exceptions
from rest_framework.authentication import BaseAuthentication


def get_api_authorization_header(request) -> str:
    auth = request.META.get("HTTP_X_API_KEY", b"")
    if isinstance(auth, bytes):
        auth = auth.decode(HTTP_HEADER_ENCODING)
    return auth


class InternalApiAccess(BaseAuthentication):
    def authenticate(self, request):
        api_key = get_api_authorization_header(request)

        if not api_key:
            raise exceptions.AuthenticationFailed("No API key")
        elif api_key != settings.INTERNAL_API_KEY:
            raise exceptions.AuthenticationFailed("Wrong API key")
        return (AnonymousUser(), None)