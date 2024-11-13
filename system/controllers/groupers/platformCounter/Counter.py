from system.commonsSystem.DTO.PlatformDTO import PlatformDTO
from system.commonsSystem.DTO.GamesDTO import GamesDTO, STATE_PLATFORM
from system.commonsSystem.DTO.DetectDTO import DetectDTO
from system.commonsSystem.node.node import Node
from common.tolerance.IDList import IDList
from common.tolerance.logFile import LogFile
from common.tolerance.checkpointFile import CheckpointFile
from system.commonsSystem.node.structures.platformStructure import PlatformStructure
import os
import logging

class Counter(Node):
    def __init__(self):
        super().__init__()
        prefix = os.getenv("NODE_NAME") + os.getenv("NODE_ID") + "_"
        self.id_list = IDList()
        self.logs = LogFile(prefix)
        self.checkpoint = CheckpointFile(prefix, log_file=self.logs, id_lists=[self.id_list])
        self.data = PlatformStructure()
        self.recover()

    def pre_eof_actions(self, client_id):
        if client_id not in self.result:
            return
        self.checkpoint.save_checkpoint(self.data.to_bytes())
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

    def recover(self):
        checkpoint, must_reprocess = self.checkpoint.load_checkpoint()
        self.data.from_bytes(checkpoint)
        if must_reprocess:
            for log in self.logs.logs:
                data = DetectDTO(log).get_dto()
                self.process_data(data)
        self.data.print_state()
        self.checkpoint.save_checkpoint(self.data.to_bytes())
