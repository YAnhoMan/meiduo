import logging

from django.shortcuts import render

from QQLoginTool.QQtool import OAuthQQ
# Create your views here.
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from rest_framework.views import APIView
from rest_framework_jwt.settings import api_settings

from carts.utils import merge_cart_cookie_to_redis
from meiduo_mall.apps.oauth import constants
from users.models import User
from .serializers import QQAuthUserSerializer
from .models import OAuthQQUser
from meiduo_mall.apps.oauth.utils import generate_save_user_token

logger = logging.getLogger('Django')


class QQAuthURLView(APIView):
    """
    提供QQ登录页面的URL
    """

    def get(self, request):
        next = request.query_params.get('next', '/')

        oauth = OAuthQQ(
            client_id=constants.QQ_CLIENT_ID,
            client_secret=constants.QQ_CLIENT_SECRET,
            redirect_uri=constants.QQ_REDIRECT_URI,
            state=next)

        login_url = oauth.get_qq_url()

        return Response({'login_url': login_url})


class QQAuthUserView(GenericAPIView):
    """
    QQ登录成功后的回调处理
    """

    serializer_class = QQAuthUserSerializer

    def get(self, request):
        # 获取前端传入的Code
        code = request.query_params.get('code')

        if not code:
            return Response({'message': '缺少code'},
                            status=status.HTTP_400_BAD_REQUEST)

        oauth = OAuthQQ(
            client_id=constants.QQ_CLIENT_ID,
            client_secret=constants.QQ_CLIENT_SECRET,
            redirect_uri=constants.QQ_REDIRECT_URI,
            state=next)

        try:

            access_token = oauth.get_access_token(code)

            openid = oauth.get_open_id(access_token)

        except Exception as e:
            logger.info(e)
            return Response({'message': 'QQ服务错误'},
                            status=status.HTTP_503_SERVICE_UNAVAILABLE)

        try:
            oauthQQUserModel = OAuthQQUser.objects.get(openid=openid)

        except OAuthQQUser.DoesNotExist:

            token = generate_save_user_token(openid)

            return Response({
                'access_token': token
            })

        else:
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

            # 获取oauth_user关联的user
            user = oauthQQUserModel.user
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)

            response = Response({
                'token': token,
                'user_id': user.id,
                'username': user.username
            })

            response = merge_cart_cookie_to_redis(request, user, response)

            return response

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        response = Response({
            'token': token,
            'user_id': user.id,
            'username': user.username
        })

        response = merge_cart_cookie_to_redis(request, user, response)

        return response







