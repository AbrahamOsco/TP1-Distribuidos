from system.commonsSystem.node.node import Node, UnfinishedReviewsException, UnfinishedGamesException
from system.commonsSystem.DTO.ReviewsDTO import ReviewsDTO
from system.commonsSystem.DTO.GamesDTO import GamesDTO, STATE_IDNAME
from system.commonsSystem.DTO.GameIDNameDTO import GameIDNameDTO
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

    def send_games(self, games):
        gamesDTO = GamesDTO(client_id=self.client_id, state_games=STATE_IDNAME, games_dto=games, query=5)
        self.broker.public_message(sink=self.sink, message=gamesDTO.serialize(), routing_key="default")

    def send_result(self):
        values = sorted(self.list.values())
        index = int(self.percentile * len(values)) -1
        amount_to_send = int(len(values) * (1- self.percentile))
        percentile_90_value = values[index]
        logging.info(f"Percentile 90 value: {percentile_90_value}")
        games_to_send = []
        games_sent = 0
        for app_id, reviews in self.list.items():
            if reviews >= percentile_90_value:
                games_to_send.append(GameIDNameDTO(app_id=app_id, name=self.games[app_id]))
            if len(games_to_send) > 50:
                self.send_games(games_to_send)
                games_to_send = []
                games_sent += 50
            if games_sent > amount_to_send:
                break
        if len(games_to_send) > 0 and games_sent <= amount_to_send:
            self.send_games(games_to_send)

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