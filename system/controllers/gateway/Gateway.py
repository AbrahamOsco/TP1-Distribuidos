from common.DTO.GamesRawDTO import OPERATION_TYPE_GAMES_RAW
from common.DTO.ReviewsRawDTO import OPERATION_TYPE_REVIEWS_RAW
from common.utils.utils import initialize_log 
from common.socket.Socket import Socket
from system.commonsSystem.DTO.GamesDTO import GamesDTO
from system.commonsSystem.broker.Broker import Broker
import logging
import os
from system.commonsSystem.protocol.ServerProtocol import ServerProtocol

class Gateway:
    def __init__(self):
        initialize_log(logging_level= os.getenv("LOGGING_LEVEL"))
        self.game_indexes = {"AppID": 0 , "Name": 0, "Windows": 0, "Mac": 0, "Linux": 0,
                            "Genres": 0, "Release date": 0, "Average playtime forever": 0}
        self.review_indexes = { 'app_id':0, 'review_text':0, 'review_score':0 }
        self.game_index_init= False
        self.review_index_init= False
        self.sink = os.getenv("SINK")
        self.broker = Broker()
        self.broker.create_sink(type='topic', name=self.sink)
        self.socket_accepter = Socket(port=12345)

    def accept_a_connection(self):
        logging.info("action: Waiting a client to connect | result: pending ⌚")
        self.socket_peer, addr = self.socket_accepter.accept()
        logging.info("action: Waiting a client to connect | result: success ✅")
        self.protocol = ServerProtocol(self.socket_peer)
    
    def run(self):
        while True:
            self.accept_a_connection()
            logging.info(f"action: Gateway started | result: sucess ✅")
            while True:
                raw_dto = self.protocol.recv_data_raw()
                self.initialize_indexes(raw_dto.operation_type, raw_dto.data_raw)
                if raw_dto.operation_type == OPERATION_TYPE_GAMES_RAW:
                    games_dto = GamesDTO(client_id =raw_dto.client_id,
                                                    games_raw =raw_dto.data_raw, indexes = self.game_indexes)
                    self.broker.public_message(sink=self.sink, message = games_dto.serialize(), routing_key="games")
                
                # elif raw_dto.operation_type == OPERATION_TYPE_REVIEWS_RAW:
                #     review_index_dto = ReviewsIndexDTO(client_id =raw_dto.client_id,
                #                                     reviews_raw =raw_dto.data_raw, indexes =self.review_indexes)
                #     self.broker.public_message(sink=self.sink, message = review_index_dto.serialize())
            
    def initialize_indexes(self, operation_type, list_items):
        if operation_type == OPERATION_TYPE_GAMES_RAW and self.game_index_init == True:
            return
        elif operation_type == OPERATION_TYPE_REVIEWS_RAW and self.review_index_init == True:
            return
        elif self.game_index_init == False:
            for i, element in enumerate(list_items[0]):
                if element in self.game_indexes.keys():
                    self.game_indexes[element] = i
            list_items.pop(0)
            self.game_index_init = True
        
        elif self.review_index_init == False:
            for i, element in enumerate(list_items[0]):
                if element in self.review_indexes.keys():
                    self.review_indexes[element] = i
            list_items.pop(0)
            self.review_index_init = True
