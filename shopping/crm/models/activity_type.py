from django.db import models


class ActivityType(models.Model):
    """
    Represents a type of activity or interaction in the CRM system.

    In Odoo, activity types define the categories of interactions
    (e.g., 'Call', 'Email', 'Meeting', 'Task'). They help sales teams
    plan and track communications with leads, opportunities, and contacts.

    Fields:
        name (CharField):
            Display name of the activity type (e.g., 'Phone Call', 'Meeting').
        category (CharField):
            Logical category grouping (e.g., 'phone', 'email', 'meeting', 'todo').
        icon (CharField):
            Optional icon CSS class or identifier for UI display.
        default_summary (CharField):
            Suggested summary or title when creating this activity.
        is_active (BooleanField):
            Indicates whether this activity type is active and can be used.
        sequence (PositiveIntegerField):
            Determines the display order in dropdowns and forms.
        created_at (DateTimeField):
            Timestamp when the activity type was created.
        updated_at (DateTimeField):
            Timestamp when the activity type was last updated.
    """

    CATEGORY_CHOICES = [
        ("call", "Phone Call"),
        ("email", "Email"),
        ("meeting", "Meeting"),
        ("todo", "To-Do / Task"),
        ("other", "Other"),
    ]

    name = models.CharField(max_length=255, unique=True)
    category = models.CharField(
        max_length=50, choices=CATEGORY_CHOICES, default="other"
    )
    icon = models.CharField(
        max_length=100, blank=True, null=True, help_text="Optional UI icon class"
    )
    default_summary = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    sequence = models.PositiveIntegerField(default=10)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sequence", "name"]

    def __str__(self):
        return self.name
