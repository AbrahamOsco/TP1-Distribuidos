from system.commonsSystem.node.node import Node
from system.commonsSystem.DTO.GamesDTO import GamesDTO, STATE_PLATFORM

class Select(Node):
    def __init__(self):
        super().__init__()

    def send_games(self, data: GamesDTO):
        data.set_state(STATE_PLATFORM)
        self.update_amount_received_by_node(data.get_client(), data.get_amount())
        self.update_amount_sent_by_node(data.get_client(), data.get_amount())
        self.broker.public_message(sink=self.sink, message=data.serialize(), routing_key="default")

    def process_data(self, data):
        self.send_games(data)