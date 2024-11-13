import os
from system.commonsSystem.node.node import Node
from system.commonsSystem.DTO.ReviewsDTO import ReviewsDTO
from system.commonsSystem.DTO.DetectDTO import DetectDTO
from system.commonsSystem.DTO.GamesDTO import GamesDTO, STATE_IDNAME
from system.commonsSystem.DTO.GameIDNameDTO import GameIDNameDTO
from common.tolerance.IDList import IDList
from common.tolerance.logFile import LogFile
from common.tolerance.checkpointFile import CheckpointFile
from system.commonsSystem.node.structures.storageQ4Structure import StorageQ4Structure

class Storage(Node):
    def __init__(self):
        super().__init__()
        self.amount_needed = int(os.getenv("AMOUNT_NEEDED"))
        prefix = os.getenv("NODE_NAME") + os.getenv("NODE_ID") + "_"
        self.id_list = IDList()
        self.logs = LogFile(prefix)
        self.checkpoint = CheckpointFile(prefix, log_file=self.logs, id_lists=[self.id_list])
        self.data = StorageQ4Structure(counter_size=1)
        self.recover()

    def pre_eof_actions(self, client_id):
        if client_id not in self.data.list:
            return
        self.data.reset(client_id)
    
    def send_result(self, client_id, review):
        result = GamesDTO(client_id=client_id, state_games=STATE_IDNAME, games_dto=[GameIDNameDTO(review.app_id, review.name)], query=4, global_counter=self.data.counter.pop(0))
        self.broker.public_message(sink=self.sink, message=result.serialize(), routing_key="default")

    def process_data(self, data: ReviewsDTO):
        client_id = data.get_client()
        if client_id not in self.data.list:
            self.data.list[client_id] = {}
            self.data.counter[client_id] = []
        self.data.add_counter(client_id, data.global_counter)
        for review in data.reviews_dto:
            if review.name not in self.data.list[client_id]:
                self.data.list[client_id][review.name] = 1
            else:
                self.data.list[client_id][review.name] += 1
            if self.data.list[client_id][review.name] == self.amount_needed:
                self.send_result(client_id, review)
                
    def recover(self):
        checkpoint, must_reprocess = self.checkpoint.load_checkpoint()
        self.data.from_bytes(checkpoint)
        if must_reprocess:
            for log in self.logs.logs:
                data = DetectDTO(log).get_dto()
                self.process_data(data)
        self.data.print_state()
        self.checkpoint.save_checkpoint(self.data.to_bytes())