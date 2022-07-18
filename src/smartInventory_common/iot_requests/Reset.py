from smartInventory_common.interfaces import LoRaPayload


class Reset(LoRaPayload):

    def __init__(self, device_id = ""):
        super(Reset, self).__init__()

        self.action = ""
        self.payload = "RESET"
        self.device_id = device_id or "000000"
        self.seq = "00"

