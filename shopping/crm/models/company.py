from django.db import models
from django.conf import settings


class Company(models.Model):
    """
    Represents an organization (company) in the CRM system.

    This model is inspired by Odoo's multi-company support. Each user,
    contact, and lead belongs to a company, which allows the system to
    handle multiple businesses within the same database.

    A company may also have child (subsidiary) companies through the
    'parent' relationship.

    Fields:
        name (CharField):
            The official name of the company. Must be unique.
        logo (ImageField):
            An optional company logo image.
        email (EmailField):
            The main email address of the company.
        phone (CharField):
            The primary phone number of the company.
        website (URLField):
            The company's website URL.
        street (CharField):
            Street address line for the company headquarters.
        city (CharField):
            City of the company address.
        state (CharField):
            State, province, or region of the company address.
        country (CharField):
            Country where the company is located.
        zip_code (CharField):
            Postal or ZIP code of the company address.
        currency (CharField):
            Default currency for financial transactions (e.g., USD, EUR).
        timezone (CharField):
            Timezone in which the company primarily operates.
        parent (ForeignKey to Company):
            Optional link to a parent company, useful for subsidiaries.
        created_at (DateTimeField):
            Timestamp when the company record was created.
        updated_at (DateTimeField):
            Timestamp when the company record was last updated.
    """

    name = models.CharField(max_length=255, unique=True)
    logo = models.ImageField(upload_to="company_logos/", blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    street = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True)

    currency = models.CharField(max_length=10, default="USD")
    timezone = models.CharField(max_length=50, default="UTC")

    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subsidiaries",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
