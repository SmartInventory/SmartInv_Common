from django.db import models
from django.utils.translation import gettext_lazy as _


class JobStatus(models.TextChoices):
    """Async Job Type enum"""

    ONGOING = "ONG", _("Ongoing")
    STUCK = "STU", _("Stuck")
    COMPLETED = "COM", _("Completed")
    SENT = "SEN", _("Sent")
    FAILED = "FAI", _("Failed")
