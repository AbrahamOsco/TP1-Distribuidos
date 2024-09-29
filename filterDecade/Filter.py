import logging
import os
from common.node.node import Node

class Filter(Node):
    def __init__(self):
        super()
        self.decade = int(os.getenv("DECADE"))

    def receive_data(self):
        data = []
        return data
    
    def send_eof(self):
        logging.info("action: eof")

    def is_correct_decade(self, date):
        year = int(date.split(', ')[1])
        return year >= self.decade and year < self.decade + 10
    
    def trim_data(self, data):
        return data['name'] + " | " + data['average_playtime']

    def send_game(self, data):
        logging.info(f"action: result | {self.trim_data(data)}")

    def process_data(self, data):
        if self.is_eof(data):
            self.send_eof()
            return
        if self.is_correct_decade(data["release_date"]):
            self.send_game(data)