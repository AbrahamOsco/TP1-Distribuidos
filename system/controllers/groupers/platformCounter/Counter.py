import logging
from system.commonsSystem.node.node import Node
from system.commonsSystem.DTO.GameDTO import GameDTO

class Counter(Node):
    def __init__(self):
        super().__init__()
        self.reset_counter()

    def reset_counter(self):
        self.result = {
            "windows": 0,
            "linux": 0,
            "mac": 0,
        }

    def pre_eof_actions(self):
        self.send_result()
        self.reset_counter()

    def trim_data(self, data):
        return GameDTO(client=data.client, windows=self.result["windows"], linux=self.result["linux"], mac=self.result["mac"])

    def send_result(self, data):
        logging.info(f"action: send_result | data: {data}")
        self.broker.public_message(exchange_name=self.sink, message=self.trim_data(data).to_string())

    def process_data(self, data):
        self.result["windows"] += data.windows
        self.result["linux"] += data.linux
        self.result["mac"] += data.mac