from rest_framework import serializers

from shopping.product.models import Category
from shopping.product.models import Product
from shopping.product.models import ProductCategory
from shopping.product.models import ProductImage
from shopping.product.models import Review
from shopping.product.models import AttributeType
from shopping.product.models import AttributeValue
from shopping.product.models import ProductVariation, ProductAttribute
from shopping.users.models import User


class ProductReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        exclude = ("product",)


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "name")


class ProductListSerializer(serializers.ModelSerializer):
    class CategorySerializer(serializers.ModelSerializer):
        id = serializers.IntegerField(source="category.id", read_only=True)
        name = serializers.CharField(source="category.name", read_only=True)
        slug = serializers.CharField(source="category.slug", read_only=True)

        class Meta:
            model = ProductCategory
            exclude = ("product", "category", "depth")

    image = serializers.SerializerMethodField(read_only=True)
    variations = serializers.SerializerMethodField(read_only=True)
    category = CategorySerializer(
        source="categories.first",
        many=False,
        read_only=True,
    )

    class Meta:
        model = Product
        exclude = ("vendor",)

    def get_image(self, obj):
        request = self.context.get("request")
        # Use prefetched data if available, otherwise fallback to query
        try:
            image = (
                getattr(obj, "_prefetched_objects_cache", {}).get("images", {}).first()
            )

            if image is None:
                image = obj.images.order_by("-is_featured").first()
            if image.image and hasattr(image.image, "url"):
                return (
                    request.build_absolute_uri(image.image.url)
                    if request
                    else image.image.url
                )
        except Exception as e:
            return None

    def get_variations(self, obj):
        attributes = getattr(obj, "_prefetched_objects_cache", {}).get(
            "variations", None
        )
        if attributes is None:
            attributes = obj.variations.filter(price_modifier__gt=0)
        attributes = filter(lambda x: x.price_modifier > 0, attributes)
        return [
            {
                "id": attribute.id,
                "name": attribute.attribute.attribute_type.name,
                "value": attribute.attribute.value,
                "price_modifier": attribute.price_modifier,
                "stock": attribute.stock,
            }
            for attribute in attributes
        ]


class ProductSerializer(serializers.ModelSerializer):

    class ProductAttributeSerializer(serializers.ModelSerializer):
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
            fields = [
                "id",
                "attribute_name",
                "attribute_name_slug",
                "attribute_value",
                "attribute_value_slug",
            ]

    reviews = ProductReviewSerializer(many=True, read_only=True)
    vendor = VendorSerializer(many=False, read_only=True)
    attributes = ProductAttributeSerializer(many=True, read_only=True)
    categories = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    variations = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "discounted_price",
            "available",
            "images",
            "attributes",
            "rating",
            "vendor",
            "reviews",
            "categories",
            "variations",
        ]

    def get_images(self, obj):
        request = self.context.get("request")
        # Use prefetched data if available, otherwise fallback to query
        images = getattr(obj, "_prefetched_objects_cache", {}).get("images", None)
        if images is None:
            images = obj.images.all().order_by("-is_featured")

        return [
            request.build_absolute_uri(image.image.url) if request else image.image.url
            for image in images
            if image.image and hasattr(image.image, "url")
        ]

    def get_variations(self, obj):
        attributes = getattr(obj, "_prefetched_objects_cache", {}).get(
            "variations", None
        )
        if attributes is None:
            attributes = obj.variations.filter(price_modifier__gt=0)
        attributes = filter(lambda x: x.price_modifier > 0, attributes)
        return [
            {
                "id": attribute.id,
                "name": attribute.attribute.attribute_type.name,
                "value": attribute.attribute.value,
                "price_modifier": attribute.price_modifier,
                "stock": attribute.stock,
            }
            for attribute in attributes
        ]

    def get_categories(self, obj):
        # Use prefetched data if available, otherwise fallback to query
        categories = getattr(obj, "_prefetched_objects_cache", {}).get(
            "categories", None
        )
        if categories is None:
            categories = obj.categories.all().order_by("-depth")

        return [
            {
                "id": pc.category.id,
                "name": pc.category.name,
                "slug": pc.category.slug,
            }
            for pc in categories
        ]
