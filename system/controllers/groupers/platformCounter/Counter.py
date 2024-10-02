import logging
from system.commonsSystem.DTO.PlatformDTO import PlatformDTO
from system.commonsSystem.broker.Broker import Broker
from system.commonsSystem.DTO.GameDTO import GameDTO

COUNT_BY_PLATFORM = "CountByPlatform"
RK_COUNT_BY_PLATFORM= "count_by_platform"

class Counter:
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
        return PlatformDTO(client_id=data["client_id"], windows=data["windows"], linux=data["linux"], mac=data["mac"])

    def send_result(self, data):
        logging.info(f"action: send_result | data: {data}")
        self.broker.public_message(exchange_name=self.sink, message=self.trim_data(data), routing_key="default")

    def process_data(self, data):
        client_id = data.client_id
        self.result.client_id = client_id
        platform_count = data.get_platform_count()
        self.result.windows += platform_count["windows"]
        self.result.linux += platform_count["linux"]
        self.result.mac += platform_count["mac"]