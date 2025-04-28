from django.contrib import admin
from shopping.cart.models import Cart, CartItem


@admin.register(Cart, CartItem)
class CartAdmin(admin.ModelAdmin):
    pass
