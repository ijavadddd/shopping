from django.db.models import Prefetch
from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveAPIView
from rest_framework import viewsets

from shopping.product.api.serializers import ProductListSerializer
from shopping.product.api.serializers import ProductReviewSerializer
from shopping.product.api.serializers import ProductSerializer
from shopping.product.api.serializers import CategoryListSerializer
from shopping.product.models import Product, Category
from shopping.product.models import ProductImage
from shopping.product.models import Review
from shopping.product.models import ProductVariation, ProductAttribute
from django_filters import rest_framework as filters


class ProductFilter(filters.FilterSet):
    min_price = filters.NumberFilter(field_name="variations__price", lookup_expr="gte")
    max_price = filters.NumberFilter(field_name="variations__price", lookup_expr="lte")
    name = filters.CharFilter(field_name="name", lookup_expr="icontains")
    categories = filters.CharFilter(
        field_name="category__name", lookup_expr="icontains"
    )

    class Meta:
        model = Product
        fields = [
            # "variations__ price",
            "category__name",
            "name",
        ]

    def filter_queryset(self, queryset):
        """
        Override filter_queryset to handle dynamic attribute filters
        """
        queryset = super().filter_queryset(queryset)

        # Get all attribute type slugs from the request
        attribute_filters = {
            key: value
            for key, value in self.request.query_params.items()
            if key not in self.filters  # Exclude predefined filters
        }

        # Apply attribute filters
        for attr_slug, value_slug in attribute_filters.items():
            queryset = queryset.filter(
                attributes__attribute__attribute_type__slug=attr_slug,
                attributes__attribute__slug=value_slug,
            ).distinct()

        return queryset


class ProductListAPIView(ListAPIView):
    serializer_class = ProductListSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ProductFilter
    queryset = Product.objects.all()  # Define base queryset

    def get_queryset(self):
        # Get the filtered queryset first
        queryset = super().get_queryset()
        prefetch_args = []

        prefetch_args.append(
            Prefetch(
                "attributes",
                queryset=ProductAttribute.objects.select_related(
                    "attribute", "attribute__attribute_type"
                ),
            )
        )

        prefetch_args.append(
            Prefetch(
                "variations",
                queryset=ProductVariation.objects.select_related(
                    "attribute", "attribute__attribute_type"
                ),
            )
        )

        prefetch_args.append(
            Prefetch(
                "images",
                queryset=ProductImage.objects.order_by("-is_featured"),
            )
        )

        if prefetch_args:
            queryset = queryset.prefetch_related(*prefetch_args)

        return queryset.select_related("vendor")


class ProductRetrieveAPIView(RetrieveAPIView):
    queryset = Product.objects.prefetch_related(
        Prefetch("attributes", queryset=ProductAttribute.objects.all()),
        "category",
        Prefetch(
            "images",
            queryset=ProductImage.objects.order_by("-is_featured"),
        ),
        Prefetch(
            "variations",
            queryset=ProductVariation.objects.order_by("price_modifier"),
        ),
        "attributes__attribute",
        "attributes__attribute__attribute_type",
        "reviews__user",
    ).select_related("vendor")
    serializer_class = ProductSerializer
    lookup_field = "pk"


class ProductReviewListAPIView(ListAPIView):
    queryset = Review.objects.select_related("user").order_by("created_at")
    serializer_class = ProductReviewSerializer
    lookup_field = "pk"


class CategoryListAPIView(ListAPIView):
    queryset = Category.objects.root_nodes()  # only root nodes
    serializer_class = CategoryListSerializer
