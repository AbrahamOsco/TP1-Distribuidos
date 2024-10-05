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
        data.filter_reviews(lambda x: self.is_correct_score(x.review_score))
        if len(data.reviews_dto) > 0:
            self.send_review(data)