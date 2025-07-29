from django.db import models
from django.conf import settings
from .company import Company
from .contact import Contact
from .opportunity import Opportunity
from .activity_type import ActivityType


class Task(models.Model):
    """
    Represents a scheduled task or to-do activity in the CRM system.

    In Odoo, tasks (or activities) are used for reminders, follow-ups,
    and planned actions such as sending an email, making a phone call,
    or preparing a meeting. A Task can be linked to a company, contact,
    or opportunity, and has a due date, priority, and completion status.

    Fields:
        subject (CharField):
            Title of the task (e.g., 'Follow-up call', 'Send proposal').
        description (TextField):
            Detailed notes about the task.
        due_date (DateTimeField):
            The deadline by which the task should be completed.
        completed (BooleanField):
            Whether the task has been marked as completed.
        priority (CharField):
            Priority of the task: Low, Normal, High.
        related_company (ForeignKey to Company):
            The company this task is associated with.
        related_contact (ForeignKey to Contact):
            The contact this task is associated with.
        related_opportunity (ForeignKey to Opportunity):
            The opportunity this task is associated with.
        activity_type (ForeignKey to ActivityType):
            The category of task (Call, Email, Meeting, etc.).
        assigned_to (ForeignKey to AUTH_USER_MODEL):
            User responsible for completing the task.
        created_by (ForeignKey to AUTH_USER_MODEL):
            User who created the task.
        created_at (DateTimeField):
            Timestamp when the task was created.
        updated_at (DateTimeField):
            Timestamp when the task was last updated.
    """

    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("normal", "Normal"),
        ("high", "High"),
    ]

    subject = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    due_date = models.DateTimeField()
    completed = models.BooleanField(default=False)
    priority = models.CharField(
        max_length=10, choices=PRIORITY_CHOICES, default="normal"
    )

    related_company = models.ForeignKey(
        Company, on_delete=models.CASCADE, null=True, blank=True, related_name="tasks"
    )
    related_contact = models.ForeignKey(
        Contact, on_delete=models.CASCADE, null=True, blank=True, related_name="tasks"
    )
    related_opportunity = models.ForeignKey(
        Opportunity,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="tasks",
    )
    activity_type = models.ForeignKey(
        ActivityType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_tasks",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["completed", "priority", "due_date"]

    def __str__(self):
        return f"{self.subject} (Due: {self.due_date.strftime('%Y-%m-%d')})"
