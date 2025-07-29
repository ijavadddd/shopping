from django.db import models
from django.conf import settings


class Contact(models.Model):
    """
    Represents a contact (person or organization) in the CRM.

    Contacts in this model are equivalent to Odoo's 'partners'.
    A contact can be:
        - A company (is_company=True)
        - An individual person
        - An employee/child contact under a parent company

    Fields:
        name (CharField):
            Full name of the contact or the company name.
        is_company (BooleanField):
            Indicates whether this contact is a company.
        parent (ForeignKey to Contact):
            Optional parent contact. Used when this contact is an individual
            working for a company.
        company (ForeignKey to Company):
            The company record this contact belongs to (multi-company support).
        email (EmailField):
            Primary email address of the contact.
        phone (CharField):
            Landline phone number of the contact.
        mobile (CharField):
            Mobile phone number of the contact.
        website (URLField):
            Contact's or organization's website.
        street (CharField):
            Street address of the contact.
        city (CharField):
            City of the contact's address.
        state (CharField):
            State, province, or region of the contact's address.
        country (CharField):
            Country of the contact's address.
        zip_code (CharField):
            Postal or ZIP code of the contact.
        job_title (CharField):
            The contact's job title, if applicable.
        notes (TextField):
            Free-form notes about the contact.
        created_by (ForeignKey to AUTH_USER_MODEL):
            User who created the contact record.
        created_at (DateTimeField):
            Timestamp when the contact record was created.
    """

    # General info
    name = models.CharField(max_length=255)
    is_company = models.BooleanField(
        default=False, help_text="True if this contact is a company"
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
        help_text="For employees/contacts under a company",
    )

    # Company ownership
    company = models.ForeignKey(
        "crm.Company", on_delete=models.CASCADE, related_name="contacts"
    )

    # Communication
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    mobile = models.CharField(max_length=30, blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    # Address
    street = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=True, null=True)

    # Additional info
    job_title = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_contacts",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
