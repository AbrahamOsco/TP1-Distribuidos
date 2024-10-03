import os
import logging
from system.commonsSystem.node.node import Node
from system.commonsSystem.DTO.DecadeDTO import DecadeDTO

class Filter(Node):
    def __init__(self):
        super().__init__()
        self.genders = os.getenv("GENDERS").split(',')

    def is_gender(self, genders, wanted_gender):
        return wanted_gender in genders.split(',')
    
    def trim_data(self, data):
        return DecadeDTO.from_genreDTO(data)
    
    def send_game(self, data, gender):
        self.broker.public_message(exchange_name=self.sink, routing_key=gender, message=self.trim_data(data))

    def process_data(self, data):
        for gender in self.genders:
            if self.is_gender(data.genres, gender):
                self.send_game(data, gender)