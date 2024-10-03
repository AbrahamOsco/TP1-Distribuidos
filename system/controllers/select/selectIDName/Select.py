from system.commonsSystem.node.node import Node
from system.commonsSystem.DTO.GamesDTO import GamesDTO, STATE_IDNAME

class Select(Node):
    def __init__(self):
        super().__init__()

    def send_games(self, data: GamesDTO):
        data.set_state(STATE_IDNAME)
        self.broker.public_message(sink=self.sink, message=data.serialize(), routing_key="default")

    def process_data(self, data):
        self.send_games(data)