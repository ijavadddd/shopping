from django.urls import path

from shopping.product.api.views import (
    ProductListAPIView,
    ProductRetrieveAPIView,
    ReviewListAPIView,
    ProductReviewListAPIView,
)

app_name = "product"
urlpatterns = [
    path("v1/list/", ProductListAPIView.as_view(), name="product_list"),
    path(
        "v1/retrieve/<slug:slug>",
        ProductRetrieveAPIView.as_view(),
        name="product_retrieve",
    ),
    path("v1/review_list/", ReviewListAPIView.as_view(), name="review_list"),
    path(
        "v1/review_list/<slug:slug>",
        ProductReviewListAPIView.as_view(),
        name="product_review_list",
    ),
]
