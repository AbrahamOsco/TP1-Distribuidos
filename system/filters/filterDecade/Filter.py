import logging
import os
from commonsSystem.node.node import Node
from commonsSystem.DTO.GameDTO import GameDTO

class Filter(Node):
    def __init__(self):
        super()
        self.decade = int(os.getenv("DECADE"))

    def receive_data(self):
        data = []
        return data

    def is_correct_decade(self, date):
        year = int(date.split(', ')[1])
        return year >= self.decade and year < self.decade + 10
    
    def trim_data(self, data):
        return data.retain(["client", "name", "avg_playtime_forever"])

    def send_game(self, data):
        self.broker.public_message(exchange_name=self.sink, message=self.trim_data(data).to_string())

    def process_data(self, data):
        if self.is_correct_decade(data.release_date):
            self.send_game(data)