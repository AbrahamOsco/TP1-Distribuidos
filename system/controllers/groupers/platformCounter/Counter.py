import logging
from system.commonsSystem.DTO.PlatformDTO import PlatformDTO
from system.commonsSystem.DTO.GamesDTO import GamesDTO, STATE_PLATFORM
from system.commonsSystem.node.node import Node

class Counter(Node):
    def __init__(self):
        super().__init__()
        self.reset_counter()

    def reset_counter(self):
        self.result = {
            "client_id": "",
            "windows": 0,
            "linux": 0,
            "mac": 0,
        }

    def pre_eof_actions(self):
        self.send_result(self.result)
        self.reset_counter()

    def trim_data(self, data):
        return GamesDTO(client_id=data["client_id"], state_games=STATE_PLATFORM, games_dto=[PlatformDTO(windows=data["windows"], linux=data["linux"], mac=data["mac"])])

    def send_result(self, data):
        self.broker.public_message(sink=self.sink, message=self.trim_data(data).serialize(), routing_key="default")

    def process_data(self, data: GamesDTO):
        client_id = data.get_client()
        self.result["client_id"] = client_id
        platform_count = data.get_platform_count()
        self.result["windows"] += platform_count["windows"]
        self.result["linux"] += platform_count["linux"]
        self.result["mac"] += platform_count["mac"]
        self.update_amount_received_by_node(data.get_client(), data.get_amount())
        self.update_amount_sent_by_node(data.get_client(), data.get_amount())