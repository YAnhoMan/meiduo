from django.conf.urls import url

from . import views


urlpatterns = [
    # 商品列表数据
    url(r'^cart/$', views.CartView.as_view()),

    # 商品列表数据
    url(r'^cart/selection/$', views.CartSelectAllView.as_view()),

]