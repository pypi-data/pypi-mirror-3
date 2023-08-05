from django.conf import settings
from django.contrib.auth.models import check_password

from .models import User

class CouchDBAuthBackend(object):
    # Create a User object if not exists.
    # Subclasses must override this attribute.
    create_unknown_user = False

    def authenticate(self, username=None, password=None):
        user_cls = get_user_class()
        user = user_cls.get_user(username)
        if user and check_password(password, user.password):
            return user
        if not user:
            if self.create_unknown_user:
                user = user_cls(username)
                user.set_password(password)
                user.save()
                return user
            else:
                return None

    def get_user(self, username):
        user_cls = get_user_class()
        user = user_cls.get_user(username)
        if not user:
            raise KeyError
        return user


def get_user_class():
    if not hasattr(settings, 'USER_CLASS'):
        return User

    cls_name = settings.USER_CLASS
    index = cls_name.rfind('.')
    mod, cls = cls_name[:index], cls_name[index+1:]
    m = __import__(mod, fromlist=[cls])
    return getattr(m, cls)
