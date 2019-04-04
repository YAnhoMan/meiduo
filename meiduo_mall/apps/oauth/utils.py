from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadData

from meiduo_mall.settings.dev import SECRET_KEY


def generate_save_user_token(openid):
    serializer = Serializer(SECRET_KEY, 300)

    token = serializer.dumps({'openid': openid})

    return token.decode()


def check_save_user_token(access_token):

    serializer = Serializer(SECRET_KEY, 300)

    try:
        data = serializer.loads(access_token)

    except BadData:
        return None

    else:
        return data.get('openid')

