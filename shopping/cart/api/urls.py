from shopping.cart.api.views import CartAPIViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"v1", CartAPIViewSet, basename="cart")


app_name = "cart"
urlpatterns = [] + router.urls
