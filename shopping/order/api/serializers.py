from rest_framework import serializers

from shopping.order.models import Order, Payment, Product, Shipping, Refund, OrderItem
from shopping.product.api.serializers import VendorSerializer, ProductSerializer
from shopping.product.models import Product, ProductAttribute
from django.db import transaction


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    # attribute = ProductAttributeSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product", "attribute", "quantity", "price"]


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        exclude = ("order",)


class ShippingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipping
        exclude = ("order",)


class RefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refund
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    shipping = ShippingSerializer(read_only=True)
    refund = RefundSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        exclude = ("user",)


class OrderItemCreateSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    attribute = serializers.PrimaryKeyRelatedField(
        queryset=ProductAttribute.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = OrderItem
        fields = ["product", "attribute", "quantity", "price"]


class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemCreateSerializer(many=True)
    payments = PaymentSerializer(many=True)
    shipping = ShippingSerializer()

    class Meta:
        model = Order
        exclude = ("user",)

    def create(self, validated_data):
        with transaction.atomic():
            # Extract nested data
            items_data = validated_data.pop("items")
            shipping_data = validated_data.pop("shipping")
            payment_data_list = validated_data.pop("payments")

            # Create order
            order = Order.objects.create(**validated_data)

            # Create shipping
            Shipping.objects.create(order=order, **shipping_data)

            # Create payments
            for payment_data in payment_data_list:
                Payment.objects.create(order=order, **payment_data)

            # Create order items
            for item_data in items_data:
                OrderItem.objects.create(
                    order=order,
                    product=item_data["product"],
                    attribute=item_data.get("attribute"),
                    quantity=item_data["quantity"],
                    price=item_data["price"],
                )

            return order
