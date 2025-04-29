from rest_framework import serializers
from django.db import transaction

from shopping.cart.models import Cart, CartItem
from shopping.product.api.serializers import ProductSerializer
from shopping.product.models import Product, ProductAttribute
from django.db.models import F


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    # attribute = ProductAttributeSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "product", "attribute", "quantity"]


class CartItemCreateSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    variation = serializers.PrimaryKeyRelatedField(
        queryset=ProductAttribute.objects.all(), required=False, allow_null=True
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

        if "items" in validated_data:
            items_data = validated_data.pop("items")
            with transaction.atomic():
                for item in items_data:
                    try:
                        item_instance = CartItem.objects.get(
                            product=item["product"],
                            variation=item.get("variation"),
                            cart=cart,
                        )
                        item_instance.quantity = F("quantity") + item["quantity"]
                        item_instance.save()
                    except CartItem.DoesNotExist:
                        CartItem.objects.create(**item, cart=cart)
        return cart

    def update(self, instance, validated_data):
        if "items" in validated_data:
            items_data = validated_data.pop("items")
            with transaction.atomic():
                for item in items_data:
                    try:
                        item_instance = CartItem.objects.get(
                            product=item["product"],
                            variation=item.get("variation"),
                            cart=instance,
                        )
                        item_instance.quantity = F("quantity") + item["quantity"]
                        item_instance.save()
                    except CartItem.DoesNotExist:
                        CartItem.objects.create(**item, cart=instance)

        return instance
