from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^sms_codes/(?P<mobile>1[3-9]\d{9})/$', views.SMSCodeView.as_view()),

    url(r"^image_codes/(?P<image_code_id>\w+-\w+-\w+-\w+-\w+)/$", views.ImageCode.as_view()),  # 发送图形验证码

]