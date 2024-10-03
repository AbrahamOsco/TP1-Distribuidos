from system.commonsSystem.node.node import Node, UnfinishedReviewsException, UnfinishedGamesException
from system.commonsSystem.DTO.ReviewedGameDTO import ReviewedGameDTO
from system.commonsSystem.DTO.ReviewsDTO import ReviewsDTO
from system.commonsSystem.DTO.GamesDTO import GamesDTO
import logging

STATUS_STARTED = 0
STATUS_REVIEWING = 1

class Storage(Node):
    def __init__(self):
        super().__init__()
        self.reset_list()

    def reset_list(self):
        self.list = {}
        self.games = {}
        self.client_id = 0
        self.status = STATUS_STARTED

    def inform_eof_to_nodes(self, client):
        if self.status == STATUS_REVIEWING:
            self.send_result()
            self.send_eof(client)
            self.reset_list()
            self.status = STATUS_STARTED
            logging.info("Status changed. Now is expecting games")
        else:
            self.status = STATUS_REVIEWING
            logging.info("Status changed. Now is expecting reviews")

    def send_result(self):
        for app_id in self.list:
            data = ReviewedGameDTO(self.client_id, self.games[app_id], self.list[app_id])
            self.broker.public_message(sink=self.sink, message=data.serialize(), routing_key="default")

    def process_reviews(self, data: ReviewsDTO):
        if self.status == STATUS_STARTED:
            raise UnfinishedGamesException()
        # logging.info(f"Processing reviews {len(data.reviews_dto)}")
        for review in data.reviews_dto:
            if review.app_id in self.list:
                self.list[review.app_id] += 1

    def process_games(self, data: GamesDTO):
        if self.status == STATUS_REVIEWING:
            raise UnfinishedReviewsException()
        self.client_id = data.client_id
        for game in data.games_dto:
            self.list[game.app_id] = 0
            self.games[game.app_id] = game.name

    def process_data(self, data):
        if data.is_reviews():
            self.process_reviews(data)
        if data.is_games():
            self.process_games(data)