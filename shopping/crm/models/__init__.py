# crm/models/__init__.py

from .company import Company
from .contact import Contact
from .lead import Lead
from .opportunity import Opportunity
from .interaction import Interaction

__all__ = [
    "Company",
    "Contact",
    "Lead",
    "Opportunity",
    "Interaction",
]
