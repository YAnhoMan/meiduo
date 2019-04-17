from django.conf.urls import url

from .views import *

urlpatterns = [

    url(r'^orders/$', SaveOrderView.as_view()),

    url(r'^orders/settlement/$', OrderSettlementView.as_view()),

]