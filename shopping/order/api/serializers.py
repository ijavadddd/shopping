from rest_framework import serializers
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from django.db.models import F

from shopping.order.models import Order, Payment, Product, Shipping, Refund, OrderItem
from shopping.product.api.serializers import VendorSerializer
from shopping.product.models import Product, ProductAttribute
from shopping.cart.models import CartItem


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


class StockValidationError(serializers.ValidationError):
    def __init__(self, message):
        super().__init__({"result": "error", "message": message, "status_code": 403})


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
    items = OrderItemSerializer(many=True)
    payments = PaymentSerializer(many=True, read_only=True)
    shipping = ShippingSerializer(read_only=True)

    class Meta:
        model = Order
        exclude = ("user",)

    def validate_items(self, items_data):
        # Track quantities for each product+variation combination
        quantity_totals = {}

        for item in items_data:
            product = item["product"]
            variation = item.get("variation")
            quantity = item["quantity"]

            # Create unique key for product+variation combination
            key = f"{product.id}_{variation.id if variation else 'none'}"

            # Add to total quantity for this combination
            if key in quantity_totals:
                quantity_totals[key] += quantity
            else:
                quantity_totals[key] = quantity

            # Check if variation exists for product
            if variation:
                if not ProductAttribute.objects.filter(
                    id=variation.id, product=product
                ).exists():
                    raise StockValidationError(
                        f"Variation {variation.id} does not exist for product {product.id}"
                    )

                # Check if total quantity exceeds variation stock
                if variation.stock < quantity_totals[key]:
                    raise StockValidationError(
                        f"Not enough stock for variation {variation.id}. Available: {variation.stock}, Requested: {quantity_totals[key]}"
                    )
            else:
                # Check if total quantity exceeds product stock
                if product.stock < quantity_totals[key]:
                    raise StockValidationError(
                        f"Not enough stock for product {product.id}. Available: {product.stock}, Requested: {quantity_totals[key]}"
                    )

        return items_data

    def create(self, validated_data):
        items_data = validated_data.pop("items")

        with transaction.atomic():
            order = Order.objects.create(**validated_data)

            # Track processed items to handle duplicates
            processed_items = {}

            for item_data in items_data:
                product = item_data["product"]
                variation = item_data.get("variation")
                quantity = item_data["quantity"]

                # Create unique key for product+variation combination
                key = f"{product.id}_{variation.id if variation else 'none'}"

                if key in processed_items:
                    # Update existing item's quantity
                    order_item = processed_items[key]
                    order_item.quantity = F("quantity") + quantity
                    order_item.save()
                else:
                    # Create new order item
                    order_item = OrderItem.objects.create(order=order, **item_data)
                    processed_items[key] = order_item

                # Reduce stock
                if variation:
                    variation.stock = F("stock") - quantity
                    variation.save()
                else:
                    product.stock = F("stock") - quantity
                    product.save()

            # Schedule stock restoration if payment is not completed within 10 minutes
            from django_q.tasks import schedule

            schedule(
                "shopping.order.tasks.restore_stock",
                order.id,
                schedule_type="O",
                next_run=timezone.now() + timedelta(minutes=10),
            )

        return order

    def update(self, instance, validated_data):
        if "items" in validated_data:
            items_data = validated_data.pop("items")

            with transaction.atomic():
                # Track processed items to handle duplicates
                processed_items = {}

                for item_data in items_data:
                    product = item_data["product"]
                    variation = item_data.get("variation")
                    quantity = item_data["quantity"]

                    # Create unique key for product+variation combination
                    key = f"{product.id}_{variation.id if variation else 'none'}"

                    try:
                        # Try to find existing order item
                        order_item = OrderItem.objects.get(
                            order=instance, product=product, variation=variation
                        )

                        # Check if adding quantity would exceed stock
                        if variation:
                            if variation.stock < (order_item.quantity + quantity):
                                raise StockValidationError(
                                    f"Adding {quantity} would exceed variation stock. Available: {variation.stock}"
                                )
                        else:
                            if product.stock < (order_item.quantity + quantity):
                                raise StockValidationError(
                                    f"Adding {quantity} would exceed product stock. Available: {product.stock}"
                                )

                        # Update quantity
                        order_item.quantity = F("quantity") + quantity
                        order_item.save()
                        processed_items[key] = order_item

                    except OrderItem.DoesNotExist:
                        if key not in processed_items:
                            # Create new order item
                            order_item = OrderItem.objects.create(
                                order=instance, **item_data
                            )
                            processed_items[key] = order_item
                        else:
                            # Update existing item's quantity
                            order_item = processed_items[key]
                            order_item.quantity = F("quantity") + quantity
                            order_item.save()

                    # Reduce stock
                    if variation:
                        variation.stock = F("stock") - quantity
                        variation.save()
                    else:
                        product.stock = F("stock") - quantity
                        product.save()

        return instance


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
