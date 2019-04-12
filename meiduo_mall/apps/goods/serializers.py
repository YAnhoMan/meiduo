from rest_framework import serializers

from goods.models import GoodsChannel, GoodsCategory, SKU


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
