from django.db.models import Prefetch
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db import transaction
from django.db.models import F
from shopping.order.api.serializers import (
    OrderSerializer,
    OrderCreateSerializer,
    StockValidationError,
    ShippingSerializer,
    OrderChartData,
)
from shopping.order.models import (
    Order,
    Payment,
    Refund,
    OrderItem,
    ProductVariation,
    Shipping,
)
from shopping.product.models import ProductImage

from rest_framework import status
from rest_framework.response import Response
from datetime import date, timedelta
from collections import defaultdict
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate


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
                queryset=OrderItem.objects.select_related("product", "variation"),
            )
        )

        # Prefetch product images for items
        prefetch_args.append(
            Prefetch(
                "items__product__images",
                queryset=ProductImage.objects.order_by("-is_featured"),
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
        order = serializer.save(user=self.request.user)
        return Response(
            OrderSerializer(order).data, status=status.HTTP_206_PARTIAL_CONTENT
        )


class AdminOrderAPI(ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = OrderChartData

    def get(self, request):
        today = date.today()
        time_filter = defaultdict(
            lambda: timedelta(days=7),
            {
                "today": 0,
                "1d": timedelta(days=1),
                "7d": timedelta(days=7),
                "30d": timedelta(days=30),
                "90d": timedelta(days=90),
            },
        )
        duration_key = request.query_params.get("period", "7d")
        period = today - time_filter[duration_key]
        last_period = period - time_filter[duration_key]

        queryset = (
            Order.objects.filter(
                created_at__gte=period, status=Order.OrderStatus.COMPLETED.value
            )
            .annotate(day=TruncDate("created_at"))
            .values("day")  # Group by day
            .annotate(count=Count("id"))  # Count orders per day
            .order_by("day")  # order by day ascending (optional)
        )
        total_count = sum(item["count"] for item in queryset)
        last_period_qs = Order.objects.filter(
            created_at__gte=last_period,
            created_at__lt=period,
            status=Order.OrderStatus.COMPLETED.value,
        ).aggregate(count=Count("id"))
        last_count = last_period_qs["count"] or 0
        growth_percent = 0
        if last_count > 0:
            growth_percent = ((total_count - last_count) / last_count) * 100

        data = {
            "days": list(queryset),
            "total_count": total_count,
            "growth_percent": int(growth_percent),
        }

        serializer = OrderChartData(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class ShippingListAPIView(ListAPIView):
    serializer_class = ShippingSerializer
    queryset = Shipping.objects.all()
