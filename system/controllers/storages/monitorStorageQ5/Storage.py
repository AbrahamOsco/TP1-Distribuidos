from system.commonsSystem.node.node import Node, UnfinishedReviewsException, UnfinishedGamesException
from system.commonsSystem.DTO.ReviewsDTO import ReviewsDTO, STATE_NAME
from system.commonsSystem.DTO.GamesDTO import GamesDTO
from system.commonsSystem.DTO.ReviewNameDTO import ReviewNameDTO
import os
import logging

STATUS_STARTED = 0
STATUS_REVIEWING = 1

class Storage(Node):
    def __init__(self):
        super().__init__()
        self.percentile = float(os.getenv("PERCENTILE", 0.9))
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

    def send_reviews(self, reviews):
        for review in reviews:
            if review.name in ["Counter-Strike", "Counter-Strike: Source", "Half-Life: Source", "Half-Life 2: Lost Coast", "Team Fortress 2", "Left 4 Dead 2", "Dota 2", "Portal 2", "Killing Floor", "The Ship: Murder Party"]:
                logging.info(f"Game fullfils criteria: {review.name}")
        # reviewsDTO = ReviewsDTO(self.client_id, STATE_NAME, reviews)
        # self.broker.public_message(sink=self.sink, message=reviewsDTO.serialize(), routing_key="default")

    def send_result(self):
        values = sorted(self.list.values())
        index = int(self.percentile * len(values)) -1
        percentile_90_value = values[index]
        reviews_to_send = []
        for app_id, reviews in self.list.items():
            if reviews >= percentile_90_value:
                reviews_to_send.append(ReviewNameDTO(name=self.games[app_id]))
            if len(reviews_to_send) > 50:
                self.send_reviews(reviews_to_send)
                reviews_to_send = []
        if len(reviews_to_send) > 0:
            self.send_reviews(reviews_to_send)

    def process_reviews(self, data: ReviewsDTO):
        if self.status == STATUS_STARTED:
            raise UnfinishedGamesException()
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