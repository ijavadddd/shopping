from django.db.models import Prefetch
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from shopping.order.api.serializers import OrderSerializer, OrderCreateSerializer
from shopping.order.models import Order, Payment, Refund, OrderItem
from shopping.product.models import ProductImage

from rest_framework import status
from rest_framework.response import Response


class OrderAPIViewSet(ModelViewSet):
    http_method_names = ["get", "post", "patch", "head", "options"]
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = "pk"
    queryset = Order.objects.all()

    def get_serializer_class(self):
        return OrderCreateSerializer if self.action == "create" else OrderSerializer

    def get_queryset(self):
        # Get the filtered queryset first
        queryset = super().get_queryset()
        prefetch_args = []

        # Always prefetch items and their related data
        prefetch_args.append(
            Prefetch(
                "items",
                queryset=OrderItem.objects.select_related(
                    "product",
                ),
            )
        )

        # Prefetch product images for items
        prefetch_args.append(
            Prefetch(
                "items__product__images",
                queryset=ProductImage.objects.order_by("-is_featured"),
                to_attr="image",
            )
        )

        # Prefetch payments ordered by status
        prefetch_args.append(
            Prefetch(
                "payments",
                queryset=Payment.objects.order_by("status"),
            )
        )

        # Prefetch refunds ordered by status
        # prefetch_args.append(
        #     Prefetch(
        #         "refunds",
        #         queryset=Refund.objects.order_by("status"),
        #     )
        # )

        if prefetch_args:
            queryset = queryset.prefetch_related(*prefetch_args)

        return queryset.select_related("shipping", "user")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save(user=self.request.user)
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
