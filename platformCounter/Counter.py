import logging
from common.node.node import Node

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

    def receive_data(self):
        data = []
        return data

    def send_eof(self):
        logging.info("action: eof")

    def send_result(self):
        logging.info(f"action: result | windows: {self.result['windows']} | linux: {self.result['linux']} | mac: {self.result['mac']}")

    def process_data(self, data):
        if self.is_eof(data):
            self.send_result()
            self.reset_counter()
            self.send_eof()
            return
        for d in data:
            self.result["windows"] += d["windows"]
            self.result["linux"] += d["linux"]
            self.result["mac"] += d["mac"]