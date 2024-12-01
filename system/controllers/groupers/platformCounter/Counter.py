from system.commonsSystem.DTO.PlatformDTO import PlatformDTO
from system.commonsSystem.DTO.GamesDTO import GamesDTO, STATE_PLATFORM
from system.commonsSystem.DTO.DetectDTO import DetectDTO
from system.commonsSystem.node.statefullNode import StatefullNode
from common.tolerance.IDList import IDList
from system.commonsSystem.node.structures.platformStructure import PlatformStructure
import logging

class Counter(StatefullNode):
    def __init__(self):
        self.id_list = IDList()
        self.data = PlatformStructure()
        super().__init__(self.data, [self.id_list])

    def pre_eof_actions(self, client_id):
        if client_id not in self.data.result:
            return
        data = self.data.result[client_id]
        result = GamesDTO(client_id=int(client_id), state_games=STATE_PLATFORM, games_dto=[PlatformDTO(windows=data["windows"], linux=data["linux"], mac=data["mac"])], global_counter=data["counter"])
        self.send_result(result)
        self.data.reset(client_id)
        self.checkpoint.save_checkpoint(self.data.to_bytes())

    def send_result(self, data):
        self.broker.public_message(sink=self.sink, message=data.serialize(), routing_key="default")

    def process_data(self, data: GamesDTO):
        if self.id_list.already_processed(data.global_counter):
            logging.info(f"Already processed {data.global_counter}")
            return
        self.logs.add_log(data.serialize())
        self.id_list.insert(data.global_counter)
        client_id = data.get_client()
        if client_id not in self.data.result:
            self.data.result[client_id] = {"windows": 0, "linux": 0, "mac": 0, "counter": 0}
        platform_count = data.get_platform_count()
        self.data.result[client_id]["windows"] += platform_count["windows"]
        self.data.result[client_id]["linux"] += platform_count["linux"]
        self.data.result[client_id]["mac"] += platform_count["mac"]
        self.data.result[client_id]["counter"] = data.global_counter
        if self.logs.is_full():
            self.checkpoint.save_checkpoint(self.data.to_bytes())
