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

    def reset_list(self):
        self.list = {}
        self.current_client = 0

    def pre_eof_actions(self, client_id):
        self.reset_list()
    
    def send_result(self, review):
        result = GamesDTO(client_id=self.current_client, state_games=STATE_IDNAME, games_dto=[GameIDNameDTO(review.app_id, review.name)], query=4)
        self.broker.public_message(sink=self.sink, message=result.serialize(), routing_key="default")

    def process_data(self, data: ReviewsDTO):
        self.current_client = data.get_client()
        self.update_amount_received_by_node(data.get_client(), data.get_amount())
        for review in data.reviews_dto:
            if review.name not in self.list:
                self.list[review.name] = 1
            else:
                self.list[review.name] += 1
            if self.list[review.name] == self.amount_needed:
                self.send_result(review)
                self.update_amount_sent_by_node(data.get_client(), 1)