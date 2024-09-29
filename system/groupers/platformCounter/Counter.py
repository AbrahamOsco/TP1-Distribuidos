import logging
from commonsSystem.node.node import Node
from commonsSystem.DTO.GameDTO import GameDTO

class Counter(Node):
    def __init__(self):
        super()
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
        self.broker.public_message(exchange_name=self.sink, message=self.trim_data(data).to_string())

    def process_data(self, data):
        for d in data:
            self.result["windows"] += d.windows
            self.result["linux"] += d.linux
            self.result["mac"] += d.mac