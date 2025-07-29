from django.db import models


class PipelineStage(models.Model):
    """
    Represents a sales pipeline stage in the CRM system.

    In Odoo, opportunities move through a customizable sales pipeline
    represented by stages (e.g., New, Qualified, Proposal, Negotiation, Won, Lost).
    This model allows administrators to define, order, and manage those stages.

    Fields:
        name (CharField):
            The display name of the stage (e.g., 'Qualified', 'Proposal Sent').
        sequence (PositiveIntegerField):
            Determines the order in which stages are displayed.
            Lower numbers appear earlier in the pipeline.
        probability (FloatField):
            Default winning probability (%) assigned to opportunities in this stage.
            Can be manually overridden on individual opportunities.
        is_won (BooleanField):
            Whether this stage is considered a winning stage.
        is_lost (BooleanField):
            Whether this stage is considered a losing stage.
        fold (BooleanField):
            Whether this stage is folded (collapsed) by default in the pipeline view.
        description (TextField):
            Optional description of the stage for internal reference.
        created_at (DateTimeField):
            Timestamp when the stage was created.
        updated_at (DateTimeField):
            Timestamp when the stage was last updated.
    """

    name = models.CharField(max_length=255, unique=True)
    sequence = models.PositiveIntegerField(
        default=1, help_text="Order of the stage in the pipeline."
    )
    probability = models.FloatField(
        default=0.0, help_text="Default winning probability (%) for this stage."
    )
    is_won = models.BooleanField(
        default=False, help_text="Marks the stage as a winning stage."
    )
    is_lost = models.BooleanField(
        default=False, help_text="Marks the stage as a losing stage."
    )
    fold = models.BooleanField(
        default=False, help_text="Fold this stage by default in Kanban view."
    )
    description = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sequence"]

    def __str__(self):
        return f"{self.sequence}. {self.name}"
