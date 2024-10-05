from system.commonsSystem.DTO.enums.OperationType import OperationType
from common.utils.utils import initialize_log
from system.commonsSystem.DTO.DetectDTO import DetectDTO
from system.commonsSystem.DTO.CalculatorDTO import CalculatorDTO, STATUS_REQUEST, STATUS_RESPONSE
from system.commonsSystem.DTO.EOFDTO import EOFDTO
from system.commonsSystem.handlerEOF.HandlerEOF import HandlerEOF
from system.commonsSystem.DTO.GamesDTO import GamesDTO, STATE_GAMES_INITIAL
from system.commonsSystem.broker.Broker import Broker
import logging
import os
import signal

QUEUE_GATEWAY_FILTER = "gateway_filterbasic"
QUEUE_FILTER_SELECTQ1 = "filterbasic_selectq1"
QUEUE_FILTER_SELECTQ2345 = "filterbasic_selectq2345"
EXCHANGE_FILTER_BASIC = "Exchange_gateway_filterbasic"

class FilterBasic:
    def __init__(self):
        initialize_log(logging_level= os.getenv("LOGGING_LEVEL"))
        self.id = os.getenv("NODE_ID")
        self.amounts_indivdual = {"games": 0, "reviews": 0}
        self.amount_total_current = {"games":0 , "reviews": 0}
        self.amount_total_definitive = {"games":0, "reviews": 0}
        self.recv_calculator = 0
        self.total_nodes = 3
        self.eof_dto = None
        self.i_am_lider = False
        self.game_indexes = {}
        self.review_indexes = {}
        self.game_index_init= False
        self.review_index_init= False
        signal.signal(signal.SIGTERM, self.handler_sigterm)
        self.broker = Broker()
        
        self.broker.create_exchange(name =EXCHANGE_FILTER_BASIC, exchange_type='fanout')
        anonymous_queue = self.broker.create_queue(durable =True, callback=self.callback_eof_calculator())
        self.broker.bind_queue(exchange_name =EXCHANGE_FILTER_BASIC, queue_name =anonymous_queue)

        self.broker.create_queue(name =QUEUE_GATEWAY_FILTER, durable = True, callback =self.callback_filter_basic())
        self.broker.create_queue(name =QUEUE_FILTER_SELECTQ1, durable = True)
        self.handler_eof_games = HandlerEOF(target="games", broker =self.broker,
                                 node_id =self.id, exchange_name =EXCHANGE_FILTER_BASIC, name_next_queue =QUEUE_FILTER_SELECTQ1)
        self.broker.create_queue(name =QUEUE_FILTER_SELECTQ2345, durable = True)
        self.wait_for_select = False

    def callback_eof_calculator(self):
        def handler_message(ch, method, properties, body):
            result_dto = DetectDTO(body).get_dto()
            self.handler_eof_games.run(result_dto)
            ch.basic_ack(delivery_tag =method.delivery_tag)
        return handler_message

    def callback_filter_basic(self):
        def handler_message(ch, method, properties, body):
            result_dto = DetectDTO(body).get_dto()
            logging.info(f"ResultDTO: {result_dto} {result_dto.operation_type} 🏑 🌵")
            if (result_dto.operation_type == OperationType.OPERATION_TYPE_EOF_INITIAL_DTO):
                self.handler_eof_games.initialize_lider(result_dto)
                self.broker.public_message(exchange_name =EXCHANGE_FILTER_BASIC, message = CalculatorDTO(result_dto.client_id).serialize())
            else: 
                batch_filtered = self.filter_fields_item(result_dto)
                self.send_batch_data(batch_filtered, result_dto.operation_type, result_dto.client_id)
            ch.basic_ack(delivery_tag =method.delivery_tag)
        return handler_message


    def send_batch_data(self, data_filtered, operation_type, client_id):
        if operation_type == OperationType.OPERATION_TYPE_GAMES_INDEX_DTO:
            gamesDTO = GamesDTO(games_raw =data_filtered, client_id =client_id, state_games =STATE_GAMES_INITIAL)
            self.broker.public_message(queue_name= QUEUE_FILTER_SELECTQ1, message = gamesDTO.serialize())
            self.broker.public_message(queue_name= QUEUE_FILTER_SELECTQ2345, message = gamesDTO.serialize())
            self.handler_eof_games.add_new_processing()

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
            basic_game = self.drop_basic_item(a_game, indexes)
            batch_item.append(basic_game)

    def drop_basic_item(self, a_item, dic_indexes):
        #logging.info(f"Dic Indexes 🦃 : {dic_indexes}")
        item_basic = []
        for i in range(len(a_item)):
            if i in dic_indexes.values():
                #logging.info(f"index: {i} value: {a_item[i]}")
                item_basic.append(a_item[i])
        return item_basic    

    def handler_sigterm(self, signum, frame):
        logging.info(f"action:⚡signal SIGTERM {signum} was received | result: sucess ✅ ")
        self.broker.close()

    def run(self):
        self.broker.start_consuming()
        logging.info(f"action: Filter basic started to consume | result: sucess ✅")
    

#    self.broker.public_message(exchange_name =FILTERBASIC_INPUT,
#                                routing_key =RK_GATEWAY_SELECTQ2345, message = "Some data 🩹 🅰️ 🥑")
#
#elif operation_type == OperationType.OPERATION_TYPE_REVIEWS_INDEX_DTO:
#    self.broker.public_message(exchange_name =FILTERBASIC_INPUT,
#                                 routing_key =RK_GATEWAY_SELECTQ345, message ="Some data 🛡️ 👨‍🔧 🗡️")
# for each game se cumple:  ['AppID', 'Name', 'Release date', 'Windows', 'Mac', 'Linux', 'Average playtime forever', 'Genres']
# example: ['1659180', 'TD Worlds', 'Jan 9, 2022', 'True', 'False', 'False', '0', 'Indie,Strategy']
