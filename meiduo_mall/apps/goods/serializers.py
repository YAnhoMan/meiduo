from drf_haystack.serializers import HaystackSerializer
from rest_framework import serializers

from goods.models import GoodsChannel, GoodsCategory, SKU
from goods.search_indexes import SKUIndex


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategory
        fields = ['id', 'name']


class ChannelSerializer(serializers.ModelSerializer):
    category = CategorySerializer()

    class Meta:
        model = GoodsChannel
        fields = ['url', 'category']


class SKUSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKU
        fields = ['id', 'name', 'price', 'default_image_url', 'comments']


class SKUSerializer(serializers.ModelSerializer):
    """
    SKU序列化器
    """

    class Meta:
        model = SKU
        fields = ('id', 'name', 'price', 'default_image_url', 'comments')


class SKUIndexSerializer(HaystackSerializer):
    """
    SKU索引结果数据序列化器
    """
    object = SKUSerializer(read_only=True)

    class Meta:
        index_classes = [SKUIndex]
        fields = ('text', 'object')
