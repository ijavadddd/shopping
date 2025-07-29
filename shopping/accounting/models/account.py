from django.db import models


class AccountType(models.Model):
    """
    AccountType Model

    Summary:
        Defines the classification of accounts within the Chart of Accounts.
        It categorizes accounts into logical groups for reporting and bookkeeping,
        such as Assets, Liabilities, Income, Expenses, or Equity. This mirrors
        Odoo's "Account Types".

    Fields:
        name (CharField):
            The name of the account type.
            Example: "Assets", "Expenses", "Liabilities".

        description (TextField):
            Optional free-text description to clarify the purpose or use case
            of this account type.
    """

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Account(models.Model):
    """
    Account Model

    Summary:
        Represents an account in the Chart of Accounts.
        Each Journal Item must be linked to an Account.
        Inspired by Odoo's "Chart of Accounts", this is the core structure
        for double-entry accounting.

    Fields:
        code (CharField):
            A unique short code to identify the account.
            Example: "1010" for a Bank Account.

        name (CharField):
            Full descriptive name of the account.
            Example: "Cash", "Accounts Receivable", "Sales Revenue".

        account_type (ForeignKey → AccountType):
            Links the account to its type category
            (e.g., Assets, Income, Expenses).

        is_active (BooleanField):
            Determines if this account is available for posting transactions.
            Inactive accounts remain in history but cannot be used in new entries.
    """

    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    account_type = models.ForeignKey(AccountType, on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} - {self.name}"
