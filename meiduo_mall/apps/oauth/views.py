from django.shortcuts import render

from QQLoginTool.QQtool import OAuthQQ
# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView
from meiduo_mall.apps.oauth import constants


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
