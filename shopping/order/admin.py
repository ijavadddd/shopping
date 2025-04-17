from django.contrib import admin

from shopping.order.models import Order, Shipping, Payment, OrderItem


@admin.register(Order, Shipping, Payment, OrderItem)
class OrderAdmin(admin.ModelAdmin):
    pass
