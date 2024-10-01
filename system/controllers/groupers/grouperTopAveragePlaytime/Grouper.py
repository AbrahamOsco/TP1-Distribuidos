import logging
import os
from system.commonsSystem.node.node import Node

class Grouper(Node):
    def __init__(self):
        super().__init__()
        self.reset_list()
        self.top_size = os.getenv("TOP_SIZE")

    def reset_list(self):
        self.list = []
        self.min_time = 0

    def pre_eof_actions(self):
        self.send_result()
        self.reset_list()

    def has_to_be_inserted(self, game):
        return len(self.list) < self.top_size or game.avg_playtime_forever > self.min_time
    
    def send_result(self):
        logging.info(f"action: result | list: {self.list}")

    def process_data(self, data):
        if self.has_to_be_inserted(data):
            for i in range(len(self.list)):
                if data.avg_playtime_forever > self.list[i].avg_playtime_forever:
                    self.list.insert(i, data)
                    break
            if len(self.list) > self.top_size:
                self.list.pop()
            self.min_time = self.list[-1].avg_playtime_forever