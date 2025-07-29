from django.urls import path

from shopping.product.api.views import ProductListAPIView
from shopping.product.api.views import ProductRetrieveAPIView
from shopping.product.api.views import ProductReviewListAPIView
from shopping.product.api.views import CategoryListAPIView

app_name = "product"
urlpatterns = [
    path("v1/list/", ProductListAPIView.as_view(), name="product_list"),
    path(
        "v1/retrieve/<int:pk>",
        ProductRetrieveAPIView.as_view(),
        name="product_retrieve",
    ),
    path(
        "v1/review_list/<int:pk>",
        ProductReviewListAPIView.as_view(),
        name="product_review_list",
    ),
    path(
        "v1/categories",
        CategoryListAPIView.as_view(),
        name="category_list",
    ),
]
