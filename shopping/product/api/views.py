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
from shopping.product.filters import ProductFilter
from shopping.product.selectors import product_list, product_detail


class ProductListAPIView(ListAPIView):
    serializer_class = ProductListSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ProductFilter
    queryset = Product.objects.all()  # Define base queryset

    def get_queryset(self):
        return product_list()


class ProductRetrieveAPIView(RetrieveAPIView):
    queryset = product_detail()
    serializer_class = ProductSerializer
    lookup_field = "pk"


class ProductReviewListAPIView(ListAPIView):
    queryset = Review.objects.select_related("user").order_by("created_at")
    serializer_class = ProductReviewSerializer
    lookup_field = "pk"


class CategoryListAPIView(ListAPIView):
    queryset = Category.objects.root_nodes()  # only root nodes
    serializer_class = CategoryListSerializer
