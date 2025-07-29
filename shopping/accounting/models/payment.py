from django.db import models
from django.conf import settings
from shopping.crm.models.contact import Contact
from .journal import Journal
from .invoice import Invoice


class Payment(models.Model):
    """
    Summary:
        Represents a payment transaction (either inbound from a customer
        or outbound to a vendor). Payments can reconcile with one or more invoices.
        Equivalent to Odoo's "Account Payment".

    Fields:
        type (ChoiceField):
            The type of payment.
            Options: Inbound (customer payments), Outbound (vendor payments).

        contact (ForeignKey → Contact):
            The customer or vendor associated with the payment.

        journal (ForeignKey → Journal):
            The journal used to record the payment.
            Example: "Bank Journal".

        amount (DecimalField):
            The amount of the payment.

        date (DateField):
            The date the payment was made or received.

        invoices (ManyToManyField → Invoice):
            The invoices that this payment reconciles.

        created_by (ForeignKey → User):
            The system user who recorded the payment.
    """

    PAYMENT_TYPES = [
        ("inbound", "Inbound Payment"),
        ("outbound", "Outbound Payment"),
    ]

    type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    journal = models.ForeignKey(Journal, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    invoices = models.ManyToManyField(Invoice, blank=True, related_name="payments")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_payments",
    )

    def __str__(self):
        return f"{self.get_type_display()} {self.amount} on {self.date}"
