from django.contrib import admin

from shopping.product.models import Category
from shopping.product.models import Product
from shopping.product.models import ProductCategory
from shopping.product.models import ProductImage
from shopping.product.models import Variation


@admin.register(Category, Variation, ProductCategory, ProductImage)
class WholeTestAdmin(admin.ModelAdmin):
    pass


class ProductCategoryInline(
    admin.TabularInline,
):  # or admin.StackedInline for different layout
    model = ProductCategory
    extra = 1  # Number of empty forms to display
    raw_id_fields = ("category",)  # Useful if you have many categories

    # Optional: customize how the depth field is displayed
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == "depth":
            kwargs["initial"] = 0  # Default depth
            kwargs["disabled"] = True  # Make it read-only since it's auto-calculated
        return super().formfield_for_dbfield(db_field, request, **kwargs)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductCategoryInline]
