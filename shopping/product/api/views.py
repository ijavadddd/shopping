from rest_framework.generics import ListAPIView, RetrieveAPIView
from shopping.product.api.serializers import (
    ProductListSerializer,
    ProductSerializer,
    ReviewSerializer,
    ProductReviewSerializer,
)

from shopping.product.models import Product, Review


class ProductListAPIView(ListAPIView):
    queryset = Product.objects.prefetch_related(
        "category", "variations", "images"
    ).defer("vendor")
    serializer_class = ProductListSerializer


class ProductRetrieveAPIView(RetrieveAPIView):
    queryset = Product.objects.prefetch_related(
        "category", "variations", "images", "reviews"
    ).select_related("vendor")
    serializer_class = ProductSerializer
    lookup_field = "slug"


class ReviewListAPIView(ListAPIView):
    queryset = Review.objects.select_related("user", "product")
    serializer_class = ReviewSerializer


class ProductReviewListAPIView(ListAPIView):
    queryset = Review.objects.select_related("user")
    serializer_class = ProductReviewSerializer
    lookup_field = "slug"
