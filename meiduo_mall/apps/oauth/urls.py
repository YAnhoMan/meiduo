from django.conf.urls import url

from .views import *

urlpatterns = [
    # 拼接QQ登录URL
    url(r'^qq/authorization/$', QQAuthURLView.as_view()),
    #
    url(r'^qq/user/$', QQAuthUserView.as_view()),

    url(r'^weibo/authorization/$', SINAAuthURLView.as_view()),

    url(r'^sina/user/$', SINAAuthUserView.as_view()),
]