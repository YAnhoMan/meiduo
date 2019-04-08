from django.conf.urls import url

from .views import *

urlpatterns = [
    # 拼接QQ登录URL
    url(r'^qq/authorization/$', QQAuthURLView.as_view()),
    #
    url(r'^qq/user/$', QQAuthUserView.as_view()),

    # 发送邮件
    url(r'^email/$', EmailView.as_view()),

    # 验证邮件
    url(r'^email/verification/$', VerifyEmailView.as_view()),
]