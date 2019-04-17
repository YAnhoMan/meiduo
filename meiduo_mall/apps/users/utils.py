import re

from django.contrib.auth.backends import ModelBackend

from users.models import User


def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'token': token,
        'user_id': user.id,
        'username': user.username
    }


def get_user_by_account(account):
    """
    根据手机号或用户名找到用户
    :param account: 用户名或手机号
    :return: User对象 或者 None
    """
    try:
        if re.match('^1[3-9]\d{9}$', account):
            user = User.objects.get(mobile=account)

        else:
            user = User.objects.get(username=account)

    except User.DoesNotExist:
        return None

    else:
        return user


class UsernameMobileAuthBackend(ModelBackend):
    """实现多账号登录"""

    def authenticate(self, request, username=None, password=None, **kwargs):
        user = get_user_by_account(username)

        if user:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        else:
            return
