from django.db import models
from django.utils.translation import gettext_lazy as _


class BorrowType(models.TextChoices):
    """Equipment borrowing mode Enum"""

    DIGITAL = "DI", _("Digital")
    IN_LAB = "IL", _("In_lab")
    OUT_LAB = "OL", _("Out_lab")
    NONE = "NO", _("None")
