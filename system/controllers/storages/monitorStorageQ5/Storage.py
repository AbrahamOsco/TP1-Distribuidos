from system.commonsSystem.node.node import Node, UnfinishedReviewsException, UnfinishedGamesException, PrematureEOFException
from system.commonsSystem.DTO.ReviewsDTO import ReviewsDTO
from system.commonsSystem.DTO.GamesDTO import GamesDTO, STATE_IDNAME
from system.commonsSystem.DTO.GameIDNameDTO import GameIDNameDTO
from system.commonsSystem.DTO.EOFDTO import EOFDTO, STATE_DEFAULT
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

    def send_eof(self, data):
        logging.info(f"action: send_eof | client: {data.get_client()} | total_amount_sent: {self.amount_sent_by_node[data.get_client()]}")
        self.broker.public_message(sink=self.sink, message=EOFDTO(data.operation_type, data.get_client(),STATE_DEFAULT,"",0,self.amount_sent_by_node[data.get_client()]).serialize(), routing_key='default')

    def inform_eof_to_nodes(self, data):
        if self.status == STATUS_REVIEWING:
            self.total_amount_received[data.get_client()] = {}
            self.total_amount_received[data.get_client()]["reviews"] = self.amount_received_by_node[data.get_client()].get("reviews", 0)
            self.expected_total_amount_received[data.get_client()] = {}
            self.expected_total_amount_received[data.get_client()]["reviews"] = data.get_amount_sent()
            self.check_amounts(data)
            self.amount_received_by_node[data.get_client()] = {}
            self.amount_sent_by_node[data.get_client()] = 0
            logging.info("Status changed. Now is expecting games")
        else:
            self.status = STATUS_REVIEWING
            self.total_amount_received[data.get_client()] = {}
            self.total_amount_received[data.get_client()]["games"] = self.amount_received_by_node[data.get_client()].get("games", 0)
            self.expected_total_amount_received[data.get_client()] = {}
            self.expected_total_amount_received[data.get_client()]["games"] = data.get_amount_sent()
            self.check_amounts(data)
            self.update_amount_sent_by_node(data.get_client(), len(self.list) - int(self.percentile * len(self.list)) -1)
            logging.info("Status changed. Now is expecting reviews")
               
    def check_amounts(self, data: EOFDTO):
        client = data.get_client()
        tipo = data.get_type()
        logging.info(f"action: check_amounts | client: {client} | tipo: {tipo} | total_amount_received: {self.total_amount_received} | expected_total_amount_received: {self.expected_total_amount_received}")
        if self.total_amount_received[client].get(tipo, 0) == self.expected_total_amount_received[client].get(tipo, 0):
            if tipo == "games":
                return
            self.send_result()
            self.send_eof(data)
            self.reset_list()
            self.status = STATUS_STARTED
            self.reset_amounts(client)
            return
        raise PrematureEOFException()
     
    def send_games(self, games):
        gamesDTO = GamesDTO(client_id=self.client_id, state_games=STATE_IDNAME, games_dto=games, query=5)
        self.broker.public_message(sink=self.sink, message=gamesDTO.serialize(), routing_key="default")

    def send_result(self):
        values = sorted(self.list.items(), key=lambda item: (item[1], item[0]))
        index = int(self.percentile * len(values)) -1
        games_to_send = []
        for app_id, _ in values[index:]:
            games_to_send.append(GameIDNameDTO(app_id=app_id, name=self.games[app_id]))
            if len(games_to_send) > 50:
                self.send_games(games_to_send)
                games_to_send = []
        if len(games_to_send) > 0:
            self.send_games(games_to_send)

    def process_reviews(self, data: ReviewsDTO):
        if self.status == STATUS_STARTED:
            raise UnfinishedGamesException()
        self.update_amount_received_by_node(data.get_client(), "reviews", data.get_amount())
        for review in data.reviews_dto:
            if review.app_id in self.list:
                self.list[review.app_id] += 1

    def process_games(self, data: GamesDTO):
        if self.status == STATUS_REVIEWING:
            raise UnfinishedReviewsException()
        self.update_amount_received_by_node(data.get_client(), "games", data.get_amount())
        self.client_id = data.client_id
        for game in data.games_dto:
            self.list[game.app_id] = 0
            self.games[game.app_id] = game.name

    def process_data(self, data):
        if data.is_reviews():
            self.process_reviews(data)
        if data.is_games():
            self.process_games(data)

    def update_total_amount_received(self,client,tipo:str, amount=0):
        if client not in self.total_amount_received:
            self.total_amount_received[client] = {}
        if tipo not in self.total_amount_received[client]:
            self.total_amount_received[client][tipo] = 0
        
        self.total_amount_received[client][tipo] += amount

    def update_totals(self, client:int, tipo:str, amount_received, amount_sent):
        self.update_total_amount_received(client, tipo,amount_received)
        self.update_total_amount_sent(client,tipo, amount_sent)
    
    def update_amount_received_by_node(self,client_id, tipo:str, amount=0):
        if client_id not in self.amount_received_by_node:
            self.amount_received_by_node[client_id] = {}
        if tipo not in self.amount_received_by_node[client_id]:
            self.amount_received_by_node[client_id][tipo] = 0
        
        self.amount_received_by_node[client_id][tipo] += amount