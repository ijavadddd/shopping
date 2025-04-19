from shopping.cart.api.views import CartAPIView, CartRemoveAPIView
from rest_framework.routers import DefaultRouter
from django.urls import path

app_name = "cart"
urlpatterns = [
    path("", CartAPIView.as_view(), name="cart"),
    path("remove/", CartRemoveAPIView.as_view(), name="item_remove"),
]
