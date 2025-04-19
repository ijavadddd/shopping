from rest_framework import serializers

from shopping.cart.models import Cart, Item
from shopping.order.api.serializers import (
    VendorSerializer,
    ImageSerializer,
    ProductVariationSerializer,
)
from shopping.order.models import Product, Variation
from django.db.models import F
from django.db import transaction

from shopping.product.api.serializers import ProductSerializer


class ItemSerializer(serializers.ModelSerializer):
    class ProductSerializer(serializers.ModelSerializer):
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

    product = ProductSerializer()
    variation = ProductVariationSerializer()

    class Meta:
        model = Item
        fields = "__all__"


class CartSerializer(serializers.ModelSerializer):
    items = ItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        exclude = ("user",)


class CartItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    variation = serializers.PrimaryKeyRelatedField(queryset=Variation.objects.all())

    class Meta:
        model = Item
        exclude = ("cart",)


class CartCreateSerializer(serializers.ModelSerializer):

    items = CartItemSerializer(many=True)

    class Meta:
        model = Cart
        exclude = ("user",)

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        cart, created = Cart.objects.get_or_create(**validated_data)

        with transaction.atomic():  # Ensure all operations succeed or fail together
            for item_data in items_data:
                # First try to get existing item
                try:
                    item_instance = Item.objects.get(
                        product=item_data["product"],
                        variation=item_data["variation"],
                        cart=cart,
                    )
                    # Update existing item
                    item_instance.quantity = F("quantity") + item_data["quantity"]
                    item_instance.save()
                except Item.DoesNotExist:
                    # Create new item
                    Item.objects.create(
                        product=item_data["product"],
                        variation=item_data["variation"],
                        cart=cart,
                        quantity=item_data["quantity"],
                    )

        return cart
