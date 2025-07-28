from django.contrib import admin

from shopping.product.models import (
    Category,
    ProductImage,
    Product,
    AttributeType,
    AttributeValue,
    ProductVariation,
    Review,
    ProductAttribute,
)


@admin.register(
    Category,
    ProductImage,
    AttributeType,
    AttributeValue,
    ProductVariation,
    Review,
    ProductAttribute,
)
class WholeTestAdmin(admin.ModelAdmin):
    pass


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    pass
