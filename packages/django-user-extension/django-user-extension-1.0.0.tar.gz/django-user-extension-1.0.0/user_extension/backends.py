from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from model_utils.managers import InheritanceQuerySet


class SubUserModelBackend(ModelBackend):
    """
    A modified ModelBackend that automatically returns the right
    subclass of User.
    """
    def authenticate(self, username=None, password=None):
        try:
            user = (InheritanceQuerySet(User).select_subclasses()
                    .get(username=username))
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return (InheritanceQuerySet(User).select_subclasses()
                    .get(pk=user_id))
        except User.DoesNotExist:
            return None
