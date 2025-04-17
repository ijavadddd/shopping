from rest_framework import serializers

from shopping.order.models import Order, Payment, Product, Shipping, Refund, Variation
from shopping.order.models import OrderItem
from shopping.product.api.serializers import VendorSerializer, ImageSerializer
from shopping.product.api.serializers import ProductVariationSerializer
from django.db import transaction


class OrderItemSerializer(serializers.ModelSerializer):
    class OrderProductSerializer(serializers.ModelSerializer):
        vendor = VendorSerializer(many=False, read_only=True)
        image = ImageSerializer(source="images.first", many=False, read_only=True)

        class Meta:
            model = Product
            fields = "__all__"

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Make all fields optional except id
            for field_name, field in self.fields.items():
                if field_name != "id":
                    field.required = False

    product = OrderProductSerializer()
    variation = ProductVariationSerializer()

    class Meta:
        model = OrderItem
        exclude = ("order",)


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


class OrderCreateSerializer(serializers.ModelSerializer):
    class ItemSerializer(serializers.ModelSerializer):
        product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
        variation = serializers.PrimaryKeyRelatedField(queryset=Variation.objects.all())

        class Meta:
            model = OrderItem
            exclude = ("order",)  # Exclude order field as it will be set automatically

    items = ItemSerializer(many=True)
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
                    order=order,  # Set the order relationship here
                    product=item_data["product"],
                    variation=item_data["variation"],
                    **{
                        k: v
                        for k, v in item_data.items()
                        if k not in ["product", "variation"]
                    },
                )

            return order
