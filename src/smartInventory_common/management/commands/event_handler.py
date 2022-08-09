import json

from django.conf import settings
from django.core.management import BaseCommand
from django.core.cache import cache

from smartInventory_common.communication import EventsHandler, RequestsBackend
from smartInventory_common.utils import common_logger

module_logger = common_logger.getChild("ListenEvents")


class ListenEvents(BaseCommand):
    def __init__(self):
        super(ListenEvents, self).__init__()
        self.queue_name = None

    def on_message(self, channel, method_frame, header_frame, body):
        module_logger.info("Received...")
        data = json.loads(bytes(body).decode("UTF-8"))
        module_logger.info(str(data))
        channel.basic_ack(delivery_tag=method_frame.delivery_tag)

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

    def on_action(self, data):
        raise NotImplemented

    def handle(self, *args, **options):
        event_conn = EventsHandler(settings.RABBITMQ, self.queue_name)

        event_conn.consume(self.on_message)
