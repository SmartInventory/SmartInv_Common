import json
import sys

from django.conf import settings
from django.core.management import BaseCommand
from django.core.cache import cache

from smartInventory_common.communication import EventsHandler, RequestsBackend


class ListenEvents(BaseCommand):
    def __init__(self):
        super(ListenEvents, self).__init__()
        self.queue_name = None

    def on_message(self, channel, method_frame, header_frame, body):
        sys.stdout.write("Received...")
        data = json.loads(bytes(body).decode("UTF-8"))
        sys.stdout.write(str(data)+"\n")
        channel.basic_ack(delivery_tag=method_frame.delivery_tag)

        if "action" in data:
            if data["action"] == "PURGE":
                sys.stdout.write("purge cache\n")
                cache.clear()
            elif data["action"] == "SET" and "payload" in data:
                payload = data["payload"]
                if "id" in data and "type" in data:
                    sys.stdout.write("set cache\n")
                    cache.set(RequestsBackend.get_cache_key(data["type"], data["id"]), payload)
                    sys.stdout.write(RequestsBackend.get_cache_key(data["type"], data["id"])+"\n")
            else:
                if "job_id" not in data:
                    sys.stdout.write("NO JOB ID\n")
                    return
                self.on_action(data)  # Actions will be handled by the system itself

    def on_action(self, data):
        raise NotImplemented

    def handle(self, *args, **options):
        event_conn = EventsHandler(settings.RABBITMQ, self.queue_name)

        event_conn.consume(self.on_message)
