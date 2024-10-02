import logging
import os
from system.commonsSystem.node.node import Node

class Grouper(Node):
    def __init__(self):
        super().__init__()
        self.reset_list()
        self.amount_needed = os.getenv("AMOUNT_NEEDED")

    def reset_list(self):
        self.list = {}

    def pre_eof_actions(self):
        self.reset_list()
    
    def send_result(self, app_id):
        logging.info(f"action: result | list: {app_id}")
        self.broker.public_message(exchange_name=self.sink, message=app_id, routing_key="default")

    def process_data(self, data):
        if data.app_id not in self.list:
            self.list[data.app_id] = 0
        self.list[data.app_id] += 1
        if self.list[data.app_id] == self.amount_needed:
            self.send_result(data.app_id)