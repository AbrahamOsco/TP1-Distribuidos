import os
from system.commonsSystem.node.node import Node
from system.commonsSystem.DTO.ReviewsDTO import ReviewsDTO
from system.commonsSystem.DTO.DetectDTO import DetectDTO
from system.commonsSystem.DTO.GamesDTO import GamesDTO, STATE_IDNAME
from system.commonsSystem.DTO.GameIDNameDTO import GameIDNameDTO
from common.tolerance.IDList import IDList
from system.commonsSystem.node.structures.storageQ4Structure import StorageQ4Structure
from system.commonsSystem.node.statefullNode import StatefullNode
import logging

class Storage(StatefullNode):
    def __init__(self):
        self.amount_needed = int(os.getenv("AMOUNT_NEEDED"))
        self.id_list = IDList()
        data = StorageQ4Structure(counter_size=1)
        super().__init__(data, [self.id_list])

    def pre_eof_actions(self, client_id):
        if client_id not in self.data.list:
            return
        self.data.reset(client_id)
    
    def send_result(self, client_id, review):
        result = GamesDTO(client_id=client_id, state_games=STATE_IDNAME, games_dto=[GameIDNameDTO(review.app_id, review.name)], query=4, global_counter=self.data.counter[client_id].pop(0))
        self.broker.public_message(sink=self.sink, message=result.serialize(), routing_key="default")

    def process_data(self, data: ReviewsDTO):
        if self.id_list.already_processed(data.global_counter):
            logging.error(f"Game {data.global_counter} already processed")
            return
        self.id_list.insert(data.global_counter)
        self.logs.add_log(data.serialize())
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
        if self.logs.is_full():
            self.checkpoint.save_checkpoint(self.data.to_bytes())