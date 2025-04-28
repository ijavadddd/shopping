from django.urls import path

from shopping.cart.api.views import CartAPIView, CartRemoveAPIView

app_name = "cart"

urlpatterns = [
    path("", CartAPIView.as_view(), name="cart"),
    path("remove/", CartRemoveAPIView.as_view(), name="cart-remove"),
]
