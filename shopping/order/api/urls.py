from django.urls import path

from shopping.order.api.views import OrderListAPIView

app_name = "order"
urlpatterns = [
    path("v1/list/", OrderListAPIView.as_view(), name="order_list"),
]
