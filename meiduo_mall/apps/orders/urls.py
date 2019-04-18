from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from .views import *

urlpatterns = [

    url(r'^orders/$', SaveOrderView.as_view()),

    url(r'^orders/settlement/$', OrderSettlementView.as_view()),

]

router = DefaultRouter()
router.register('orders', OrderJudgeViewSet, base_name='judge')

urlpatterns += router.urls