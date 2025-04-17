from shopping.order.api.views import OrderAPIViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"v1", OrderAPIViewSet, basename="order")


app_name = "order"
urlpatterns = [] + router.urls
