from django.db import models
from django.conf import settings
from .account import Account


class Journal(models.Model):
    """
    Summary:
        Represents categories used to group accounting transactions.
        Journals define the source of transactions in double-entry bookkeeping.
        Similar to Odoo journals like Sales, Purchases, Bank, or Cash.

    Fields:
        name (CharField):
            The full descriptive name of the journal.
            Example: "Sales Journal", "Bank Journal".

        code (CharField):
            A short unique code for quick identification.
            Example: "SAL" for Sales Journal.

        type (ChoiceField):
            Defines the type of journal.
            Options include: Sales, Purchases, Bank, Cash, General.

        default_debit_account (ForeignKey → Account):
            Default debit account for transactions posted in this journal.
            Example: "Accounts Receivable" for a Sales Journal.

        default_credit_account (ForeignKey → Account):
            Default credit account for transactions posted in this journal.
            Example: "Sales Revenue" for a Sales Journal.
    """

    JOURNAL_TYPES = [
        ("sale", "Sales"),
        ("purchase", "Purchases"),
        ("bank", "Bank"),
        ("cash", "Cash"),
        ("general", "General"),
    ]

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    type = models.CharField(max_length=20, choices=JOURNAL_TYPES)
    default_debit_account = models.ForeignKey(
        "accounting.Account",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="debit_journals",
    )
    default_credit_account = models.ForeignKey(
        "accounting.Account",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="credit_journals",
    )

    def __str__(self):
        return f"{self.code} - {self.name}"


class JournalEntry(models.Model):
    """
    Summary:
        Represents an individual debit or credit line within a Journal Entry.
        Multiple Journal Items together form a balanced Journal Entry.
        This corresponds to Odoo's "Account Move Line".

    Fields:
        entry (ForeignKey → JournalEntry):
            The parent journal entry that this line belongs to.

        account (ForeignKey → Account):
            The account where the line is posted.

        partner (ForeignKey → Contact):
            The contact (customer/vendor) associated with the transaction line.

        debit (DecimalField):
            The debit amount for the line.
            Must equal the sum of credits in the entry.

        credit (DecimalField):
            The credit amount for the line.
            Must equal the sum of debits in the entry.

        description (CharField):
            Free-text field describing the nature of the transaction line.
            Example: "Payment for Invoice INV-2025-001".
    """

    date = models.DateField()
    reference = models.CharField(max_length=200, blank=True, null=True)
    journal = models.ForeignKey(Journal, on_delete=models.PROTECT)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_entries",
    )
    posted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Entry {self.id} on {self.date}"


class JournalItem(models.Model):
    """
    Lines of a journal entry.
    Must always balance (sum(debit) == sum(credit)).
    """

    entry = models.ForeignKey(
        JournalEntry, on_delete=models.CASCADE, related_name="lines"
    )
    account = models.ForeignKey(Account, on_delete=models.PROTECT)
    partner = models.ForeignKey(
        "crm.Contact", on_delete=models.SET_NULL, null=True, blank=True
    )
    debit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    description = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.account.name} | Debit {self.debit} Credit {self.credit}"
