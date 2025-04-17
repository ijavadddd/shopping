from django.db.models import Prefetch
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from shopping.order.api.serializers import OrderSerializer, OrderCreateSerializer
from shopping.order.models import Order, Payment, Refund
from shopping.product.models import ProductImage

from rest_framework import status
from rest_framework.response import Response


class OrderAPIViewSet(ModelViewSet):
    http_method_names = ["get", "post", "patch", "head", "options"]
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = "pk"

    def get_serializer_class(self):
        return OrderCreateSerializer if self.action == "create" else OrderSerializer

    def _get_base_queryset(self):
        """Shared base queryset for list and retrieve actions"""
        return Order.objects.filter(user=self.request.user).select_related("shipping")

    def _get_prefetch_config(self):
        """Shared prefetch configuration for list and retrieve actions"""
        return [
            "items",
            "items__product",
            Prefetch(
                "items__product__images",
                queryset=ProductImage.objects.filter(is_featured=True),
                to_attr="image",
            ),
            Prefetch(
                "payments",
                queryset=Payment.objects.order_by("status"),
            ),
            Prefetch(
                "refunds",
                queryset=Refund.objects.order_by("status"),
            ),
        ]

    def _get_defer_fields(self):
        """Fields to defer in queries"""
        return [
            "user",
            "items__product__reviews",
            "items__product__categories",
        ]

    def get_queryset(self):
        queryset = self._get_base_queryset()

        if self.action in ("list", "retrieve", "update", "partial_update"):
            queryset = queryset.prefetch_related(*self._get_prefetch_config())

        if (
            self.action == "retrieve"
            or self.action == "update"
            or self.action == "partial_update"
        ):
            queryset = queryset.filter(id=self.kwargs["pk"])

        return queryset.defer(*self._get_defer_fields())

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save(user=self.request.user)
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
