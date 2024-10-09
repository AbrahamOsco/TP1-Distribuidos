from system.commonsSystem.node.node import Node
from system.commonsSystem.DTO.RawDTO import RawDTO
from system.commonsSystem.DTO.ReviewsDTO import ReviewsDTO
from system.commonsSystem.DTO.GamesDTO import GamesDTO
from system.commonsSystem.DTO.EOFDTO import EOFDTO
from system.commonsSystem.DTO.enums.OperationType import OperationType
import logging

class Filter(Node):
    def __init__(self):
        super().__init__()
        self.game_indexes = {0:"app_id" , 1:"name", 2:"release_date", 17: "windows", 18: "mac", 19: "linux", 29: "avg_playtime_forever", 36: "genres"}
        self.review_indexes = {0:'app_id', 2:'review_text', 3:'review_score'}
    
    def send_reviews(self, data: RawDTO):
        self.update_amount_received_by_node(data.get_client(), "reviews", len(data.raw_data))
        reviews = ReviewsDTO.from_raw(data, self.review_indexes)
        if len(reviews.reviews_dto) == 0:
            return
        self.broker.public_message(sink=self.sink, message=reviews.serialize(), routing_key="reviews")
        self.update_amount_sent_by_node(data.get_client(), "reviews", len(reviews.reviews_dto()))

    def send_games(self, data: RawDTO):
        self.update_amount_received_by_node(data.get_client(), "games", len(data.raw_data))
        games = GamesDTO.from_raw(data, self.game_indexes)
        if len(games.games_dto) == 0:
            return
        self.broker.public_message(sink=self.sink, message=games.serialize(), routing_key="games")
        self.update_amount_sent_by_node(data.get_client(), "games", len(games.games_dto))

    def update_amount_sent_by_node(self,client_id, type:str, amount=0):
        if client_id not in self.amount_sent_by_node:
            self.amount_sent_by_node[client_id] = {}
        if type not in self.amount_sent_by_node[client_id]:
            self.amount_sent_by_node[client_id][type] = 0
        
        self.amount_sent_by_node[client_id][type] += amount

    def update_amount_received_by_node(self,client_id, type:str, amount=0):
        if client_id not in self.amount_received_by_node:
            self.amount_received_by_node[client_id] = {}
        if type not in self.amount_received_by_node[client_id]:
            self.amount_received_by_node[client_id][type] = 0
        
        self.amount_received_by_node[client_id][type] += amount

    def process_data(self, data: RawDTO):
        if data.is_games():
            self.send_games(data)
        elif data.is_reviews():
            self.send_reviews(data)
    
    # def inform_eof_to_nodes(self, data):
    #     if data.is_games_EOF():
    #         self.broker.public_message(sink=self.sink, message=EOFDTO(type=OperationType.OPERATION_TYPE_GAMES_EOF_DTO, client=data.client_id, confirmation=False).serialize(), routing_key="games")
    #     elif data.is_reviews_EOF():
    #         self.broker.public_message(sink=self.sink, message=EOFDTO(type=OperationType.OPERATION_TYPE_REVIEWS_EOF_DTO, client=data.client_id, confirmation=False).serialize(), routing_key="reviews")
        
    #     client = data.get_client()
    #     logging.info(f"action: inform_eof_to_nodes | client: {client}")
    #     self.reset_totals()
    #     self.update_totals(client, self.amount_received_by_node[client], self.amount_sent_by_node[client])
    #     self.expected_total_amount_received[client] = data.get_amount_sent()
    #     self.clients_pending_confirmations.append(client)
    #     if self.amount_of_nodes < 2:
    #         self.check_amounts(data)
    #         return
    #     self.ask_confirmations(data)