from system.commonsSystem.node.node import Node
from system.commonsSystem.DTO.ReviewsDTO import ReviewsDTO, STATE_TEXT

class Filter(Node):
    def __init__(self):
        super().__init__()

    def is_correct_score(self, score):
        return score == -1
    
    def send_review(self, data):
        data.set_state(STATE_TEXT)
        self.broker.public_message(sink=self.sink, message=data.serialize(), routing_key="default")

    def process_data(self, data: ReviewsDTO):
        self.update_total_received(data.client, len(data.reviews_dto))
        data.filter_reviews(lambda x: self.is_correct_score(x.review_score))
        if len(data.reviews_dto) > 0:
            self.send_review(data)
            self.update_total_processed(data.client, len(data.reviews_dto))