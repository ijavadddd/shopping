from shopping.order.api.views import OrderAPIViewSet, AdminOrderAPI
from rest_framework.routers import DefaultRouter
from django.urls import path


router = DefaultRouter()
router.register(r"v1", OrderAPIViewSet, basename="order")


app_name = "order"
urlpatterns = [
    path("chart-data/", AdminOrderAPI.as_view(), name="chart_data"),
] + router.urls
