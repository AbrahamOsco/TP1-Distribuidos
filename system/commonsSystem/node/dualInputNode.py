from system.commonsSystem.node.node import Node, UnfinishedReviewsException, UnfinishedGamesException, PrematureEOFException
from system.commonsSystem.DTO.GameReviewedDTO import GameReviewedDTO
from system.commonsSystem.DTO.ReviewsDTO import ReviewsDTO
from system.commonsSystem.DTO.GamesDTO import GamesDTO, STATE_REVIEWED
from system.commonsSystem.DTO.EOFDTO import EOFDTO
from system.commonsSystem.node.routingPolicies.RoutingManyToOne import RoutingManyToOne
import logging

STATUS_STARTED = 0
STATUS_REVIEWING = 1

class DualInputNode(Node):
    def __init__(self):
        super().__init__(RoutingManyToOne())
        self.reset_list()

    def reset_list(self, client_id=None):
        if client_id is None:
            self.list = {}
            self.games = {}
            self.status = {}
        else:
            del self.list[client_id]
            del self.games[client_id]
            del self.status[client_id]

    def inform_eof_to_nodes(self, data):
        client_id = data.get_client()
        if self.status[client_id] == STATUS_REVIEWING:
            self.eof.total_amount_received[data.get_client()] = {}
            self.eof.total_amount_received[data.get_client()]["reviews"] = self.eof.amount_received_by_node[data.get_client()].get("reviews", 0)
            self.eof.set_expected_total_amount_received(data.get_client(), "reviews", data.get_amount_sent())
            self.check_amounts(data)
            logging.info("Status changed. Now is expecting games")
        else:
            self.status[client_id] = STATUS_REVIEWING
            self.eof.total_amount_received[data.get_client()] = {}
            self.eof.total_amount_received[data.get_client()]["games"] = self.eof.amount_received_by_node[data.get_client()].get("games", 0)
            self.eof.set_expected_total_amount_received(data.get_client(), "games", data.get_amount_sent())
            self.check_amounts(data)
            logging.info("Status changed. Now is expecting reviews")

    def check_amounts(self, data: EOFDTO):
        if self.eof.ready_to_send_eof(data):
            tipo = data.get_type()
            if tipo == "games":
                return
            self.send_result(data.get_client())
            self.eof.total_amount_sent[data.get_client()] = {}
            self.eof.total_amount_sent[data.get_client()]["games"] = self.eof.amount_sent_by_node[data.get_client()].get("games", 0)
            self.send_eof(data)
            self.reset_list(data.get_client())
            self.eof.reset_amounts(data)
            return
        raise PrematureEOFException()
     
    def send_games(self, client_id, games, state, query=0):
        self.eof.update_amount_sent_by_node(client_id, len(games), "games")
        gamesDTO = GamesDTO(client_id=client_id, state_games=state, games_dto=games, query=query)
        self.broker.public_message(sink=self.sink, message=gamesDTO.serialize(), routing_key="default")

    def send_result(self, client_id):
        pass

    def process_reviews(self, data: ReviewsDTO):
        client_id = data.get_client()
        if self.status[client_id] == STATUS_STARTED:
            raise UnfinishedReviewsException()
        self.eof.update_amount_received_by_node(client_id, data.get_amount(), "reviews")
        for review in data.reviews_dto:
            if review.app_id in self.list[client_id]:
                self.list[client_id][review.app_id] += 1

    def process_games(self, data: GamesDTO):
        client_id = data.client_id
        if self.status[client_id] == STATUS_REVIEWING:
            raise UnfinishedGamesException()
        self.eof.update_amount_received_by_node(client_id, data.get_amount(), "games")
        for game in data.games_dto:
            self.list[client_id][game.app_id] = 0
            self.games[client_id][game.app_id] = game.name

    def process_data(self, data):
        client_id = data.get_client()
        if client_id not in self.status:
            self.status[client_id] = STATUS_STARTED
            self.list[client_id] = {}
            self.games[client_id] = {}
        if data.is_reviews():
            self.process_reviews(data)
        if data.is_games():
            self.process_games(data)