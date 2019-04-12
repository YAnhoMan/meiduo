from django.conf.urls import url

from . import views


urlpatterns = [
    # 商品列表数据
    url(r'^categories/(?P<category_id>\d+)/skus/', views.SKUListView.as_view()),

    url(r'^categories/(?P<pk>\d+)/', views.CategoryView.as_view()),

]