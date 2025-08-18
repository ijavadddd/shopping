from django.db.models import Prefetch, OuterRef, Subquery
from shopping.product.models import Product, Category
from shopping.product.models import ProductImage
from shopping.product.models import Review
from shopping.product.models import ProductVariation, ProductAttribute
import logging


logger = logging.getLogger("selector")


def product_list():
    try:
        queryset = Product.objects.filter(is_active=True).select_related("vendor")

        # Featured image annotation
        featured_image_subquery = (
            ProductImage.objects.filter(product=OuterRef("pk"))
            .order_by("-is_featured", "id")
            .values("image")[:1]
        )
        queryset = queryset.annotate(image=Subquery(featured_image_subquery))

        # Prefetch attributes with related attribute and type
        attributes_qs = ProductAttribute.objects.select_related(
            "attribute", "attribute__attribute_type"
        )
        variations_qs = ProductVariation.objects.select_related(
            "attribute", "attribute__attribute_type"
        )

        queryset = queryset.prefetch_related(
            Prefetch("attributes", queryset=attributes_qs),
            Prefetch("variations", queryset=variations_qs),
        )
        logger.debug(str(queryset.query))
        return queryset
    except Exception as e:
        logger.error(f"while fetching product_list, Exception: {e}")


def product_detail():
    try:
        # Prefetch querysets with ordering
        attributes_qs = ProductAttribute.objects.select_related(
            "attribute", "attribute__attribute_type"
        )
        variations_qs = ProductVariation.objects.select_related(
            "attribute", "attribute__attribute_type"
        ).order_by("price_modifier")
        images_qs = ProductImage.objects.order_by("-is_featured")

        queryset = (
            Product.objects.filter(is_active=True)
            .select_related("vendor", "category")
            .prefetch_related(
                Prefetch("attributes", queryset=attributes_qs),
                Prefetch("variations", queryset=variations_qs),
                Prefetch("images", queryset=images_qs),
                "reviews__user",
            )
        )
        logger.debug(str(queryset.query))
        return queryset
    except Exception as e:
        logger.error(f"while fetching product_detail, Exception: {e}")
        return None
