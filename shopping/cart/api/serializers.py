from rest_framework import serializers

from shopping.cart.models import Cart, Item
from shopping.order.api.serializers import (
    VendorSerializer,
    ImageSerializer,
    ProductVariationSerializer,
)
from shopping.order.models import Product, Variation


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


class CartCreateSerializer(serializers.ModelSerializer):
    class ItemSerializer(serializers.ModelSerializer):
        product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
        variation = serializers.PrimaryKeyRelatedField(queryset=Variation.objects.all())

        class Meta:
            model = Item
            fields = "__all__"

    # def create(self, validated_data):
    #     Cart.objects.get_or_create()
