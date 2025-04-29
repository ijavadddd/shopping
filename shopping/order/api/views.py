from django.db.models import Prefetch
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

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
        return (
            OrderCreateSerializer
            if self.action == "create" or self.action == "partial_update"
            else OrderSerializer
        )

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

        if prefetch_args:
            queryset = queryset.prefetch_related(*prefetch_args)

        return queryset.select_related("shipping", "user")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save(user=self.request.user)
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            # Update order fields
            for attr, value in serializer.validated_data.items():
                if attr not in ["items", "payments", "shipping"]:
                    setattr(instance, attr, value)

            # Update shipping if provided
            if "shipping" in serializer.validated_data:
                shipping_data = serializer.validated_data.pop("shipping")
                for attr, value in shipping_data.items():
                    setattr(instance.shipping, attr, value)
                instance.shipping.save()

            # Update payments if provided
            if "payments" in serializer.validated_data:
                payments_data = serializer.validated_data.pop("payments")
                # Delete existing payments
                instance.payments.all().delete()
                # Create new payments
                for payment_data in payments_data:
                    Payment.objects.create(order=instance, **payment_data)

            # Update items if provided
            if "items" in serializer.validated_data:
                items_data = serializer.validated_data.pop("items")
                # Delete existing items
                instance.items.all().delete()
                # Create new items
                for item_data in items_data:
                    OrderItem.objects.create(order=instance, **item_data)

            instance.save()

        return Response(OrderSerializer(instance).data)
