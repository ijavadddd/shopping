from django.db.models import Prefetch, OuterRef, Subquery
from shopping.product.models import Product, Category
from shopping.product.models import ProductImage
from shopping.product.models import Review
from shopping.product.models import ProductVariation, ProductAttribute
import logging


logger = logging.getLogger("selector")


def product_list():
    queryset = Product.objects.filter(is_active=True)
    prefetch_args = []

    prefetch_args.append(
        Prefetch(
            "attributes",
            queryset=ProductAttribute.objects.select_related(
                "attribute", "attribute__attribute_type"
            ),
        )
    )

    prefetch_args.append(
        Prefetch(
            "variations",
            queryset=ProductVariation.objects.select_related(
                "attribute", "attribute__attribute_type"
            ),
        )
    )

    featured_image_subquery = (
        ProductImage.objects.filter(product=OuterRef("pk"))
        .order_by("-is_featured", "id")
        .values("image")[:1]
    )  # change "image" to your field

    queryset = queryset.annotate(image=Subquery(featured_image_subquery))

    if prefetch_args:
        queryset = queryset.prefetch_related(*prefetch_args)

    logger.info(queryset)
    return queryset.select_related("vendor")
