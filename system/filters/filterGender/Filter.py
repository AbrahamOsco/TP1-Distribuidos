import os
import logging
from commonsSystem.node.node import Node

class Filter(Node):
    def __init__(self):
        super()
        self.genders = os.getenv("GENDERS").split(',')

    def is_gender(self, genders, wanted_gender):
        return wanted_gender in genders.split(',')
    
    def trim_data(self, data):
        return data.retain(["client", "name", "release_date", "avg_playtime_forever"])
    
    def send_game(self, data, gender):
        self.broker.public_message(exchange_name=self.sink, routing_key=gender, message=self.trim_data(data).to_string())

    def process_data(self, data):
        for gender in self.genders:
            if self.is_gender(data.genres, gender):
                self.send_game(data, gender)