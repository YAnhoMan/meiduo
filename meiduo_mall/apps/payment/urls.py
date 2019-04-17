from django.conf.urls import url

from .views import *

urlpatterns = [
    # 拼接QQ登录URL
    url(r'^orders/(?P<order_id>\d+)/payment/$', PaymentView.as_view()),

    #
    url(r'^payment/status/$', PaymentStatusView.as_view()),



]