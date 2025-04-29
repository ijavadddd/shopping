from django.db.models import Prefetch
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.db.models import F

from shopping.order.api.serializers import (
    OrderSerializer,
    OrderCreateSerializer,
    StockValidationError,
)
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
                # Create new payments
                for payment_data in payments_data:
                    Payment.objects.create(order=instance, **payment_data)

            # Update items if provided
            if "items" in serializer.validated_data:
                items_data = serializer.validated_data.pop("items")
                # Track processed items to handle duplicates
                processed_items = {}

                for item_data in items_data:
                    product = item_data["product"]
                    variation = item_data.get("variation")
                    quantity = item_data["quantity"]

                    # Create unique key for product+variation combination
                    key = f"{product.id}_{variation.id if variation else 'none'}"

                    try:
                        # Try to find existing order item
                        order_item = OrderItem.objects.get(
                            order=instance, product=product, variation=variation
                        )

                        # Get current quantity from database
                        current_quantity = OrderItem.objects.values_list(
                            "quantity", flat=True
                        ).get(pk=order_item.pk)

                        # Check if adding quantity would exceed stock
                        if variation:
                            if variation.stock < (current_quantity + quantity):
                                raise StockValidationError(
                                    f"Adding {quantity} would exceed variation stock. Available: {variation.stock}"
                                )
                            # Reduce stock
                            variation.stock = F("stock") - quantity
                            variation.save()
                        else:
                            if product.stock < (current_quantity + quantity):
                                raise StockValidationError(
                                    f"Adding {quantity} would exceed product stock. Available: {product.stock}"
                                )
                            # Reduce stock
                            product.stock = F("stock") - quantity
                            product.save()

                        # Update quantity
                        order_item.quantity = F("quantity") + quantity
                        order_item.save()
                        processed_items[key] = order_item

                    except OrderItem.DoesNotExist:
                        if key not in processed_items:
                            # Check if product has enough stock
                            if variation:
                                if variation.stock < quantity:
                                    raise StockValidationError(
                                        f"Not enough stock for variation {variation.id}. Available: {variation.stock}"
                                    )
                                # Reduce stock
                                variation.stock = F("stock") - quantity
                                variation.save()
                            else:
                                if product.stock < quantity:
                                    raise StockValidationError(
                                        f"Not enough stock for product {product.id}. Available: {product.stock}"
                                    )
                                # Reduce stock
                                product.stock = F("stock") - quantity
                                product.save()

                            # Create new order item
                            order_item = OrderItem.objects.create(
                                order=instance, **item_data
                            )
                            processed_items[key] = order_item
                        else:
                            # Update existing item's quantity
                            order_item = processed_items[key]
                            current_quantity = OrderItem.objects.values_list(
                                "quantity", flat=True
                            ).get(pk=order_item.pk)

                            # Check if adding quantity would exceed stock
                            if variation:
                                if variation.stock < (current_quantity + quantity):
                                    raise StockValidationError(
                                        f"Adding {quantity} would exceed variation stock. Available: {variation.stock}"
                                    )
                                # Reduce stock
                                variation.stock = F("stock") - quantity
                                variation.save()
                            else:
                                if product.stock < (current_quantity + quantity):
                                    raise StockValidationError(
                                        f"Adding {quantity} would exceed product stock. Available: {product.stock}"
                                    )
                                # Reduce stock
                                product.stock = F("stock") - quantity
                                product.save()

                            order_item.quantity = F("quantity") + quantity
                            order_item.save()

            instance.save()

        # Refresh the instance to get latest data
        instance.refresh_from_db()
        # Get fresh serializer with updated data
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
