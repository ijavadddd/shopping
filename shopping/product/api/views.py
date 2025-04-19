from django.db.models import Prefetch
from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveAPIView

from shopping.product.api.serializers import ProductListSerializer
from shopping.product.api.serializers import ProductReviewSerializer
from shopping.product.api.serializers import ProductSerializer
from shopping.product.models import Product
from shopping.product.models import ProductCategory
from shopping.product.models import ProductImage
from shopping.product.models import Review
from shopping.product.models import Variation
from django_filters import rest_framework as filters


class ProductFilter(filters.FilterSet):
    min_price = filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = filters.NumberFilter(field_name="price", lookup_expr="lte")
    name = filters.CharFilter(field_name="name", lookup_expr="icontains")
    categories = filters.CharFilter(
        field_name="categories__category__name", lookup_expr="icontains"
    )

    class Meta:
        model = Product
        fields = [
            "price",
            "categories__category__name",
            "name",
        ]


class ProductListAPIView(ListAPIView):
    serializer_class = ProductListSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ProductFilter

    def get_queryset(self):
        queryset = Product.objects.prefetch_related(
            Prefetch(
                "variations",
                queryset=Variation.objects.order_by("price_modifier"),
                to_attr="variation",
            ),
            Prefetch("categories", queryset=ProductCategory.objects.order_by("depth")),
            Prefetch(
                "images",
                queryset=ProductImage.objects.filter(is_featured=True),
                to_attr="image",
            ),
        ).defer("vendor")
        return queryset


class ProductRetrieveAPIView(RetrieveAPIView):
    queryset = Product.objects.prefetch_related(
        Prefetch("variations", queryset=Variation.objects.order_by("price_modifier")),
        Prefetch("categories", queryset=ProductCategory.objects.order_by("depth")),
        "categories__category",
        Prefetch(
            "images",
            queryset=ProductImage.objects.order_by("-is_featured"),
        ),
        "reviews__user",
    ).select_related("vendor")
    serializer_class = ProductSerializer
    lookup_field = "pk"


class ProductReviewListAPIView(ListAPIView):
    queryset = Review.objects.select_related("user").order_by("created_at")
    serializer_class = ProductReviewSerializer
    lookup_field = "pk"
