from system.commonsSystem.DTO.enums.OperationType import OperationType
from common.utils.utils import initialize_log, ALL_GAMES_WAS_SENT, ALL_REVIEWS_WAS_SENT
from system.commonsSystem.DTO.DetectDTO import DetectDTO
from system.commonsSystem.DTO.EOFDTO import EOFDTO 
from system.commonsSystem.handlerEOF.HandlerEOF import HandlerEOF
from system.commonsSystem.DTO.GamesDTO import GamesDTO, STATE_GAMES_INITIAL
from system.commonsSystem.broker.Broker import Broker
import logging
import os
import signal


QUEUE_GATEWAY_FILTER = "gateway_filterBasic"
QUEUE_FILTER_SELECTQ1 = "filterBasic_selectq1"
QUEUE_FILTER_SELECTQ2345 = "filterBasic_selectq2345"
QUEUE_FILTER_SCORE_POSITIVE = "filterBasic_scorePositive"
QUEUE_FILTER_SCORE_NEGATIVE = "filterBasic_scoreNegative"

EXCHANGE_EOF_FILTER_BASIC = "Exchange_filterBasic"

class FilterBasic:
    def __init__(self):
        initialize_log(logging_level= os.getenv("LOGGING_LEVEL"))
        self.id = os.getenv("NODE_ID")
        self.total_nodes = int(os.getenv("TOTAL_NODES"))
        self.game_indexes = {}
        self.review_indexes = {}
        self.genres_position = -1
        self.name_position = -1
        self.game_index_init= False
        self.review_index_init= False
        signal.signal(signal.SIGTERM, self.handler_sigterm)
        self.broker = Broker()
        self.broker.create_queue(name =QUEUE_GATEWAY_FILTER, callback =self.callback_filter_basic())
        self.broker.create_queue(name =QUEUE_FILTER_SELECTQ1)
        
        self.broker.create_fanout_and_bind(name_exchange=EXCHANGE_EOF_FILTER_BASIC, callback=self.callback_eof_calculator())
        self.handler_eof_games = HandlerEOF(broker =self.broker, node_id =self.id, target_name ="Games", total_nodes= self.total_nodes,
                                exchange_name =EXCHANGE_EOF_FILTER_BASIC, next_queues =[QUEUE_FILTER_SELECTQ1, QUEUE_FILTER_SELECTQ2345])
        self.handler_eof_reviews = HandlerEOF(broker =self.broker, node_id =self.id, target_name ="Reviews", total_nodes= self.total_nodes,
                                exchange_name =EXCHANGE_EOF_FILTER_BASIC, next_queues =[QUEUE_FILTER_SELECTQ1])
        self.broker.create_queue(name =QUEUE_FILTER_SELECTQ2345)

    def callback_eof_calculator(self):
        def handler_message(ch, method, properties, body):
            result_dto = DetectDTO(body).get_dto()
            if result_dto.target_type == ALL_GAMES_WAS_SENT:
                self.handler_eof_games.run(calculatorDTO =result_dto)
            elif result_dto.target_type == ALL_REVIEWS_WAS_SENT:
                self.handler_eof_reviews.run(calculatorDTO =result_dto)
            ch.basic_ack(delivery_tag =method.delivery_tag)
        return handler_message

    def callback_filter_basic(self):
        def handler_message(ch, method, properties, body):
            result_dto = DetectDTO(body).get_dto()
            if (result_dto.operation_type == OperationType.OPERATION_TYPE_EOF_INITIAL_DTO and
                result_dto.old_operation_type == ALL_GAMES_WAS_SENT):
                self.handler_eof_games.init_lider_and_push_eof(result_dto)
            elif (result_dto.operation_type == OperationType.OPERATION_TYPE_EOF_INITIAL_DTO and
                result_dto.old_operation_type == ALL_REVIEWS_WAS_SENT):
                self.handler_eof_reviews.init_lider_and_push_eof(result_dto)
            else: 
                self.send_batch_data(result_dto)
            ch.basic_ack(delivery_tag =method.delivery_tag)
        return handler_message


    def send_batch_data(self, result_dto):
        data_filtered = self.filter_fields_item(result_dto)
        if result_dto.operation_type == OperationType.OPERATION_TYPE_GAMES_INDEX_DTO:
            gamesDTO = GamesDTO(games_raw =data_filtered, client_id =result_dto.client_id, state_games =STATE_GAMES_INITIAL)
            self.broker.public_message(queue_name= QUEUE_FILTER_SELECTQ1, message = gamesDTO.serialize())
            self.broker.public_message(queue_name= QUEUE_FILTER_SELECTQ2345, message = gamesDTO.serialize())
            self.handler_eof_games.add_new_processing()
        elif result_dto.operation_type == OperationType.OPERATION_TYPE_REVIEWS_INDEX_DTO:
            self.handler_eof_reviews.add_new_processing()

    def filter_fields_item(self, result_dto):
        batch_item = []
        if result_dto.operation_type == OperationType.OPERATION_TYPE_GAMES_INDEX_DTO:
            if not self.game_index_init:
                self.game_indexes = result_dto.indexes
                self.game_index_init = True
            self.filter_fields_by(batch_item, result_dto, self.game_indexes)
        elif result_dto.operation_type == OperationType.OPERATION_TYPE_REVIEWS_INDEX_DTO:
            if not self.review_index_init:
                self.review_indexes = result_dto.indexes
                self.review_index_init = True
            self.filter_fields_by(batch_item, result_dto, self.review_indexes)
        return batch_item

    def filter_fields_by(self, batch_item, result_dto, indexes):
        for a_game in result_dto.data_raw:
            basic_item = self.drop_basic_item(a_game, indexes)
            if (not self.some_features_is_empty(basic_item)):
                batch_item.append(basic_item)
            elif (len(basic_item) == len(self.review_indexes)):
                batch_item.append(basic_item)

    def some_features_is_empty(self, basic_item):
        if  len(basic_item) == len(self.game_indexes) and (basic_item[self.genres_position] == "" or basic_item[self.name_position] == ""):
            return True

    def drop_basic_item(self, a_item, dic_indexes):
        #logging.info(f"Dic Indexes 🦃 : {dic_indexes}")
        item_basic = []
        position = 0
        for i in range(len(a_item)):
            if i in dic_indexes.values():
                if self.genres_position == -1 and len(dic_indexes) == len(self.game_indexes) and i == dic_indexes["Genres"] :
                    self.genres_position = position
                elif self.name_position == -1 and len(dic_indexes) == len(self.game_indexes) and i == dic_indexes["Name"]:
                    self.name_position = position
                item_basic.append(a_item[i])
                position +=1
        return item_basic    

    def handler_sigterm(self, signum, frame):
        logging.info(f"action:⚡signal SIGTERM {signum} was received | result: sucess ✅ ")
        self.broker.close()

    def run(self):
        self.broker.start_consuming()
    
