from django.contrib import admin

from shopping.order.models import Order, Shipping, Payment, OrderItem, Refund


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("created_at",)


@admin.register(Shipping, Payment, OrderItem, Refund)
class PassAdmin(admin.ModelAdmin):
    pass
