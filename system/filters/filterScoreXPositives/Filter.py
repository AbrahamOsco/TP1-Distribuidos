import logging
import os
from commonsSystem.node.node import Node

class Filter(Node):
    def __init__(self):
        super()
        self.amount_needed = int(os.getenv("AMOUNT_NEEDED"))

    def has_enough_score(self, score):
        return score >= self.amount_needed
    
    def trim_data(self, data):
        return data.retain(["client", "name"])

    def send_game(self, data):
        self.broker.public_message(exchange_name=self.sink, message=self.trim_data(data).to_string())

    def process_data(self, data):
        if self.has_enough_score(data["score"]):
            self.send_game(data)