from rest_framework import serializers

from shopping.product.models import Category
from shopping.product.models import Product
from shopping.product.models import ProductCategory
from shopping.product.models import ProductImage
from shopping.product.models import Review
from shopping.product.models import Variation
from shopping.users.models import User


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        exclude = ("product",)


class ProductVariationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variation
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


class ProductCategorySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="category.id", read_only=True)
    name = serializers.CharField(source="category.name", read_only=True)
    slug = serializers.CharField(source="category.slug", read_only=True)
    description = serializers.CharField(source="category.category", read_only=True)
    image = serializers.CharField(source="category.image", read_only=True)

    class Meta:
        model = ProductCategory
        exclude = ("product", "category")


class ProductListSerializer(serializers.ModelSerializer):
    image = ImageSerializer(source="images.first", many=False, read_only=True)
    variation = ProductVariationSerializer(
        source="variations.first",
        many=False,
        read_only=True,
    )
    category = ProductCategorySerializer(
        source="categories.first",
        many=False,
        read_only=True,
    )

    class Meta:
        model = Product
        exclude = ("vendor",)


class ProductSerializer(serializers.ModelSerializer):
    reviews = ProductReviewSerializer(many=True, read_only=True)
    vendor = VendorSerializer(many=False, read_only=True)
    images = ImageSerializer(many=True, read_only=True)
    variations = ProductVariationSerializer(many=True, read_only=True)
    categories = ProductCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = "__all__"
