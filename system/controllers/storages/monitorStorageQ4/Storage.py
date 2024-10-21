import logging
import os
from system.commonsSystem.node.node import Node
from system.commonsSystem.DTO.ReviewsDTO import ReviewsDTO
from system.commonsSystem.DTO.GamesDTO import GamesDTO, STATE_IDNAME
from system.commonsSystem.DTO.GameIDNameDTO import GameIDNameDTO

class Storage(Node):
    def __init__(self):
        super().__init__()
        self.reset_list()
        self.amount_needed = int(os.getenv("AMOUNT_NEEDED"))

    def reset_list(self, client_id=None):
        if client_id is None:
            self.list = {}
            self.counters = {}
        else:
            del self.list[client_id]
            del self.counters[client_id]

    def pre_eof_actions(self, client_id):
        if client_id not in self.list:
            return
        self.reset_list(client_id)
    
    def send_result(self, client_id, review):
        result = GamesDTO(client_id=client_id, state_games=STATE_IDNAME, games_dto=[GameIDNameDTO(review.app_id, review.name)], query=4, global_counter=self.counters[client_id])
        self.broker.public_message(sink=self.sink, message=result.serialize(), routing_key="default")

    def process_data(self, data: ReviewsDTO):
        client_id = data.get_client()
        if client_id not in self.list:
            self.list[client_id] = {}
        self.counters[client_id] = data.global_counter
        for review in data.reviews_dto:
            if review.name not in self.list[client_id]:
                self.list[client_id][review.name] = 1
            else:
                self.list[client_id][review.name] += 1
            if self.list[client_id][review.name] == self.amount_needed:
                self.send_result(client_id, review)