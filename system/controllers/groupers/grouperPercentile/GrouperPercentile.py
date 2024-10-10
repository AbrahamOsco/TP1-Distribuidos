from system.commonsSystem.DTO.enums.OperationType import OperationType
from common.utils.utils import initialize_log, ALL_GAMES_WAS_SENT
from system.commonsSystem.DTO.GamesDTO import GamesDTO
from system.commonsSystem.broker.Broker import Broker
from system.commonsSystem.DTO.DetectDTO import DetectDTO
from system.commonsSystem.handlerEOF.HandlerEOF import HandlerEOF
from system.commonsSystem.DTO.PlatformDTO import PlatformDTO
from system.commonsSystem.utils.utils import handler_sigterm_default
from system.commonsSystem.utils.TopResults import TopResults
from system.commonsSystem.DTO.ResultQueryDTO import ResultQueryDTO, RESULT_TOP

import os
import logging
import signal 
import math
QUEUE_MONITORSTORAGEQ5_GROUPERPERCENTIL = "monitorStorageQ5_grouperPercentil"
QUEUE_RESULTQ5_GATEWAY = "resultq5_gateway"
#QUEUE_PLATFORMCOUNTER_REDUCER = "platformCounter_platformReducer"
#EXCHANGE_EOF_GROUPER_PERCENTILE = "Exchange_platformCounter"

PERCENTILE_TOP_10_PERCENTAGE = 0.1 # percentile 90

class GrouperPercentile:
    def __init__(self):
        initialize_log(logging_level= os.getenv("LOGGING_LEVEL"))
        self.id = os.getenv("NODE_ID")
        #self.total_nodes = 2
        self.total_games = 0
        self.games_up_percentile = None
        self.registered_client = False
        self.broker = Broker()
        signal.signal(signal.SIGTERM, handler_sigterm_default(self.broker))
        self.broker.create_queue(name =QUEUE_MONITORSTORAGEQ5_GROUPERPERCENTIL, callback =self.handler_games_for_percentil())
        self.broker.create_queue(name =QUEUE_RESULTQ5_GATEWAY)

        #self.broker.create_fanout_and_bind(name_exchange =EXCHANGE_EOF_PLATFORM_COUNTER, callback =self.callback_eof_calculator())
        #self.handler_eof_games = HandlerEOF(broker =self.broker, node_id =self.id, target_name ="Games", total_nodes= self.total_nodes,
        #                        exchange_name =EXCHANGE_EOF_PLATFORM_COUNTER, next_queues =[QUEUE_PLATFORMCOUNTER_REDUCER])

    def handler_games_for_percentil(self):
        def handler_message(ch, method, properties, body):
            result_dto = DetectDTO(body).get_dto()
            if result_dto.operation_type == OperationType.OPERATION_TYPE_EOF_DTO:
                games_order_top = self.games_up_percentile.sort()
                logging.info(f"Recibi eof!! in GrouperPercentile 🥹 🅰️🥹 🅰️🥹 🅰️🥹 🅰️ {games_order_top} ")
                result_queryDTO = ResultQueryDTO(client_id =result_dto.client_id, data =games_order_top, status =RESULT_TOP)
                self.broker.public_message(queue_name =QUEUE_RESULTQ5_GATEWAY, message =result_queryDTO.serialize())
                logging.info(f"Respeustas QUERY 5 IN GROUPER {games_order_top} Ⓜ️Ⓜ️Ⓜ️Ⓜ️Ⓜ️Ⓜ️Ⓜ️Ⓜ️")
                #self.handler_eof_games.init_leader_and_push_eof(result_dto)  
            else:
                self.calculate_percentile(result_dto)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        return handler_message

    def calculate_percentile(self, games_with_reviews):
        if self.games_up_percentile is None:
            self.total_games = games_with_reviews.size_games
            size_top_games = math.ceil(games_with_reviews.size_games * PERCENTILE_TOP_10_PERCENTAGE)
            self.games_up_percentile = TopResults(size = size_top_games)
        self.games_up_percentile.try_to_insert_top(games_with_reviews)
        logging.info(f"Current: {self.total_games} {self.games_up_percentile.top_data}")


    def run(self):
        self.broker.start_consuming()
