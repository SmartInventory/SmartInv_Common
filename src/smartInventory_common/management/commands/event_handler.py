import json

from django.conf import settings
from django.core.management import BaseCommand
from django.core.cache import cache

from smartInventory_common.communication import EventsHandler, RequestsBackend
from smartInventory_common.utils import common_logger
from smartInventory_common.utils.job import JobStatus

module_logger = common_logger.getChild("EventHandler")


class EventHandler(BaseCommand):
    def __init__(self, queue_name, job_model, rabbitmq_conn):
        super(EventHandler, self).__init__()
        self.queue_name = queue_name
        self.job_model = job_model
        self.rabbitmq_conn = rabbitmq_conn

        if not rabbitmq_conn or not job_model or not queue_name:
            raise NotImplementedError

    def on_job_update(self, data):
        if self.job_model is None:
            raise ValueError("JobModelMissing")
        try:
            job = self.job_model.objects.get(id=data["job_id"])

            job.job_status = data["job_status"]
            job.append_logs(data["logs"])

            job.save()
        except self.job_model.DoesNotExist:
            raise ValueError("Job not found %s" % data["job_id"])

    def check_related_job_ok(self, job_id, related_job):
        job = self.job_model.objects.get(id=related_job)
        if job.job_status != JobStatus.COMPLETED:
            self.rabbitmq_conn.send_job_update(job_id, JobStatus.FAILED, "Related job not completed %s" % related_job)
            return False
        return True

    def on_update_attribute(self, couchdb_attributes, job_id, attribute_name, attribute_new_name):
        """Update all the attributes names"""
        self.rabbitmq_conn.send_job_update(job_id, JobStatus.ONGOING)
        attributes = couchdb_attributes.find_attribute(attribute_name)
        try:
            total = len(attributes["docs"])
            self.rabbitmq_conn.send_job_update(job_id, JobStatus.ONGOING, f"Total to update {total}")
            done = couchdb_attributes.update_attributes_name(attributes, attribute_name, attribute_new_name)
            if done == total:
                self.rabbitmq_conn.send_job_update(job_id, JobStatus.COMPLETED, f"Done {done}/{total}")
            else:
                raise Exception("Not all attributes where updated")
        except Exception as e:
            self.rabbitmq_conn.send_job_update(job_id, JobStatus.FAILED, str(e.args))

    def on_delete_attribute(self, couchdb_attributes, job_id, attribute_name):
        """Remove attribute from database"""
        self.rabbitmq_conn.send_job_update(job_id, JobStatus.ONGOING)
        attributes = couchdb_attributes.find_attribute(attribute_name)
        try:
            total = len(attributes["docs"])
            self.rabbitmq_conn.send_job_update(job_id, JobStatus.ONGOING, f"Total to delete {total}")
            done = couchdb_attributes.delete_attributes_name(attributes, attribute_name)
            if done == total:
                self.rabbitmq_conn.send_job_update(job_id, JobStatus.COMPLETED, f"Done {done}/{total}")
            else:
                raise Exception("Not all attributes where updated")
        except Exception as e:
            self.rabbitmq_conn.send_job_update(job_id, JobStatus.FAILED, str(e.args))

    def on_message(self, channel, method_frame, header_frame, body):
        module_logger.info("Received...")
        data = json.loads(bytes(body).decode("UTF-8"))
        module_logger.info(str(data))

        try:
            if "action" in data:
                if data["action"] == "PURGE":
                    module_logger.info("purge cache")
                    cache.clear()
                elif data["action"] == "SET" and "payload" in data:
                    payload = data["payload"]
                    if "id" in data and "type" in data:
                        module_logger.info("set cache")
                        cache.set(RequestsBackend.get_cache_key(data["type"], data["id"]), payload)
                        module_logger.info(RequestsBackend.get_cache_key(data["type"], data["id"]) + "")
                else:
                    if "job_id" not in data:
                        module_logger.warn("NO JOB ID")
                        module_logger.warn(body)
                        return
                    self.on_action(data)  # Actions will be handled by the system itself
            channel.basic_ack(delivery_tag=method_frame.delivery_tag)
        except Exception as e:
            channel.basic_nack(delivery_tag=method_frame.delivery_tag, requeue=False)
            raise e

    def on_action(self, data):
        raise NotImplemented

    def handle(self, *args, **options):
        event_conn = EventsHandler(settings.RABBITMQ, self.queue_name)

        event_conn.consume(self.on_message)
