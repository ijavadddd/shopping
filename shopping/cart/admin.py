from django.contrib import admin
from shopping.cart.models import Cart, Item


@admin.register(Cart, Item)
class CartAdmin(admin.ModelAdmin):
    pass
