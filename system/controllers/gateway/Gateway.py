from common.DTO.GamesRawDTO import GamesRawDTO, OPERATION_TYPE_GAMES_RAW
from common.DTO.ReviewsRawDTO import ReviewsRawDTO, OPERATION_TYPE_REVIEWS_RAW
from common.socket.Socket import Socket
from system.commonsSystem.DTO.enums.OperationType import OperationType
from system.commonsSystem.DTO.DetectDTO import DetectDTO
from system.commonsSystem.DTO.GamesIndexDTO import GamesIndexDTO
from system.commonsSystem.DTO.ReviewsIndexDTO import ReviewsIndexDTO
from system.commonsSystem.broker.Broker import Broker
from common.utils.utils import initialize_log, ALL_DATA_WAS_SENT, DIC_GAME_FEATURES_TO_USE, DIC_REVIEW_FEATURES_TO_USE
from system.commonsSystem.protocol.ServerProtocol import ServerProtocol
from system.commonsSystem.DTO.EOFDTO import EOFDTO
import time
import signal
import logging
import os

QUEUE_GATEWAY_FILTER = "gateway_filterbasic"

EXCHANGE_RESULTQ1_GATEWAY = "platformReducer_gateway"
EXCHANGE_RESULTQ2_GATEWAY = "topAveragePlaytime_gateway"
ROUTING_KEY_RESULT_QUERY_1 = "result.query.1"
ROUTING_KEY_RESULT_QUERY_2 = "result.query.2"
QUEUE_RESULTQ1_GATEWAY = "platformResultq1_gateway"

class Gateway:
    def __init__(self):
        initialize_log(logging_level= os.getenv("LOGGING_LEVEL"))
        self.game_indexes = DIC_GAME_FEATURES_TO_USE
        self.review_indexes = DIC_REVIEW_FEATURES_TO_USE
        self.game_index_init= False
        self.review_index_init= False
        self.there_was_sigterm = False
        signal.signal(signal.SIGTERM, self.handler_sigterm)
        self.broker = Broker()
        self.broker.create_queue(name =QUEUE_GATEWAY_FILTER, durable = True)
        #Exchange query1
        self.broker.create_exchange_and_bind(name_exchange=EXCHANGE_RESULTQ1_GATEWAY,
                                         binding_key =ROUTING_KEY_RESULT_QUERY_1, callback =self.handler_callback_q1())
        
        #Query2
        self.broker.create_queue(name =ROUTING_KEY_RESULT_QUERY_2, durable =True, callback = self.handler_callback_q2())

        self.broker.create_queue(name=QUEUE_RESULTQ1_GATEWAY, durable =True, callback= self.handler_callback_q1())
        self.socket_accepter = Socket(port =12345)
    
    def handler_callback_q1(self):
        def handler_result_q1(ch, method, properties, body):
            result = DetectDTO(body).get_dto()
            if result.operation_type != OperationType.OPERATION_TYPE_PLATFORM_DTO:
                logging.info(f"TODO: HANDLER: EOF 🔚 🏮 🗡️")
            logging.info(f"Action: Gateway Recv result Q1: 🕹️ {result.operation_type.value} success: ✅")
            self.protocol.send_platform_q1(result)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        return handler_result_q1
    
    def handler_callback_q2(self):
        def handler_result_q2(ch, method, properties, body):
            result = DetectDTO(body).get_dto()
            logging.info(f"Action: Gateway Recv result Q2: 🕹️ {result.operation_type.value} success: ✅")
            if result.operation_type != OperationType.OPERATION_TYPE_GROUPER_TOP_AVERAGE_PLAYTIME_DTO:
                logging.info(f"TODO: HANDLER: EOF 🔚 🏮 🗡️")
            logging.info(f"Action: Gateway Recv result Q2: 🕹️ {result.operation_type.value} success: ✅")
            self.protocol.send(result)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        return handler_result_q2

    def accept_a_connection(self):
        logging.info("action: Waiting a client to connect | result: pending ⌚")
        self.socket_peer, addr = self.socket_accepter.accept()
        logging.info("action: Waiting a client to connect | result: success ✅")
        self.protocol = ServerProtocol(self.socket_peer)
    
    def run(self):
        try:
            self.accept_a_connection()
            logging.info(f"action: Gateway started 🔥 | result: sucess ✅")
            while True:
                raw_dto = self.protocol.recv_data_raw()
                if raw_dto == ALL_DATA_WAS_SENT:
                    break
                self.handler_games_and_reviews(raw_dto)
            logging.info(f"action: All customer data was received! 💯 | result: sucess ✅")
            self.broker.start_consuming()
        except Exception as e:
            if self.there_was_sigterm == False:
                logging.error(f"action: Handling a error | result: error ❌ | error: {e}")
        finally:
            self.free_all_resource()
            logging.info("action: Release all resource | result: success ✅")

    def free_all_resource(self):
        self.socket_peer.close()
        self.socket_accepter.close()
        self.broker.close()

    def handler_sigterm(self, signum, frame):
        logging.info(f"action:⚡signal SIGTERM {signum} was received | result: sucess ✅ ")
        self.there_was_sigterm = True
        self.free_all_resource()

    def handler_games_and_reviews(self,raw_dto):
        self.initialize_indexes(raw_dto.operation_type, raw_dto.data_raw)
        a_index_dto = None
        if raw_dto.operation_type == OPERATION_TYPE_GAMES_RAW:
            a_index_dto = GamesIndexDTO(client_id =raw_dto.client_id,
                                            games_raw =raw_dto.data_raw, indexes = self.game_indexes)
        elif raw_dto.operation_type == OPERATION_TYPE_REVIEWS_RAW:
            a_index_dto = ReviewsIndexDTO(client_id =raw_dto.client_id,
                                            reviews_raw =raw_dto.data_raw, indexes =self.review_indexes)
        self.broker.public_message(queue_name =QUEUE_GATEWAY_FILTER, message = a_index_dto.serialize())
        

    def initialize_indexes(self, operation_type, list_items):
        if operation_type == OPERATION_TYPE_GAMES_RAW and self.game_index_init == True:
            return
        elif operation_type == OPERATION_TYPE_REVIEWS_RAW and self.review_index_init == True:
            return
        elif self.game_index_init == False:
            self.find_main_index(list_items, self.game_indexes, self.game_index_init)
            self.game_index_init = True
        elif self.review_index_init == False:
            self.find_main_index(list_items, self.review_indexes, self.review_index_init)
            self.review_index_init = True
    
    def find_main_index(self, list_items, dic_index, index_init):
        for i, element in enumerate(list_items[0]):
                if element in dic_index.keys():
                    dic_index[element] = i
        list_items.pop(0)
