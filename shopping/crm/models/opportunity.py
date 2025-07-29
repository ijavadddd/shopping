from django.db import models
from django.conf import settings
from .company import Company
from .contact import Contact
from .lead import Lead
from .pipeline_stage import PipelineStage


class Opportunity(models.Model):
    """
    Represents a qualified sales opportunity in the CRM system.

    Unlike a lead, which is an initial prospect, an opportunity indicates
    a more concrete chance of making a sale. Opportunities belong to a
    customizable pipeline with defined stages.

    Fields:
        lead (ForeignKey to Lead):
            The original lead from which this opportunity was created.
        company (ForeignKey to Company):
            The company associated with this opportunity.
        contact (ForeignKey to Contact):
            The primary contact for the opportunity.
        name (CharField):
            A short descriptive title for the opportunity.
        stage (ForeignKey to PipelineStage):
            The current stage of the opportunity in the pipeline.
        expected_revenue (DecimalField):
            Estimated revenue if the opportunity is successfully closed.
        probability (FloatField):
            Probability (percentage) of winning this opportunity.
            Defaults from the selected pipeline stage.
        closing_date (DateField):
            Expected or actual closing date of the opportunity.
        description (TextField):
            Notes or additional information about the opportunity.
        assigned_to (ForeignKey to AUTH_USER_MODEL):
            Salesperson responsible for this opportunity.
        created_by (ForeignKey to AUTH_USER_MODEL):
            User who created the opportunity record.
        created_at (DateTimeField):
            Timestamp when the opportunity was created.
        updated_at (DateTimeField):
            Timestamp when the opportunity was last updated.
    """

    lead = models.ForeignKey(
        Lead,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="opportunities",
    )
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="opportunities"
    )
    contact = models.ForeignKey(
        Contact,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="opportunities",
    )
    name = models.CharField(max_length=255)
    stage = models.ForeignKey(
        PipelineStage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="opportunities",
    )
    expected_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    probability = models.FloatField(default=0.0, help_text="Winning probability in %")
    closing_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True, null=True)

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_opportunities",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_opportunities",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Auto-fill probability from pipeline stage if not manually set
        if self.stage and self.probability == 0.0:
            self.probability = self.stage.probability
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.stage.name if self.stage else 'No Stage'})"
