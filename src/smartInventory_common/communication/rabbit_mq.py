import json
import socket

from django.conf import settings

import pika
from pika.exceptions import AMQPConnectionError, StreamLostError

from smartInventory_common.serializers.job import JobSerializer
from smartInventory_common.utils import common_logger

module_logger = common_logger.getChild("EventHandler")


class EventsHandler:
    def __init__(self, parameters: dict, queue_name, exchange="", virtual_host="/event_handler", job_model=None, app=None):
        credentials = pika.PlainCredentials(parameters["USERNAME"], parameters["PASSWORD"])

        parameters = pika.ConnectionParameters(
            host=parameters["HOST"], port=parameters["PORT"], credentials=credentials, virtual_host=virtual_host
        )
        self.exchange = exchange
        self.parameters = parameters
        self.queue_name = queue_name
        self.connection = None
        self.channel = None
        self.job_model = job_model  # Defined by the application (Django model)
        self.app = app

    def init_connexion(self):
        module_logger.info("Init connexion to RabbitMQ queue : %s..." % self.queue_name)
        self.connection = pika.BlockingConnection(self.parameters)
        self.channel = self.connection.channel()
        module_logger.info("Success!")

    def send_cache_update(self, action, comp_type=None, comp_id=None, data=None):
        formatted_data = {"action": action, "id": str(comp_id), "type": comp_type, "payload": data}

        try:
            self.format_send_packet(formatted_data)
        except AMQPConnectionError:
            module_logger.error("error cache rabbitmq")

    def send_metrics(self, request, response):
        if not self.app:
            raise NotImplementedError
        user = "unknown"
        action = "unknown"
        if hasattr(request, "user"):
            user = str(request.user.id or "unknown")

        if hasattr(response, "renderer_context") and "view" in response.renderer_context and hasattr(
                response.renderer_context["view"], "action"):
            action = response.renderer_context["view"].action

        formatted_data = f'metrics,app={self.app},action="{action}",user="{user}",status_code="{response.status_code}" app={self.app},status_code="{response.status_code}",action="{action}",url="{request.build_absolute_uri()}",user="{user}"'
        try:
            self.send_packet(formatted_data)
        except AMQPConnectionError as e:
            module_logger.error("error metrics rabbitmq")
            module_logger.error(e.args)

    def create_job(self, action, user_id, data):
        if self.job_model is None:
            raise ValueError("JobModelMissing")
        job = self.job_model()
        job.pod_id = socket.gethostname()
        job.job_type = action
        job.logs = str(data)
        job.triggered_by = user_id
        job.save()
        serializer = JobSerializer(job)

        formatted_data = {
            "action": action,
            "user_id": str(job.triggered_by.pk if hasattr(job.triggered_by, "pk") else job.triggered_by),
            "job_id": str(job.pk),
            "payload": data,
        }

        self.format_send_packet(formatted_data)
        return serializer.data

    def send_job_update(self, job_id, status, logs=None):
        formatted_data = {"action": "JOB_UPDATE", "job_id": job_id, "job_status": status, "logs": logs}
        self.format_send_packet(formatted_data)

    def format_send_packet(self, data: dict):
        json_dump = json.dumps(data)
        self.send_packet(json_dump)
        return data

    def send_packet(self, data: str):
        if hasattr(settings, "TESTING"):
            return
        if not self.channel:
            self.init_connexion()
        module_logger.info(
            "Sending on %s : %s"
            % (
                self.queue_name,
                data,
            )
        )

        try:
            self.channel.basic_publish(
                self.exchange,
                self.queue_name,
                data.encode("UTF-8"),
                pika.BasicProperties(content_type="application/json"),
            )
        except StreamLostError as e:
            self.init_connexion()
            raise e

    def consume(self, callback):
        """
        Listening for event on a queue
        :param callback:
        :return:
        """
        if not self.channel:
            self.init_connexion()

        self.channel.queue_declare(self.queue_name, durable=True, auto_delete=False)
        self.channel.basic_consume(self.queue_name, callback, auto_ack=False)

        try:
            module_logger.info("Listening for events on %s..." % self.queue_name)
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.channel.stop_consuming()
        self.connection.close()
