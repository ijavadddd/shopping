from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from shopping.product.models import Product
from shopping.product.models import ProductCategory


@receiver(post_save, sender=Product)
def add_category(sender, instance, created, **kwargs):
    if created:
        return

    def _add_parent():
        # Get all existing categories for the product with their hierarchy
        existing_categories = set(
            instance.categories.values_list("category_id", flat=True),
        )
        new_relationships = []

        # Process each category to find ancestors
        for pc in instance.categories.select_related("category__parent").all():
            current_category = pc.category
            depth = pc.depth

            # Walk up the parent hierarchy
            while current_category.parent:
                current_category = current_category.parent
                depth += 1

                if current_category.id not in existing_categories:
                    new_relationships.append(
                        ProductCategory(
                            product=instance,
                            category=current_category,
                            depth=depth,
                        ),
                    )
                    existing_categories.add(current_category.id)

        if new_relationships:
            ProductCategory.objects.bulk_create(new_relationships)

    transaction.on_commit(_add_parent)
