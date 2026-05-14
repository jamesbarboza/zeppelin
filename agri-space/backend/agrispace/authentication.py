from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError


class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        token = request.COOKIES.get('access_token')
        if not token:
            return None
        try:
            validated_token = self.get_validated_token(token)
            return self.get_user(validated_token), validated_token
        except TokenError as e:
            raise AuthenticationFailed(str(e))
