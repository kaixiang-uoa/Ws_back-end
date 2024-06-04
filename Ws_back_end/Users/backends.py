from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from Users.models import Ws_User

class DualAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            # First, try to authenticate against the default User model
            user = UserModel.objects.get(username=username)
            if user.check_password(password):
                return user
        except UserModel.DoesNotExist:
            pass
        
        try:
            # Next, try to authenticate against Ws_User model
            user = Ws_User.objects.get(email=username)
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        except Ws_User.DoesNotExist:
            pass

        return None
