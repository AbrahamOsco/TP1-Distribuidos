from system.commonsSystem.node.node import Node, PrematureEOFException
from system.commonsSystem.DTO.RawDTO import RawDTO
from system.commonsSystem.DTO.ReviewsDTO import ReviewsDTO
from system.commonsSystem.DTO.GamesDTO import GamesDTO
from system.commonsSystem.DTO.EOFDTO import EOFDTO, STATE_COMMIT, STATE_DEFAULT, STATE_OK
from system.commonsSystem.DTO.enums.OperationType import OperationType
import logging

class Filter(Node):
    def __init__(self):
        super().__init__()
        self.game_indexes = {0:"app_id" , 1:"name", 2:"release_date", 17: "windows", 18: "mac", 19: "linux", 29: "avg_playtime_forever", 36: "genres"}
        self.review_indexes = {0:'app_id', 2:'review_text', 3:'review_score'}
    
    def send_eof(self, data):
        tipo = data.get_type()
        logging.info(f"action: send_eof | client: {data.get_client()} | total_amount_sent: {self.total_amount_sent[data.get_client()][tipo]}")
        self.broker.public_message(sink=self.sink, message=EOFDTO(data.operation_type, data.get_client(),STATE_DEFAULT,"",0,self.total_amount_sent[data.get_client()][tipo]).serialize(), routing_key=tipo)

    def send_eof_confirmation(self, data: EOFDTO):
        client = data.get_client()
        tipo = data.get_type()
        amount_received_by_node = self.amount_received_by_node[client][tipo]
        amount_sent_by_node = self.amount_sent_by_node[client][tipo]
        logging.info(f"action: send_eof_confirmation | client: {client} | amount_received_by_node: {amount_received_by_node} | amount_sent_by_node: {amount_sent_by_node}")
        self.broker.public_message(sink=self.node_name + "_eofs", message=EOFDTO(data.operation_type, client,STATE_OK,"",amount_received_by_node,amount_sent_by_node).serialize())

    def send_reviews(self, data: RawDTO):
        self.update_amount_received_by_node(data.get_client(), "reviews", len(data.raw_data))
        reviews = ReviewsDTO.from_raw(data, self.review_indexes)
        if len(reviews.reviews_dto) == 0:
            return
        self.broker.public_message(sink=self.sink, message=reviews.serialize(), routing_key="reviews")
        self.update_amount_sent_by_node(data.get_client(), "reviews", len(reviews.reviews_dto))

    def send_games(self, data: RawDTO):
        self.update_amount_received_by_node(data.get_client(), "games", len(data.raw_data))
        games = GamesDTO.from_raw(data, self.game_indexes)
        if len(games.games_dto) == 0:
            return
        self.broker.public_message(sink=self.sink, message=games.serialize(), routing_key="games")
        self.update_amount_sent_by_node(data.get_client(), "games", len(games.games_dto))

    def update_amount_sent_by_node(self,client_id, tipo:str, amount=0):
        if client_id not in self.amount_sent_by_node:
            self.amount_sent_by_node[client_id] = {}
        if tipo not in self.amount_sent_by_node[client_id]:
            self.amount_sent_by_node[client_id][tipo] = 0
        
        self.amount_sent_by_node[client_id][tipo] += amount

    def update_amount_received_by_node(self,client_id, tipo:str, amount=0):
        if client_id not in self.amount_received_by_node:
            self.amount_received_by_node[client_id] = {}
        if tipo not in self.amount_received_by_node[client_id]:
            self.amount_received_by_node[client_id][tipo] = 0
        
        self.amount_received_by_node[client_id][tipo] += amount

    def process_data(self, data: RawDTO):
        if data.is_games():
            self.send_games(data)
        elif data.is_reviews():
            self.send_reviews(data)
    
    def update_total_amount_received(self,client,tipo:str, amount=0):
        if client not in self.total_amount_received:
            self.total_amount_received[client] = {}
        if tipo not in self.total_amount_received[client]:
            self.total_amount_received[client][tipo] = 0
        
        self.total_amount_received[client][tipo] += amount
 
    def update_total_amount_sent(self,client,tipo:str, amount=0):
        if client not in self.total_amount_sent:
            self.total_amount_sent[client] = {}
        if tipo not in self.total_amount_sent[client]:
            self.total_amount_sent[client][tipo] = 0
        
        self.total_amount_sent[client][tipo] += amount

    def check_confirmations(self, data: EOFDTO):
        tipo = data.get_type()
        self.update_totals(data.get_client(), tipo, data.get_amount_received(), data.get_amount_sent())   
        self.confirmations += 1
        logging.info(f"action: check_confirmations | client: {data.get_client()} | confirmations: {self.confirmations}")
        if self.confirmations == self.amount_of_nodes:
            self.check_amounts(data)

    def update_totals(self, client:int, tipo:str, amount_received, amount_sent):
        self.update_total_amount_received(client, tipo,amount_received)
        self.update_total_amount_sent(client,tipo, amount_sent)

    def update_expected_total_amount_received(self, client:int, tipo:str, amount):
        if client not in self.expected_total_amount_received:
            self.expected_total_amount_received[client] = {}
        self.expected_total_amount_received[client][tipo] = amount

    def check_amounts(self, data: EOFDTO):
        client = data.get_client()
        tipo = data.get_type()
        if self.total_amount_received[client].get(tipo, 0) == self.expected_total_amount_received[client].get(tipo, 0):
            self.pre_eof_actions(client)
            self.send_eof(data)
            self.clients.remove(client)
            self.clients_pending_confirmations.remove(client)
            self.confirmations = 0
            self.reset_amounts(data)
            if self.amount_of_nodes > 1:
                self.send_eof_finish(data)
            return
        if self.amount_of_nodes < 2:
            raise PrematureEOFException()
        self.reset_totals(client, tipo)
        self.update_totals(client, tipo, self.amount_received_by_node[client].get(tipo, 0), self.amount_sent_by_node[client].get(tipo, 0))
        self.ask_confirmations(data)
    
    def reset_totals(self, client, tipo):
        if client in self.total_amount_received and tipo in self.total_amount_received[client]:
            del self.total_amount_received[client][tipo]
        if client in self.total_amount_sent and tipo in self.total_amount_sent[client]:
            del self.total_amount_sent[client][tipo]

    def inform_eof_to_nodes(self, data):
        client = data.get_client()
        logging.info(f"action: inform_eof_to_nodes | client: {client}")
        tipo = data.get_type()
        self.reset_totals(client, tipo)
        self.update_totals(client, tipo, self.amount_received_by_node[client].get(tipo, 0), self.amount_sent_by_node[client].get(tipo, 0))
        logging.info(f"exped total amount received: {data.get_amount_sent()}")
        self.update_expected_total_amount_received(client, tipo, data.get_amount_sent())
        self.clients_pending_confirmations.append(client)
        if self.amount_of_nodes < 2:
            self.check_amounts(data)
            return
        self.ask_confirmations(data)