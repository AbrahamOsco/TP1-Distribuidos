from system.commonsSystem.node.node import Node
from system.commonsSystem.DTO.GamesDTO import GamesDTO
from system.commonsSystem.node.routingPolicies.RoutingDefault import RoutingDefault
from system.commonsSystem.node.routingPolicies.RoutingModulo import RoutingModulo
import os

class Select(Node):
    def __init__(self):
        self.select_state = int(os.getenv("SELECT"))
        modulo = int(os.getenv("SEND_MODULO", 0))
        self.routing_policy = RoutingDefault() if modulo == 0 else RoutingModulo(modulo)
        super().__init__(self.routing_policy)

    def send_games(self, data: GamesDTO):
        data.set_state(self.select_state)
        self.broker.public_message(sink=self.sink, message=data.serialize(), routing_key=self.routing_policy.get_routing_key(data))

    def process_data(self, data):
        self.send_games(data)