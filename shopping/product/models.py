from django.db import models
from django.conf import settings
from minio_storage.storage import MinioMediaStorage
from mptt.models import MPTTModel, TreeForeignKey

from shopping.users.models import User


class Category(MPTTModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    parent = TreeForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )
    image = models.ImageField(
        upload_to="images/category_images/",
        blank=True,
        null=True,
        storage=MinioMediaStorage(),
    )

    class Meta:
        verbose_name_plural = "Categories"

    class MPTTMeta:
        order_insertion_by = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="products"
    )
    discounted_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
    )
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    vendor = models.ForeignKey(User, related_name="products", on_delete=models.CASCADE)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        related_name="images",
        on_delete=models.CASCADE,
    )
    image = models.ImageField(
        upload_to="images/product_images/",
        storage=MinioMediaStorage(),
    )
    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ("-is_featured",)

    def __str__(self):
        return f"Image for {self.product.name}"


class AttributeType(models.Model):
    """
    Defines types of attributes (Color, Size, Material, etc.)
    """

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    display_type = models.CharField(
        max_length=20,
        choices=[
            ("dropdown", "Dropdown"),
            ("color_swatch", "Color Swatch"),
            ("text", "Text"),
        ],
        default="dropdown",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class AttributeValue(models.Model):
    """
    Possible values for attributes
    """

    attribute_type = models.ForeignKey(
        AttributeType, related_name="values", on_delete=models.CASCADE
    )
    value = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    hex_code = models.CharField(max_length=8, blank=True, null=True)

    class Meta:
        unique_together = ("attribute_type", "slug")
        ordering = ["attribute_type", "value"]

    def __str__(self):
        return f"{self.attribute_type.name}: {self.value}"


class ProductAttribute(models.Model):
    """
    Links attributes to products with price modifiers
    """

    product = models.ForeignKey(
        "Product", related_name="attributes", on_delete=models.CASCADE
    )
    attribute = models.ForeignKey(
        AttributeValue, on_delete=models.CASCADE, null=True, blank=True
    )

    class Meta:
        unique_together = ("product", "attribute")

    def __str__(self):
        return f"{self.product.name} - {self.attribute}"


class ProductVariation(models.Model):
    """
    Links attributes to products with price modifiers
    """

    product = models.ForeignKey(
        "Product", related_name="variations", on_delete=models.CASCADE
    )
    attribute = models.ForeignKey(
        AttributeValue, on_delete=models.CASCADE, null=True, blank=True
    )
    price_modifier = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    stock = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("product", "attribute")

    def __str__(self):
        return f"{self.product.name} - {self.attribute}"


class Review(models.Model):
    product = models.ForeignKey(
        Product,
        related_name="reviews",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("product", "user")

    def __str__(self):
        return f"Review by {self.user.username} for {self.product.name}"
