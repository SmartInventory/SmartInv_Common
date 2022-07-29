import json

import pika


class PublishEvents:
    def __init__(self, parameters: dict, queue_name, exchange=None):
        credentials = pika.PlainCredentials(parameters["USERNAME"], parameters["PASSWORD"])

        parameters = pika.ConnectionParameters(
            host=parameters["HOST"], port=parameters["PORT"], credentials=credentials, virtual_host="/event_handler"
        )
        self.exchange = exchange or ""
        self.parameters = parameters
        self.queue_name = queue_name
        self.connection = None
        self.channel = None

    def init_connexion(self):
        self.connection = pika.BlockingConnection(self.parameters)
        self.channel = self.connection.channel()

    def send_packet(self, data: dict):
        json_dump = json.dumps(data)

        self.channel.basic_publish(
            self.exchange,
            self.queue_name,
            json_dump.encode("UTF-8"),
            pika.BasicProperties(content_type="application/json"),
        )
