import time
from datetime import timedelta
from django.core.management import BaseCommand

from smartInventory_common.utils import common_logger
from smartInventory_common.utils.job import JobStatus
from django.db.models.functions import Now

module_logger = common_logger.getChild("HouseKeeping")


class HouseKeeping(BaseCommand):
    def __init__(self, job_model):
        super(HouseKeeping, self).__init__()
        self.job_model = job_model

        if not job_model:
            raise NotImplementedError

    def handle(self, *args, **options):
        if self.job_model is None:
            raise ValueError("JobModelMissing")
        module_logger.info("House keeping started")
        while True:

            sent = self.job_model.objects.filter(
                job_status=JobStatus.SENT, last_update__lt=Now() - timedelta(minutes=5)
            )
            stuck = self.job_model.objects.filter(
                job_status=JobStatus.STUCK, last_update__lt=Now() - timedelta(minutes=5)
            )
            ongoing = self.job_model.objects.filter(
                job_status=JobStatus.ONGOING, last_update__lt=Now() - timedelta(minutes=60)
            )

            for job in sent:
                job.job_status = JobStatus.STUCK
                module_logger.warn(f"Job : {job.pk} SEN TO STUCK")
                job.save()
            for job in stuck:
                job.job_status = JobStatus.FAILED
                module_logger.error(f"Job : {job.pk} STUCK TO FAILED")
                job.append_logs("House keeping : Dead job")
                job.save()
            for job in ongoing:
                job.job_status = JobStatus.FAILED
                module_logger.error(f"Job : {job.pk} ONGOING TO FAILED")
                job.append_logs("House keeping : Dead job")
                job.save()

            updated = len(sent) + len(stuck) + len(ongoing)
            if updated > 0:
                module_logger.info("Jobs updated : %s", (updated))

            time.sleep(60)
