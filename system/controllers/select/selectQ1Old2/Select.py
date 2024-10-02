"""from system.commonsSystem.node.node import Node
from system.commonsSystem.DTO.GamesDTO import STATE_PLATFORM

class Select(Node):
    def __init__(self):
        super().__init__()

    def send_games(self, data):
        data.set_state(STATE_PLATFORM)
        self.broker.public_message(exchange_name=self.sink, message=data)

    def process_data(self, data):
        self.send_games(data)"""