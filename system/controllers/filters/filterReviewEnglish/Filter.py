from system.commonsSystem.node.node import Node
from system.commonsSystem.DTO.ReviewsDTO import ReviewsDTO, STATE_IDNAME
import langid

class Filter(Node):
    def __init__(self):
        super().__init__()
        langid.set_languages(['en'])

    def is_in_english(self, text):
        lang, _ = langid.classify(text)
        return lang == 'en'

    def send_reviews(self, data: ReviewsDTO):
        data.set_state(STATE_IDNAME)
        self.update_amount_sent_by_node(data.get_client(), data.get_amount())
        self.broker.public_message(sink=self.sink, message=data.serialize(), routing_key="default")

    def process_data(self, data: ReviewsDTO):
        self.update_amount_received_by_node(data.get_client(), data.get_amount())
        data.filter_reviews(lambda review: self.is_in_english(review.review_text))
        if len(data.reviews_dto) > 0:
            self.send_reviews(data)