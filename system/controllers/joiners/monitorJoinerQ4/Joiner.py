from system.commonsSystem.DTO.ReviewsDTO import ReviewsDTO
from system.commonsSystem.DTO.GamesDTO import GamesDTO
from system.commonsSystem.node.dualInputNode import DualInputNode, STATUS_STARTED
from system.commonsSystem.node.node import PrematureMessage
import logging

class Joiner(DualInputNode):
    def __init__(self):
        super().__init__()

    def send_review(self, data):
        self.broker.public_message(sink=self.sink, message=data.serialize(), routing_key="default")

    def process_reviews(self, data: ReviewsDTO):
        client_id = data.get_client()
        if self.status[client_id] == STATUS_STARTED:
            logging.error(f"Client {client_id} is still started")
            raise PrematureMessage()
        data.filter_data(lambda review: review.app_id in self.list[client_id])
        if len(data.reviews_dto) > 0:
            data.apply_on_reviews(lambda review: review.set_name(self.list[client_id][review.app_id]))
            self.send_review(data)

    def process_games(self, data: GamesDTO):
        client_id = data.get_client()
        for game in data.games_dto:
            self.list[client_id][game.app_id] = game.name