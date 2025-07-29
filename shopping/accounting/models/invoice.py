from django.db import models
from django.conf import settings
from shopping.crm.models.company import Company
from shopping.crm.models.contact import Contact
from .journal import Journal
from .tax import Tax


class Invoice(models.Model):
    """
    Summary:
        Represents a customer invoice or vendor bill.
        Tracks billing details, taxes, and payment status.
        Equivalent to Odoo's "Account Move" with type fields.

    Fields:
        company (ForeignKey → Company):
            The company issuing the invoice.

        contact (ForeignKey → Contact):
            The customer or vendor associated with the invoice.

        type (ChoiceField):
            The type of invoice.
            Options: Customer Invoice, Customer Credit Note,
                     Vendor Bill, Vendor Credit Note.

        date (DateField):
            The date of the invoice.

        due_date (DateField):
            The date by which payment is expected.

        journal (ForeignKey → Journal):
            Journal where the invoice is posted.

        total_amount (DecimalField):
            The total value of the invoice, including taxes.

        taxes (ManyToManyField → Tax):
            Taxes applied to this invoice.

        posted (BooleanField):
            Indicates whether the invoice has been validated and posted.

        created_by (ForeignKey → User):
            The system user who created the invoice.
    """

    INVOICE_TYPES = [
        ("out_invoice", "Customer Invoice"),
        ("out_refund", "Customer Credit Note"),
        ("in_invoice", "Vendor Bill"),
        ("in_refund", "Vendor Credit Note"),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=INVOICE_TYPES)
    date = models.DateField()
    due_date = models.DateField()
    journal = models.ForeignKey(Journal, on_delete=models.PROTECT)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    taxes = models.ManyToManyField(Tax, blank=True)
    posted = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_invoices",
    )

    def __str__(self):
        return f"{self.get_type_display()} {self.id} - {self.contact}"
