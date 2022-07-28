from django.db import models
from django.utils.translation import gettext_lazy as _


class InspectionType(models.TextChoices):
    """Inspection Type enum"""

    REVISION = "RE", _("Revision")
    MAINTENANCE = "MA", _("Maintenance")
