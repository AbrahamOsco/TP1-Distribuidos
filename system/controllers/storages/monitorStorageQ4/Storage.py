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
        else:
            del self.list[client_id]

    def pre_eof_actions(self, client_id):
        self.reset_list(client_id)
    
    def send_result(self, client_id, review):
        result = GamesDTO(client_id=client_id, state_games=STATE_IDNAME, games_dto=[GameIDNameDTO(review.app_id, review.name)], query=4)
        self.broker.public_message(sink=self.sink, message=result.serialize(), routing_key="default")

    def process_data(self, data: ReviewsDTO):
        client_id = data.get_client()
        if client_id not in self.list:
            self.list[client_id] = {}
        self.eof.update_amount_received_by_node(client_id, data.get_amount())
        if client_id not in self.eof.amount_sent_by_node:
            self.eof.update_amount_sent_by_node(client_id, 0)
        for review in data.reviews_dto:
            if review.name not in self.list[client_id]:
                self.list[client_id][review.name] = 1
            else:
                self.list[client_id][review.name] += 1
            if self.list[client_id][review.name] == self.amount_needed:
                self.send_result(client_id, review)
                self.eof.update_amount_sent_by_node(client_id, 1)