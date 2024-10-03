from common.DTO.GamesRawDTO import GamesRawDTO, OPERATION_TYPE_GAMES_RAW
from common.DTO.ReviewsRawDTO import ReviewsRawDTO, OPERATION_TYPE_REVIEWS_RAW
from common.utils.utils import initialize_log 
from common.socket.Socket import Socket
from system.commonsSystem.DTO.GamesIndexDTO import GamesIndexDTO
from system.commonsSystem.DTO.ReviewsIndexDTO import ReviewsIndexDTO
from system.commonsSystem.broker.Broker import Broker

from system.commonsSystem.DTO.enums.OperationType import OperationType
from system.commonsSystem.DTO.DetectDTO import DetectDTO

import logging
import os
from system.commonsSystem.protocol.ServerProtocol import ServerProtocol

QUEUE_GATEWAY_FILTER = "gateway_filterbasic"

EXCHANGE_RESULTQ1_GATEWAY = "platformReducer_gateway"
ROUTING_KEY_RESULT_QUERY_1 = "result.query.1"

class Gateway:
    def __init__(self):
        initialize_log(logging_level= os.getenv("LOGGING_LEVEL"))
        self.game_indexes = {"AppID": 0 , "Name": 0, "Windows": 0, "Mac": 0, "Linux": 0,
                            "Genres": 0, "Release date": 0, "Average playtime forever": 0}
        self.review_indexes = { 'app_id':0, 'review_text':0, 'review_score':0 }
        self.game_index_init= False
        self.review_index_init= False
        self.broker = Broker()
        self.broker.create_queue(name =QUEUE_GATEWAY_FILTER, durable = True)
        
        #Exchange query1
        self.broker.create_exchange(name =EXCHANGE_RESULTQ1_GATEWAY, exchange_type='direct')
        queue_result_q1 = self.broker.create_queue(durable =True, callback=self.handler_callback_q1())
        self.broker.bind_queue(exchange_name =EXCHANGE_RESULTQ1_GATEWAY, queue_name =queue_result_q1,
                                binding_key =ROUTING_KEY_RESULT_QUERY_1)

        self.socket_accepter = Socket(port =12345)
    
    def handler_callback_q1(self):
        def handler_result_q1(ch, method, properties, body):
            result = DetectDTO(body).get_dto()
            if result.operation_type != OperationType.OPERATION_TYPE_PLATFORM_DTO:
                logging.info(f"TODO: HANDLER: EOF 🔚 🏮 🗡️")
            logging.info(f"Action: Gateway Recv result Q1: 🕹️ {result.operation_type.value} sucess: ✅")
            self.protocol.send_platform_q1(result)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        return handler_result_q1

        pass

    def accept_a_connection(self):
        logging.info("action: Waiting a client to connect | result: pending ⌚")
        self.socket_peer, addr = self.socket_accepter.accept()
        logging.info("action: Waiting a client to connect | result: success ✅")
        self.protocol = ServerProtocol(self.socket_peer)
    
    def run(self):
        self.accept_a_connection()
        logging.info(f"action: Gateway started 🔥💯 | result: sucess ✅")
        i = 0
        while i < 6:
            raw_dto = self.protocol.recv_data_raw()
            self.initialize_indexes(raw_dto.operation_type, raw_dto.data_raw)
            if raw_dto.operation_type == OPERATION_TYPE_GAMES_RAW:
                games_index_dto = GamesIndexDTO(client_id =raw_dto.client_id,
                                                games_raw =raw_dto.data_raw, indexes = self.game_indexes)
                self.broker.public_message(queue_name =QUEUE_GATEWAY_FILTER, message = games_index_dto.serialize())
            elif raw_dto.operation_type == OPERATION_TYPE_REVIEWS_RAW:
                review_index_dto = ReviewsIndexDTO(client_id =raw_dto.client_id,
                                                reviews_raw =raw_dto.data_raw, indexes =self.review_indexes)
                self.broker.public_message(queue_name =QUEUE_GATEWAY_FILTER, message = review_index_dto.serialize())
            i +=1
        logging.info("start to consuming  before 🧅")
        self.broker.start_consuming()
        logging.info("start to consuming!? after 🥔")

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
