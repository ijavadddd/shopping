from datetime import timedelta

from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from shopping.product.models import Product, ProductVariation
from shopping.users.models import User


class Order(models.Model):
    class OrderStatus(models.TextChoices):
        PENDING = "pending"
        PROCESSING = "processing"
        SHIPPED = "shipped"
        DELIVERED = "delivered"
        CANCELLED = "canceled"
        REFUNDED = "refunded"
        COMPLETED = "completed"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING.value,
    )
    shipping_address = models.TextField()
    billing_address = models.TextField()
    phone = models.CharField(max_length=20)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(editable=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

    def get_absolute_url(self):
        return reverse("order:order-detail", kwargs={"pk": self.pk})


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation = models.ForeignKey(
        ProductVariation,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in order {self.order.id}"


class Payment(models.Model):
    class PaymentStatus(models.TextChoices):
        PENDING = "pending"
        SUCCESS = "success"
        UNSUCCESSFUL = "unsuccessful"

    order = models.ForeignKey(Order, related_name="payments", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=100)
    status = models.CharField(
        max_length=20,
        default=PaymentStatus.PENDING.value,
        choices=PaymentStatus.choices,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.transaction_id} for order {self.order.order_number}"


class Shipping(models.Model):
    order = models.OneToOneField(
        Order,
        related_name="shipping",
        on_delete=models.CASCADE,
    )
    tracking_number = models.CharField(max_length=50)
    carrier = models.CharField(max_length=50)
    estimated_delivery = models.DateField()
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Shipping for order {self.order.order_number}"


class Refund(models.Model):
    class RefundStatus(models.TextChoices):
        REQUESTED = "requested"
        PROCESSING = "processing"
        APPROVED = "approved"
        REJECTED = "rejected"
        COMPLETED = "completed"

    class ReasonStatus(models.TextChoices):
        DEFECTIVE = "defective"
        WRONG_ITEM = "wrong_item"
        UNWANTED = "unwanted"
        QUALITY = "quality"
        OTHER = "other"

    order = models.ForeignKey("Order", on_delete=models.PROTECT, related_name="refunds")
    order_item = models.ForeignKey(
        "OrderItem",
        on_delete=models.PROTECT,
        related_name="refunds",
        null=True,
        blank=True,
    )
    requested_by = models.ForeignKey(
        "users.User",
        on_delete=models.PROTECT,
        related_name="refund_requests",
    )
    processed_by = models.ForeignKey(
        "users.User",
        on_delete=models.PROTECT,
        related_name="processed_refunds",
        null=True,
        blank=True,
    )
    status = models.CharField(
        max_length=20,
        choices=RefundStatus.choices,
        default=RefundStatus.REQUESTED.value,
    )
    reason = models.CharField(
        max_length=20,
        choices=ReasonStatus.choices,
        default=ReasonStatus.OTHER.value,
    )
    notes = models.TextField(blank=True)
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
    )
    refund_method = models.CharField(
        max_length=50,
        choices=(
            ("original", "Original Payment Method"),
            ("credit", "Store Credit"),
            ("other", "Other"),
        ),
        default="original",
    )
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    is_partial = models.BooleanField(default=False)
    quality_rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-requested_at"]
        verbose_name = "Refund"
        verbose_name_plural = "Refunds"

    def __str__(self):
        return f"Refund #{self.id} for Order {self.order.order_number}"

    def save(self, *args, **kwargs):
        if self.status == "completed" and not self.processed_at:
            self.processed_at = timezone.now()
        super().save(*args, **kwargs)

    @property
    def eligible_items(self):
        """Returns queryset of items eligible for refund"""
        return self.order.items.filter(
            refunds__isnull=True,
            shipped_at__gte=timezone.now() - timedelta(days=30),
        )

    def full_refund(self):
        """Marks the refund as full order amount"""
        self.amount = self.order.total
        self.is_partial = False
        self.save()
