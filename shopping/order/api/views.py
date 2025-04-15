from django.db.models import Prefetch
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from shopping.order.api.serializers import OrderSerializer
from shopping.order.models import Order
from shopping.product.models import ProductImage


class OrderListAPIView(ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Order.objects.filter(user=self.request.user)
            .prefetch_related(
                "items",
                "items__product",
                Prefetch(
                    "items__product__images",
                    queryset=ProductImage.objects.order_by("-is_featured"),
                    to_attr="image",
                ),
            )
            .defer(
                "user__password",  # Better to be explicit about what to defer
                "items__product__reviews",
            )
        )
