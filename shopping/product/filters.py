from django_filters import rest_framework as filters

from shopping.product.models import Product, Category


class ProductFilter(filters.FilterSet):
    min_price = filters.NumberFilter(field_name="variations__price", lookup_expr="gte")
    max_price = filters.NumberFilter(field_name="variations__price", lookup_expr="lte")
    name = filters.CharFilter(field_name="name", lookup_expr="icontains")
    categories = filters.CharFilter(
        field_name="category__name", lookup_expr="icontains"
    )

    class Meta:
        model = Product
        fields = [
            # "variations__ price",
            "category__name",
            "name",
        ]

    def filter_queryset(self, queryset):
        """
        Override filter_queryset to handle dynamic attribute filters
        """
        queryset = super().filter_queryset(queryset)

        # Get all attribute type slugs from the request
        attribute_filters = {
            key: value
            for key, value in self.request.query_params.items()
            if key not in self.filters  # Exclude predefined filters
        }

        # Apply attribute filters
        for attr_slug, value_slug in attribute_filters.items():
            queryset = queryset.filter(
                attributes__attribute__attribute_type__slug=attr_slug,
                attributes__attribute__slug=value_slug,
            ).distinct()

        return queryset
