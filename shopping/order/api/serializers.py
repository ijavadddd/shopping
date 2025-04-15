from rest_framework import serializers

from shopping.order.models import Order
from shopping.order.models import OrderItem
from shopping.product.api.serializers import OrderProductSerializer
from shopping.product.api.serializers import ProductVariationSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    product = OrderProductSerializer(read_only=True)
    variation = ProductVariationSerializer(read_only=True)

    class Meta:
        model = OrderItem
        exclude = ("order",)


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        exclude = ("user",)
