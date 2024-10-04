import logging
import os
from system.commonsSystem.node.node import Node
from system.commonsSystem.DTO.ReviewsDTO import ReviewsDTO

class Storage(Node):
    def __init__(self):
        super().__init__()
        self.reset_list()
        self.amount_needed = int(os.getenv("AMOUNT_NEEDED"))

    def reset_list(self):
        self.list = {}
        self.current_client = 0

    def pre_eof_actions(self):
        self.reset_list()
    
    def send_result(self, name):
        logging.info(f"Game fullfils criteria: {name}")
        # self.broker.public_message(sink=self.sink, message=app_id, routing_key="default")

    def process_data(self, data: ReviewsDTO):
        self.current_client = data.get_client()
        for review in data.reviews_dto:
            if review.name not in self.list:
                self.list[review.name] = 1
            else:
                self.list[review.name] += 1
            if self.list[review.name] == self.amount_needed:
                self.send_result(review.name)