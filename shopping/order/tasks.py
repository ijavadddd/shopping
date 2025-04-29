from django_q.tasks import async_task
from django.utils import timezone
from django.db.models import F
from django.db import transaction

from shopping.order.models import Order, OrderItem
from shopping.product.models import Product, ProductVariation


def restore_stock(order_id):
    """
    Restore stock for all items in an order if payment is not completed
    """
    try:
        order = Order.objects.get(id=order_id)

        # Only restore stock if payment is not completed
        if not order.payments.filter(status="completed").exists():
            with transaction.atomic():
                for item in order.items.all():
                    if item.variation:
                        item.variation.stock = F("stock") + item.quantity
                        item.variation.save()
                    else:
                        item.product.stock = F("stock") + item.quantity
                        item.product.save()
    except Order.DoesNotExist:
        pass
