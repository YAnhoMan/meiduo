from django.conf.urls import url
from rest_framework import routers
from rest_framework_jwt.views import obtain_jwt_token

from .views import *

urlpatterns = [
    url(r'^users/', UserView.as_view()),
    url(r'^usernames/(?P<username>\w{5,20})/count/', UsernameCountView.as_view()),
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/', MobileCountView.as_view()),
    url(r'^authorizations/', obtain_jwt_token),
]

router = routers.DefaultRouter()
router.register(r'addresses', AddressViewSet, base_name='addresses')

urlpatterns += router.urls