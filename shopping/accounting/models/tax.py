from django.db import models


class Tax(models.Model):
    """
    Summary:
        Represents a tax configuration (e.g., VAT, GST) that can be applied
        to invoices or journal entries. Odoo equivalent: "Account Tax".

    Fields:
        name (CharField):
            The name of the tax.
            Example: "VAT 20%".

        rate (DecimalField):
            The percentage rate of the tax.
            Example: 20.0 for 20%.

        is_active (BooleanField):
            Whether this tax can currently be applied.
            Inactive taxes remain in history but cannot be used in new records.
    """

    name = models.CharField(max_length=100)
    rate = models.DecimalField(max_digits=5, decimal_places=2)  # 19.00 = 19%
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.rate}%)"
