from decimal import Decimal

from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet

from goods.models import SKU
from orders.models import OrderGoods, OrderInfo
from orders.serializers import OrderSettlementSerializer, SaveOrderSerializer, UnJudgeSerializer, JudgeSerializer


class OrderSettlementView(APIView):
    """
    订单结算
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        获取
        """
        user = request.user

        # 从购物车中获取用户勾选要结算的商品信息
        redis_conn = get_redis_connection('cart')
        redis_cart = redis_conn.hgetall('cart_%s' % user.id)
        cart_selected = redis_conn.smembers('cart_selected_%s' % user.id)

        cart = {}
        for sku_id in cart_selected:
            cart[int(sku_id)] = int(redis_cart[sku_id])

        # 查询商品信息
        skus = SKU.objects.filter(id__in=cart.keys())
        for sku in skus:
            sku.count = cart[sku.id]

        # 运费
        freight = Decimal('10.00')

        serializer = OrderSettlementSerializer({'freight': freight, 'skus': skus})
        return Response(serializer.data)


class SaveOrderView(CreateAPIView):
    """
    保存订单
    """
    permission_classes = [IsAuthenticated]
    serializer_class = SaveOrderSerializer


class OrderJudgeViewSet(ViewSet):
    """
    获取未评论商品及评论商品
    """

    permission_classes = [IsAuthenticated]

    @action(methods=['get'], detail=True)
    def uncommentgoods(self, request, pk=None):
        ordergoods = OrderGoods.objects.filter(order=pk, is_commented=False)
        serializer = UnJudgeSerializer(ordergoods, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True)
    def comments(self, request, pk=None):
        data = request.data
        object = OrderGoods.objects.get(order=pk, is_commented=False, sku_id=data.get('sku'))
        serializer = JudgeSerializer(instance=object, data=data)
        serializer.is_valid(raise_exception=True)
        object.is_commented = True

        unjudge = OrderGoods.objects.filter(order=pk, is_commented=False).count()
        if unjudge == 0:
            order = OrderInfo.objects.get(order_id=pk)
            order.status = 5
            order.save()
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
