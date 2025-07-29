from django.db import models
from django.conf import settings
from .contact import Contact
from .lead import Lead
from .opportunity import Opportunity


class Interaction(models.Model):
    """
    Represents an interaction (activity) with a contact, lead, or opportunity.

    Interactions are used to track the communication history and engagement
    with potential customers. They can represent calls, emails, meetings,
    or notes, and are always linked to at least one of Contact, Lead,
    or Opportunity.

    Fields:
        contact (ForeignKey to Contact):
            The contact associated with this interaction (if any).
        lead (ForeignKey to Lead):
            The lead associated with this interaction (if any).
        opportunity (ForeignKey to Opportunity):
            The opportunity associated with this interaction (if any).
        interaction_type (CharField with choices):
            Type of interaction. Choices: call, email, meeting, note, task.
        subject (CharField):
            Short subject line describing the interaction.
        details (TextField):
            Full description or notes of the interaction.
        status (CharField with choices):
            Current status of the activity. Choices: planned, done, cancelled.
        scheduled_for (DateTimeField):
            Date and time when the interaction is scheduled to happen.
        completed_at (DateTimeField):
            Date and time when the interaction was completed (if applicable).
        created_by (ForeignKey to AUTH_USER_MODEL):
            User who created the interaction record.
        assigned_to (ForeignKey to AUTH_USER_MODEL):
            User responsible for carrying out the interaction.
        created_at (DateTimeField):
            Timestamp when the interaction was created.
    """

    contact = models.ForeignKey(
        Contact,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="interactions",
    )
    lead = models.ForeignKey(
        Lead,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="interactions",
    )
    opportunity = models.ForeignKey(
        Opportunity,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="interactions",
    )

    interaction_type = models.CharField(
        max_length=20,
        choices=[
            ("call", "Call"),
            ("email", "Email"),
            ("meeting", "Meeting"),
            ("note", "Note"),
            ("task", "Task"),
        ],
    )
    subject = models.CharField(max_length=255)
    details = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("planned", "Planned"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
        ],
        default="planned",
    )
    scheduled_for = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_interactions",
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_interactions",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject} ({self.get_interaction_type_display()})"
