from rest_framework import serializers
from shopping.order.models import Order


class DashboardOrderListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = [
            "pk",
            "status",
            "order_number",
            "created_at",
            "updated_at",
            "total_amount",
        ]
