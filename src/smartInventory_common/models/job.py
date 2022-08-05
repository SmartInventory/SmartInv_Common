import uuid

from django.db import models
from django.utils import timezone

from smartInventory_common.utils.job import JobStatus


class Job(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    pod_id = models.CharField(max_length=255, editable=False)

    start_date = models.DateTimeField(editable=False, auto_created=True, default=timezone.now)

    job_type = models.CharField(max_length=50, editable=False)

    end_date = models.DateTimeField(null=True, blank=True)

    job_status = models.CharField(max_length=3, choices=JobStatus.choices, default=JobStatus.SENT)

    last_update = models.DateTimeField(default=timezone.now, editable=False)

    logs = models.TextField(max_length=255, null=True, blank=True)

    """TODO : Add 'triggered_by'"""

    class Meta:
        abstract = True

    def append_logs(self, new_logs):
        self.logs = str(new_logs) + "\n" + str(self.logs)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.last_update = timezone.now()
        if self.job_status == JobStatus.COMPLETED or self.job_status == JobStatus.FAILED and not self.end_date:
            self.end_date = timezone.now()
        return super(Job, self).save(force_insert=False, force_update=False, using=None, update_fields=None)
