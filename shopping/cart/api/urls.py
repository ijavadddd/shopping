from django.urls import path

from shopping.cart.api.views import CartAPIView

app_name = "cart"

urlpatterns = [
    path("", CartAPIView.as_view(), name="cart"),
]
