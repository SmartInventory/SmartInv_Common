import json
import random
import re
import time
import uuid

DEVICE_ACTIONS = [
    "STA",  # Student authentication
    "BOR",  # Borrowing
    "INV",  # Inventory Mode
]


class LoRaPayload:
    def __init__(self, payload: str):
        self.device_id: str = ""
        self.action: str = ""
        self.seq: int = 0
        self.ttl: int = 0
        self.payload: str = ""
        self.timestamp: int = int(time.time())

        self.correlation_id = uuid.uuid4().hex

        self.parse_regex = re.compile("^<(\w+)>(\d{2})(\d?)([A-Z]{0,3})([:_]?)(.*)$")

        self._parse(payload)

    def __str__(self):
        return json.dumps({"device_id": self.device_id, "seq": self.seq, "ttl": self.ttl, "action": self.action,
                           "payload": self.payload})

    @staticmethod
    def sleep_duration():
        """
            Verify if one second passed since the creation of the payload (LoRa Limitation)
        :return:
        """
        return random.randint(2, 4)

    def _parse(self, payload):
        """
            Parse payload into an object
        :param payload:
        :return:
        """
        tableau = re.split(self.parse_regex, payload)
        if len(tableau) == 8:
            self.device_id = tableau[1]
            self.seq = tableau[2]
            self.ttl = int(tableau[3])
            self.action = "".join([tableau[i] for i in (4, 5, 6)]) if tableau[5] == "_" else tableau[4]
            self.payload = tableau[6] if tableau[5] == ":" else ""

        return self._check_format()

    def _check_format(self):
        if self.action not in DEVICE_ACTIONS and self.ttl > 0:
            return False
        return True
