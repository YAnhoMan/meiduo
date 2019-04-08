from django.shortcuts import render

# Create your views here.
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User
from meiduo_mall.apps.users.serializers import CreateUserSerializer, UserDetailSerializer


class UserView(CreateAPIView):
    """
    用户注册
    """

    serializer_class = CreateUserSerializer


class UsernameCountView(APIView):
    """用户名数量"""
    def get(self, request, username):

        count = User.objects.filter(username=username).count()

        data = {
            'username': username,
            'count': count
        }

        return Response(data)


class MobileCountView(APIView):
    """手机号数量"""
    def get(self, request, mobile):

        count = User.objects.filter(mobile=mobile).count()

        data = {
            'mobile': mobile,
            'count': count
        }

        return Response(data)


class UserDetail(RetrieveAPIView):
    """
    用户个人信息
    """
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user














