from rest_framework import serializers

from shopping.order.models import Order, Payment, Product, Shipping, Refund, OrderItem
from shopping.product.api.serializers import VendorSerializer
from shopping.product.models import Product, ProductAttribute
from django.db import transaction


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


class ProductSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "price",
            "discounted_price",
            "stock",
            "available",
            "image",
        ]

    def get_image(self, obj):
        request = self.context.get("request")
        # Use prefetched data if available, otherwise fallback to query
        try:
            image = getattr(obj, "image", [])[0] if getattr(obj, "image", []) else None
        except (IndexError, AttributeError):
            image = obj.images.order_by("-is_featured").first()
        if image and hasattr(image.image, "url"):
            return (
                request.build_absolute_uri(image.image.url)
                if request
                else image.image.url
            )
        return None


class OrderItemSerializer(serializers.ModelSerializer):
    class VariationSerializer(serializers.ModelSerializer):
        attribute_name = serializers.CharField(
            source="attribute.attribute_type.name", read_only=True
        )
        attribute_name_slug = serializers.CharField(
            source="attribute.attribute_type.slug", read_only=True
        )
        attribute_value = serializers.CharField(
            source="attribute.value", read_only=True
        )
        attribute_value_slug = serializers.CharField(
            source="attribute.slug", read_only=True
        )

        class Meta:
            model = ProductAttribute
            exclude = ("product", "attribute")

    product = ProductSerializer(read_only=True)
    refunds = RefundSerializer(many=True, read_only=True)
    variation = VariationSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "quantity",
            "price",
            "refunds",
            "variation",
        ]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    shipping = ShippingSerializer(read_only=True)

    class Meta:
        model = Order
        exclude = ("user",)


class OrderItemCreateSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    variation = serializers.PrimaryKeyRelatedField(
        queryset=ProductAttribute.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = OrderItem
        fields = ["product", "variation", "quantity", "price"]


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
                    variation=item_data.get("variation"),
                    quantity=item_data["quantity"],
                    price=item_data["price"],
                )

            return order
