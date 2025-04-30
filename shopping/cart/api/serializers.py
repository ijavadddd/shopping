from rest_framework import serializers
from django.db import transaction
from rest_framework.exceptions import APIException

from shopping.cart.models import Cart, CartItem
from shopping.product.models import Product, ProductVariation
from django.db.models import F
from shopping.order.api.serializers import ProductSerializer


class VariationSerializer(serializers.ModelSerializer):
    attribute_name = serializers.CharField(
        source="attribute.attribute_type.name", read_only=True
    )
    attribute_name_slug = serializers.CharField(
        source="attribute.attribute_type.slug", read_only=True
    )
    attribute_value = serializers.CharField(source="attribute.value", read_only=True)
    attribute_value_slug = serializers.CharField(
        source="attribute.slug", read_only=True
    )

    class Meta:
        model = ProductVariation
        exclude = ("product", "attribute")


class StockValidationError(APIException):
    status_code = 403
    default_detail = "quantity cant be more than stock"
    default_code = "stock_validation_error"

    def __init__(self, detail=None, code=None):
        super().__init__(detail, code)
        self.detail = {
            "result": "error",
            "message": self.default_detail,
            "status_code": self.status_code,
        }


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    variation = VariationSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "product", "variation", "quantity"]


class CartItemCreateSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    variation = serializers.PrimaryKeyRelatedField(
        queryset=ProductVariation.objects.all()
    )

    class Meta:
        model = CartItem
        fields = ["product", "variation", "quantity"]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        exclude = ("user",)


class CartCreateSerializer(serializers.ModelSerializer):
    items = CartItemCreateSerializer(many=True)

    class Meta:
        model = Cart
        exclude = ("user",)

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        cart, created = Cart.objects.get_or_create(**validated_data)

        with transaction.atomic():
            for item in items_data:
                product = item["product"]
                variation = item.get("variation")
                quantity = item["quantity"]

                # Check stock based on whether variation is specified
                if variation:
                    if variation.stock < quantity:
                        raise StockValidationError()
                else:
                    if product.stock < quantity:
                        raise StockValidationError()

                try:
                    item_instance = CartItem.objects.get(
                        product=item["product"],
                        variation=variation,
                        cart=cart,
                    )
                    # Check stock based on whether variation is specified
                    if variation:
                        if variation.stock < (item_instance.quantity + quantity):
                            raise StockValidationError()
                    else:
                        if product.stock < (item_instance.quantity + quantity):
                            raise StockValidationError()

                    item_instance.quantity = F("quantity") + quantity
                    item_instance.save()
                except CartItem.DoesNotExist:
                    CartItem.objects.create(
                        product=item["product"],
                        variation=variation,
                        cart=cart,
                        quantity=quantity,
                    )
        return cart

    def update(self, instance, validated_data):
        if "items" in validated_data:
            items_data = validated_data.pop("items")
            with transaction.atomic():
                for item in items_data:
                    product = item["product"]
                    variation = item.get("variation")
                    quantity = item["quantity"]

                    try:
                        item_instance = CartItem.objects.get(
                            product=item["product"],
                            variation=variation,
                            cart=instance,
                        )
                        # Check stock based on whether variation is specified
                        if variation:
                            if variation.stock < (item_instance.quantity + quantity):
                                raise StockValidationError()
                        else:
                            if product.stock < (item_instance.quantity + quantity):
                                raise StockValidationError()

                        new_quantity = item_instance.quantity + quantity
                        if new_quantity <= 0:
                            item_instance.delete()
                        else:
                            item_instance.quantity = F("quantity") + quantity
                            item_instance.save()
                    except CartItem.DoesNotExist:
                        # Only create new item if quantity is positive
                        if quantity > 0:
                            # Check stock based on whether variation is specified
                            if variation:
                                if variation.stock < quantity:
                                    raise StockValidationError()
                            else:
                                if product.stock < quantity:
                                    raise StockValidationError()

                            CartItem.objects.create(
                                product=item["product"],
                                variation=variation,
                                cart=instance,
                                quantity=quantity,
                            )

        return instance
