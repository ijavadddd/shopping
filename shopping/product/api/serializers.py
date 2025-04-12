from rest_framework import serializers

from shopping.product.models import Product, ProductImage, Variation, Review, Category
from shopping.users.models import User


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        exclude = ("product",)


class VariationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variation
        fields = "__all__"


class ReviewSerializer(serializers.ModelSerializer):
    # user
    class Meta:
        model = Review
        exclude = ("product",)


class ProductReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        exclude = ("product",)


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "name")


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class ProductListSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)
    variation = VariationSerializer(many=True, read_only=True)
    category = CategorySerializer(many=False, read_only=True)

    class Meta:
        model = Product
        exclude = ("vendor",)


class ProductSerializer(ProductListSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)
    vendor = VendorSerializer(many=False, read_only=True)

    class Meta(ProductListSerializer.Meta):
        model = Product
        fields = "__all__"
        exclude = []
