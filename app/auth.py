from django.contrib.auth.backends import BaseBackend
from .models import User
import bcrypt

class CustomAuthBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(username=username)
            if bcrypt.checkpw(password.encode(), user.hashed_password.encode()):
                # Set admin permissions for Django admin site
                if user.is_admin:
                    user.is_staff = True
                    user.is_superuser = True
                    user.save()
                else:
                    user.is_staff = False
                    user.is_superuser = False
                    user.save()
                return user
        except User.DoesNotExist:
            return None
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None