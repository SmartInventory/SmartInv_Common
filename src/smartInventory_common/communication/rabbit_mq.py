import json
from django.conf import settings

import pika
from pika.exceptions import AMQPConnectionError

from smartInventory_common.utils import common_logger

module_logger = common_logger.getChild("EventHandler")


class EventsHandler:
    def __init__(self, parameters: dict, queue_name, exchange="", virtual_host="/event_handler"):
        credentials = pika.PlainCredentials(parameters["USERNAME"], parameters["PASSWORD"])

        parameters = pika.ConnectionParameters(
            host=parameters["HOST"], port=parameters["PORT"], credentials=credentials, virtual_host=virtual_host
        )
        self.exchange = exchange
        self.parameters = parameters
        self.queue_name = queue_name
        self.connection = None
        self.channel = None

    def init_connexion(self):
        module_logger.info("Init connexion to RabbitMQ queue : %s..." % self.queue_name)
        self.connection = pika.BlockingConnection(self.parameters)
        self.channel = self.connection.channel()
        module_logger.info("Success!")

    def send_cache_update(self, action, comp_type=None, comp_id=None, data=None):
        formatted_data = {"action": action, "id": str(comp_id), "type": comp_type, "payload": data}

        try:
            self.send_packet(formatted_data)
        except AMQPConnectionError:
            module_logger.error("error cache rabbitmq")

    def create_job(self, action, data):
        raise NotImplemented

    def send_job_update(self, job_id, status, logs=None):
        formatted_data = {"action": "JOB_UPDATE", "job_id": job_id, "job_status": status, "logs": logs}
        self.send_packet(formatted_data)

    def send_packet(self, data: dict):
        if hasattr(settings, "TESTING"):
            return
        self.init_connexion()
        json_dump = json.dumps(data)
        module_logger.info("Sending : %s" % json_dump)

        self.channel.basic_publish(
            self.exchange,
            self.queue_name,
            json_dump.encode("UTF-8"),
            pika.BasicProperties(content_type="application/json"),
        )
        return data

    def consume(self, callback):

        self.init_connexion()
        self.channel.queue_declare(self.queue_name, durable=True, auto_delete=False)
        self.channel.basic_consume(self.queue_name, callback, auto_ack=False)

        try:
            module_logger.info("Listening for events on %s..." % self.queue_name)
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.channel.stop_consuming()
        self.connection.close()
