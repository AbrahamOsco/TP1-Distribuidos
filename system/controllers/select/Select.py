from system.commonsSystem.node.node import Node
from system.commonsSystem.DTO.GamesDTO import GamesDTO
import os

class Select(Node):
    def __init__(self):
        self.select_state = int(os.getenv("SELECT"))
        super().__init__()

    def send_games(self, data: GamesDTO):
        data.set_state(self.select_state)
        self.broker.public_message(sink=self.sink, message=data.serialize(), routing_key="default")

    def process_data(self, data):
        self.send_games(data)