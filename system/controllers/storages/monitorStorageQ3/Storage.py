from system.commonsSystem.node.node import Node, UnfinishedReviewsException, UnfinishedGamesException
from system.commonsSystem.DTO.GameReviewedDTO import GameReviewedDTO
from system.commonsSystem.DTO.ReviewsDTO import ReviewsDTO
from system.commonsSystem.DTO.GamesDTO import GamesDTO, STATE_REVIEWED
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
        estado = ""
        if self.status == STATUS_REVIEWING:
            estado = "reviews"
        else:
            estado = "juegos"
        if self.status == STATUS_REVIEWING:
            self.send_result()
            self.send_eof(client)
            self.reset_list()
            self.status = STATUS_STARTED
            logging.info(f"Informo EOF de {estado} con cantidad procesados: {self.total_amount_processed[client]}")
            logging.info("Status changed. Now is expecting games")            
        else:
            self.status = STATUS_REVIEWING
            logging.info(f"Informo EOF de {estado} con cantidad procesados: {self.total_amount_processed[client]}")
            logging.info("Status changed. Now is expecting reviews")

        self.reset_total_amount_received(client)
        self.reset_total_amount_sent(client)

    def send_games(self, games):
        gamesDTO = GamesDTO(client_id=self.client_id, state_games=STATE_REVIEWED, games_dto=games)
        self.broker.public_message(sink=self.sink, message=gamesDTO.serialize(), routing_key="default")

    def send_result(self):
        games = []
        for app_id in self.list:
            games.append(GameReviewedDTO(app_id, self.games[app_id], self.list[app_id]))
            if len(games) == 25:
                self.send_games(games)
                games = []
        if len(games) > 0:
            self.send_games(games)

    def process_reviews(self, data: ReviewsDTO):
        if self.status != STATUS_REVIEWING:
            raise UnfinishedGamesException()
        self.update_total_received(data.client_id, len(data.reviews_dto))
        for review in data.reviews_dto:
            if review.app_id in self.list:
                self.list[review.app_id] += 1
                self.update_total_processed(data.client_id, 1)

    def process_games(self, data: GamesDTO):
        if self.status != STATUS_STARTED:
            raise UnfinishedReviewsException()
        self.update_total_received(data.client_id, len(data.games_dto))
        self.client_id = data.client_id
        for game in data.games_dto:
            self.list[game.app_id] = 0
            self.games[game.app_id] = game.name
            self.update_total_processed(data.client_id, 1)

    def process_data(self, data):
        if data.is_reviews():
            self.process_reviews(data)
        if data.is_games():
            self.process_games(data)