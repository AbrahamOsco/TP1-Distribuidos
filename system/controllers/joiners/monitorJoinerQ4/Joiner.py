import logging
from system.commonsSystem.node.node import Node, UnfinishedGamesException, UnfinishedReviewsException
from system.commonsSystem.DTO.ReviewsDTO import ReviewsDTO
from system.commonsSystem.DTO.GamesDTO import GamesDTO

STATUS_STARTED = 0
STATUS_REVIEWING = 1

class Joiner(Node):
    def __init__(self):
        super().__init__()
        self.reset_list()

    def reset_list(self):
        self.list = {}
        self.status = STATUS_STARTED

    def inform_eof_to_nodes(self, client):
        if self.status == STATUS_REVIEWING:
            self.send_eof(client)
            self.reset_list()
            self.status = STATUS_STARTED
            logging.info("Status changed. Now is expecting games")
        else:
            self.status = STATUS_REVIEWING
            logging.info("Status changed. Now is expecting reviews")

    def send_review(self, data):
        self.broker.public_message(sink=self.sink, message=data.serialize(), routing_key="default")

    def process_reviews(self, data: ReviewsDTO):
        if self.status == STATUS_STARTED:
            raise UnfinishedGamesException()
        data.filter_reviews(lambda review: review.app_id in self.list)
        if len(data.reviews_dto) > 0:
            data.apply_on_reviews(lambda review: review.set_name(self.list[review.app_id]))
            self.send_review(data)

    def process_games(self, data: GamesDTO):
        if self.status == STATUS_REVIEWING:
            raise UnfinishedReviewsException()
        self.update_total_received(data.get_client(), len(data.games_dto))
        for game in data.games_dto:
            self.list[game.app_id] = game.name

    def process_data(self, data):
        if data.is_reviews():
            self.process_reviews(data)
        if data.is_games():
            self.process_games(data)
