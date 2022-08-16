from django.db import models
from django.utils.translation import gettext_lazy as _


class UserRoles(models.TextChoices):
    ADMINISTRATOR = "AD", _("Administrator")
    MANAGER = "MA", _("Manager")
    STUDENT = "ST", _("Student")
    SYSTEM = "SYS", _("System")
