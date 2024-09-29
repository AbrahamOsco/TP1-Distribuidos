import logging
import os
from commons.node.node import Node

class Grouper(Node):
    def __init__(self):
        super()
        self.reset_list()
        self.top_size = os.getenv("TOP_SIZE")

    def reset_list(self):
        self.list = []
        self.min_time = 0

    def receive_data(self):
        data = []
        return data

    def has_to_be_inserted(self, game):
        return len(self.list) < self.top_size or game["reviews"] > self.min_time
    
    def send_result(self):
        logging.info(f"action: result | list: {self.list}")

    def process_data(self, data):
        if self.is_eof(data):
            self.send_result()
            self.reset_list()
            return
        if self.has_to_be_inserted(data):
            for i in range(len(self.list)):
                if data["reviews"] > self.list[i]["reviews"]:
                    self.list.insert(i, data)
                    break
            if len(self.list) > self.top_size:
                self.list.pop()
            self.min_time = self.list[-1]["reviews"]