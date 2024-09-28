import logging
from common.node.node import Node

class Filter(Node):
    def __init__(self):
        super()

    def receive_data(self):
        data = []
        return data
    
    def send_eof(self):
        logging.info("action: eof")

    def has_enough_score(self, score):
        return score >= 5000
    
    def trim_data(self, data):
        return data['name']

    def send_game(self, data):
        logging.info(f"action: result | {self.trim_data(data)}")

    def process_data(self, data):
        if self.is_eof(data):
            self.send_eof()
            return
        if self.has_enough_score(data["score"]):
            self.send_game(data)