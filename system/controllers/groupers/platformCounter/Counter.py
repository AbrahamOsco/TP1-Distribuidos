from system.commonsSystem.DTO.PlatformDTO import PlatformDTO
from system.commonsSystem.DTO.GamesDTO import GamesDTO, STATE_PLATFORM
from system.commonsSystem.node.node import Node

class Counter(Node):
    def __init__(self):
        super().__init__()
        self.reset_counter()

    def reset_counter(self, client_id=None):
        if client_id is None:
            self.result = {}
        else:
            del self.result[client_id]

    def pre_eof_actions(self, client_id):
        if client_id not in self.result:
            return
        data = self.result[client_id]
        result = GamesDTO(client_id=int(client_id), state_games=STATE_PLATFORM, games_dto=[PlatformDTO(windows=data["windows"], linux=data["linux"], mac=data["mac"])], global_counter=data["counter"])
        self.send_result(result)
        self.reset_counter(client_id)

    def send_result(self, data):
        self.broker.public_message(sink=self.sink, message=data.serialize(), routing_key="default")

    def process_data(self, data: GamesDTO):
        client_id = data.get_client()
        if client_id not in self.result:
            self.result[client_id] = {"windows": 0, "linux": 0, "mac": 0}
        platform_count = data.get_platform_count()
        self.result[client_id]["windows"] += platform_count["windows"]
        self.result[client_id]["linux"] += platform_count["linux"]
        self.result[client_id]["mac"] += platform_count["mac"]
        self.result[client_id]["counter"] = data.global_counter


