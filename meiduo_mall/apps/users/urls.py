from django.conf.urls import url
from rest_framework import routers
from rest_framework_jwt.views import obtain_jwt_token

from .views import *

urlpatterns = [
    # 用户注册
    url(r'^users/', UserView.as_view()),

    # 判断用户名是否已注册
    url(r'^usernames/(?P<username>\w{5,20})/count/', UsernameCountView.as_view()),

    # 判断用户手机号是否已注册
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/', MobileCountView.as_view()),

    # 用户登录
    url(r'^authorizations/', obtain_jwt_token),

    # 用户详细信息
    url(r'^user/', UserDetail.as_view()),

    # 设置邮箱
    url(r'^email/$', EmailView.as_view()),

    # 验证邮件
    url(r'^emails/verification/$', VerifyEmailView.as_view()),
]

router = routers.DefaultRouter()
router.register(r'addresses', AddressViewSet, base_name='addresses')

urlpatterns += router.urls