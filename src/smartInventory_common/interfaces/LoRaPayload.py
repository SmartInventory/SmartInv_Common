import json
import re
import time
import uuid
from pika.spec import Basic

from smartInventory_common.utils import common_logger

module_logger = common_logger.getChild("LoRaPayload")

DEVICE_ACTIONS = [
    "STA",  # Student authentication
    "BOR",  # Borrowing
    "INV",  # Inventory Mode
    "OUT",  # Query timed out
]


class LoRaPayload:
    def __init__(self):
        """
        LoRaPayload class : Used to communicate with devices
        """

        self._device_id: str = ""
        self._seq: int = 0
        self._action: str = ""
        self._ttl: int = 0

        self.payload: str = ""
        self.timestamp: int = int(time.time())

        self.correlation_id = uuid.uuid4().hex

        self.parse_regex = re.compile("^<(\w+)>(\d{2})(\d?)([A-Z]{3})([:_]?)(.*)$")

    def __str__(self) -> str:
        self.check_obj()

        return json.dumps(self.get_dict())

    def check_obj(self):
        module_logger.info(self.payload + self.action + str(self._seq))
        if not self.device_id or not self._seq or (not self.payload and not self.action):
            raise ValueError("Missing mandatory fields")

    @property
    def seq(self):
        if self.device_id == "000000":  # If we are broadcasting
            return "00"
        return self._seq

    @seq.setter
    def seq(self, value):
        self._seq = "%02s" % value

    @property
    def device_id(self):
        return self._device_id

    @device_id.setter
    def device_id(self, value):
        if len(value) != 6:
            raise ValueError("'device_id' len not equal to 6 (%s)" % value)
        self._device_id = value

    @property
    def action(self):
        return self._action

    @action.setter
    def action(self, value):
        if value != "" and value not in DEVICE_ACTIONS:
            raise ValueError("'action' not found %s" % value)
        self._action = value

    @property
    def ttl(self):
        return self._ttl

    @ttl.setter
    def ttl(self, value):
        if isinstance(value, int):
            if int(value) > 5:
                raise ValueError("'ttl' must be < 5")
            self._ttl = value
        else:
            self._ttl = 0

    @staticmethod
    def sleep_duration() -> int:
        """
            Verify if one second passed since the creation of the payload (LoRa Limitation)
        :return:
        """
        return 2

    def load_mqtt(self, mqtt_payload: bytes, method_frame: Basic.Deliver = None, device_id=None):
        """
            Parse payload into an object
        :param method_frame:
        :param mqtt_payload:
        :return: instance
        """
        if method_frame is None and device_id is None:
            raise ValueError("'device_id' not found")

        payload = f"<{device_id or method_frame.routing_key.split('.')[-1]}>{bytes(mqtt_payload).decode('UTF-8')}"

        tableau = re.split(self.parse_regex, payload)
        if len(tableau) == 8:
            self.device_id = tableau[1]
            self.seq = tableau[2]
            self.ttl = int(tableau[3])
            self.action = tableau[4]
            self.payload = tableau[6] if tableau[5] == ":" else ""
        self.check_obj()
        return self

    def get_mqtt_string(self) -> bytes:
        """
        Get the MQTT representation of the object
        :return: str
        """
        return f"<{self.device_id}>{self.seq}{self.ttl}{self.action}{self.payload}".encode("UTF-8")

    def load_json(self, json_string: str):
        """
            Convert JSON to objet
        :param json_string:
        :return:
        """
        dictionary = json.loads(json_string)

        # Mandatory fields
        if "device_id" not in dictionary.keys() or dictionary.get("device_id", None) is None:
            raise ValueError("'device_id' missing")
        self.device_id = dictionary.get("device_id")

        if "seq" not in dictionary.keys() or dictionary.get("seq", None) is None:
            raise ValueError("'seq' missing")
        self.seq = dictionary.get("seq")

        if "payload" not in dictionary.keys() or dictionary.get("payload", None) is None:
            raise ValueError("'payload' missing")
        self.payload = dictionary.get("payload")

        # Optional fields
        self.ttl = dictionary.get("ttl", 0)
        self.action = dictionary.get("action", None)
        self.timestamp = dictionary.get("timestamp", int(time.time()))
        self.correlation_id = dictionary.get("correlation_id", None)

        return self

    def get_dict(self) -> dict:
        return {
            "device_id": self.device_id,
            "seq": self.seq,
            "ttl": self.ttl,
            "action": self.action,
            "payload": self.payload,
            "timestamp": self.timestamp,
        }
