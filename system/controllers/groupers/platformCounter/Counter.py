import logging
from system.commonsSystem.node.node import Node
from system.commonsSystem.DTO.GameDTO import GameDTO

class Counter(Node):
    def __init__(self):
        super().__init__()
        self.reset_counter()

    def reset_counter(self):
        self.result = {
            "client_id": "",
            "windows": 0,
            "linux": 0,
            "mac": 0,
        }

    def pre_eof_actions(self):
        self.send_result(self.result)
        self.reset_counter()

    def trim_data(self, data):
        return GameDTO(client_id=data["client_id"], windows=data["windows"], linux=data["linux"], mac=data["mac"])

    def send_result(self, data):
        logging.info(f"action: send_result | data: {data}")
        self.broker.public_message(exchange_name=self.sink, message=self.trim_data(data).to_string(), routing_key="default")

    def process_data(self, data):
        self.result["client_id"] = data.client_id
        self.result["windows"] += data.windows
        self.result["linux"] += data.linux
        self.result["mac"] += data.mac