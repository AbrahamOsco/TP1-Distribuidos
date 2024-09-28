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

    def is_gender(self, genders, wanted_gender):
        for gender in genders.split(','):
            if gender == wanted_gender:
                return True
        return False
    
    def trim_data(self, data):
        return data['name'] + " | " + data['release_date'] + " | " + data['average_playtime']
    
    def send_game(self, data, gender):
        logging.info(f"action: result | routing key: {gender}" | {self.trim_data(data)})

    def process_data(self, data):
        if self.is_eof(data):
            self.send_eof()
            return
        if self.is_gender(data["gender"], "indie"):
            self.send_game(data, "indie")
        if self.is_gender(data["gender"], "action"):
            self.send_game(data, "action")