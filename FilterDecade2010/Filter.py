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

    def is_correct_decade(self, date):
        year = date.split(', ')[1]
        return year >= "2010" and year < "2020"
    
    def send_game(self, data):
        logging.info(f"action: result | name: {data['name']}")

    def process_data(self, data):
        if self.is_eof(data):
            self.send_eof()
            return
        if self.is_correct_decade(data["release_date"]):
            self.send_game(data)