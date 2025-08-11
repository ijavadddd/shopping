from shopping.order.api.views import (
    OrderAPIViewSet,
    AdminOrderAPI,
    DashboardLastOrderList,
)
from rest_framework.routers import DefaultRouter
from django.urls import path


router = DefaultRouter()
router.register(r"v1", OrderAPIViewSet, basename="order")


app_name = "order"
urlpatterns = [
    path("dashboard/chart-data/", AdminOrderAPI.as_view(), name="chart_data"),
    path("dashboard/last-orders/", DashboardLastOrderList.as_view(), name="last_order"),
] + router.urls
