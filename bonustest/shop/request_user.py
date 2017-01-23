from django.utils.deprecation import MiddlewareMixin
from django.dispatch import Signal

from threading import local

_user = local()
_user.value = None
_user.bonus = None


class RequestUserMiddleware(MiddlewareMixin):
    def process_request(self, request):
        set_current_user(request.user)


current_user_changed_signal = Signal(providing_args=["new_user"])


def set_current_user(user):
    _user.value = user
    current_user_changed_signal.send(None, new_user=user)


def get_current_user():
    return _user.value


def get_user_bonus():
    try:
        return _user.bonus
    except:
        return None


def set_user_bonus(bonus):
    _user.bonus = bonus
