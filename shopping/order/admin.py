from django.contrib import admin

from shopping.order.models import Order, Shipping, Payment, OrderItem, Refund


@admin.register(Order, Shipping, Payment, OrderItem, Refund)
class OrderAdmin(admin.ModelAdmin):
    pass
