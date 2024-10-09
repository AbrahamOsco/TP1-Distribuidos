from system.commonsSystem.node.node import Node
from system.commonsSystem.DTO.ReviewsDTO import ReviewsDTO, STATE_TEXT
import os

class Filter(Node):
    def __init__(self):
        super().__init__()
        self.score_wanted = int(os.getenv("SCORE_WANTED", 1))

    def is_correct_score(self, score):
        return score == self.score_wanted
    
    def send_review(self, data):
        data.set_state(STATE_TEXT)
        self.broker.public_message(sink=self.sink, message=data.serialize(), routing_key="default")

    def process_data(self, data: ReviewsDTO):
        self.update_amount_received_by_node(data.get_client(), data.get_amount())
        data.filter_reviews(lambda x: self.is_correct_score(x.review_score))
        if len(data.reviews_dto) > 0:
            self.send_review(data)
            self.update_amount_sent_by_node(data.get_client(), data.get_amount())