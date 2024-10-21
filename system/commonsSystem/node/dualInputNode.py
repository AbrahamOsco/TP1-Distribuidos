from system.commonsSystem.node.node import Node, PrematureMessage
from system.commonsSystem.DTO.ReviewsDTO import ReviewsDTO
from system.commonsSystem.DTO.GamesDTO import GamesDTO
from system.commonsSystem.DTO.EOFDTO import EOFDTO
from system.commonsSystem.node.routingPolicies.RoutingDefault import RoutingDefault
import logging
import time

STATUS_STARTED = 0
STATUS_REVIEWING = 1

class DualInputNode(Node):
    def __init__(self):
        super().__init__(RoutingDefault())
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

    def inform_eof_to_nodes(self, data, delivery_tag):
        client_id = data.get_client()
        self.clients_pending_confirmations[client_id] = (time.time(), delivery_tag)
        if self.status[client_id] == STATUS_REVIEWING:
            self.check_amounts(data)
            logging.info(f"Status changed for client {data.get_client()}. Finished.")
        else:
            self.status[client_id] = STATUS_REVIEWING
            self.check_amounts(data)
            logging.info(f"Status changed for client {data.get_client()}. Now is expecting reviews")

    def check_amounts(self, data: EOFDTO):
        client = data.get_client()
        if client in self.clients_pending_confirmations:
            self.broker.basic_ack(self.clients_pending_confirmations[client][1])
            del self.clients_pending_confirmations[client]
        if data.get_type() == "games":
            return
        self.send_result(client)
        self.send_eof(data)
        self.reset_list(client)
     
    def send_games(self, client_id, games, state, query=0):
        gamesDTO = GamesDTO(client_id=client_id, state_games=state, games_dto=games, query=query)
        self.broker.public_message(sink=self.sink, message=gamesDTO.serialize(), routing_key="default")

    def send_result(self, client_id):
        pass

    def process_reviews(self, data: ReviewsDTO):
        client_id = data.get_client()
        if self.status[client_id] == STATUS_STARTED:
            logging.error(f"Client {client_id} is still started")
            raise PrematureMessage()
        for review in data.reviews_dto:
            if review.app_id in self.list[client_id]:
                self.list[client_id][review.app_id] += 1

    def process_games(self, data: GamesDTO):
        client_id = data.client_id
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