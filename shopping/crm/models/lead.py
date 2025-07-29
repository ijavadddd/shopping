from django.db import models
from django.conf import settings


class Lead(models.Model):
    """
    Represents a potential sales opportunity (lead) in the CRM system.

    A lead is tied to a specific contact and company, and represents an
    opportunity in the sales pipeline. Leads can be tracked, assigned
    to users, and moved through various pipeline stages until they are
    won or lost.

    Fields:
        company (ForeignKey to Company):
            The company this lead belongs to. Supports multi-company usage.
        contact (ForeignKey to Contact):
            The contact associated with this lead. Can be a person or a company.
        title (CharField):
            The title or summary of the lead/opportunity.
        stage (CharField with choices):
            Current stage of the lead in the sales pipeline.
            Choices: new, contacted, qualified, won, lost.
        priority (IntegerField):
            Priority of the lead: 0 = Normal, 1 = High, 2 = Very High.
        expected_revenue (DecimalField):
            Estimated revenue if the lead is won.
        email (EmailField):
            Email associated with the lead (may override the contact's email).
        phone (CharField):
            Phone number associated with the lead.
        description (TextField):
            Additional notes or description of the opportunity.
        created_by (ForeignKey to AUTH_USER_MODEL):
            User who created the lead.
        assigned_to (ForeignKey to AUTH_USER_MODEL):
            User currently assigned to manage the lead.
        created_at (DateTimeField):
            Timestamp when the lead was created.
        deadline (DateField):
            Optional date by which the lead should be closed or followed up.
    """

    company = models.ForeignKey(
        "crm.Company", on_delete=models.CASCADE, related_name="leads"
    )
    contact = models.ForeignKey(
        "crm.Contact",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="leads",
    )

    # Lead details
    title = models.CharField(max_length=255)
    stage = models.CharField(
        max_length=20,
        choices=[
            ("new", "New"),
            ("contacted", "Contacted"),
            ("qualified", "Qualified"),
            ("won", "Won"),
            ("lost", "Lost"),
        ],
        default="new",
    )
    priority = models.IntegerField(default=0, help_text="0=Normal, 1=High, 2=Very High")
    expected_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Communication
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    # Tracking
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_leads",
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_leads",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} ({self.stage})"
