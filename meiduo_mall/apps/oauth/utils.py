from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadData

from meiduo_mall.settings.dev import SECRET_KEY


def generate_save_user_token(openid):
    serializer = Serializer(SECRET_KEY, 300)

    token = serializer.dumps({'openid': openid})

    return token.decode()


def generate_save_weibo_token(access_token):
    serializer = Serializer(SECRET_KEY, 300)

    token = serializer.dumps({'access_token': access_token})

    return token.decode()


def check_save_user_token(access_token):

    serializer = Serializer(SECRET_KEY, 300)

    try:
        data = serializer.loads(access_token)

    except BadData:
        return None

    else:
        return data.get('openid')


from django.conf import settings
from urllib.parse import urlencode, parse_qs
import json
import requests


class OAuthweibo(object):
    """
    微博认证辅助工具类
    """

    def __init__(self, client_id=None, client_secret=None, redirect_uri=None, state=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.state = state   # 用于保存登录成功后的跳转页面路径

    def get_weibo_url(self):
        # WEIBO登录url参数组建
        data_dict = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'state': self.state
        }

        # 构建url
        weibo_url = 'https://api.weibo.com/oauth2/authorize?' + urlencode(data_dict)

        return weibo_url

    # 获取access_token值
    def get_weibo_access_token(self, code):
        # 构建参数数据
        data_dict = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
            'code': code
        }

        # 构建url
        access_url = 'https://api.weibo.com/oauth2/access_token'

        data = None
        # 发送请求
        try:
            response = requests.post(access_url, data_dict)

            # 提取数据
            data = response.text
            data = eval(data)

        except Exception as e:
            raise Exception(e)

        # 提取access_token
        access_token = data.get('access_token', None)

        if not access_token:
            raise Exception('access_token获取失败')

        return access_token

    # 获取open_id值

    def get_open_id(self, access_token):

        # 构建请求url
        url = 'https://graph.qq.com/oauth2.0/me?access_token=' + access_token

        # 发送请求
        try:
            response = requests.get(url)

            # 提取数据
            # callback( {"client_id":"YOUR_APPID","openid":"YOUR_OPENID"} );
            # code=asdasd&msg=asjdhui  错误的时候返回的结果
            data = response.text
            data = data[10:-3]
        except:
            raise Exception('qq请求失败')
        # 转化为字典
        try:
            data_dict = json.loads(data)
            # 获取openid
            openid = data_dict.get('openid')
        except:
            raise Exception('openid获取失败')

        return openid


