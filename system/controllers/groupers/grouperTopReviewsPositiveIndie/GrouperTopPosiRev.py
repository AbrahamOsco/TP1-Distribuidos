from common.utils.utils import initialize_log
from system.commonsSystem.DTO.enums.OperationType import OperationType
from system.commonsSystem.DTO.GamesDTO import GamesDTO
from system.commonsSystem.DTO.GameDTO import GameDTO
from system.commonsSystem.broker.Broker import Broker
from system.commonsSystem.DTO.DetectDTO import DetectDTO
from system.commonsSystem.DTO.enums.StateGame import StateGame
from system.commonsSystem.handlerEOF.HandlerEOF import HandlerEOF
from system.commonsSystem.utils.utils import eof_calculator, handler_sigterm_default
from system.commonsSystem.DTO.ResultQueryDTO import ResultQueryDTO, RESULT_TOP
from system.commonsSystem.utils.TopResults import TopResults

import logging
import os
import signal

QUEUE_MONITORSTORAGEQ3_GROUPER_TOPPOSIREVIEW = "monitorStorageQ3_grouperReview"
QUEUE_RESULTQ3_GATEWAY = "resultq3_gateway"
TOP_SIZE_QUERY3 = 5

class GrouperTopPosiRev:
    def __init__(self):
        initialize_log(logging_level= os.getenv("LOGGING_LEVEL"))
        self.id = os.getenv("NODE_ID")
        self.broker = Broker()
        signal.signal(signal.SIGTERM, handler_sigterm_default(self.broker))
        self.top_games = TopResults(size = TOP_SIZE_QUERY3)
        self.broker.create_queue(name =QUEUE_MONITORSTORAGEQ3_GROUPER_TOPPOSIREVIEW, callback = self.handler_calculate_top_avg_playtime())
        self.broker.create_queue(name =QUEUE_RESULTQ3_GATEWAY)

    def handler_calculate_top_avg_playtime(self):
        def handler_message(ch, method, properties, body):
            result_dto = DetectDTO(body).get_dto()
            if result_dto.operation_type == OperationType.OPERATION_TYPE_EOF_DTO:
                games_order_top = self.top_games.sort()
                result_queryDTO = ResultQueryDTO(client_id =result_dto.client_id, data =games_order_top, status =RESULT_TOP)
                self.broker.public_message(queue_name =QUEUE_RESULTQ3_GATEWAY, message =result_queryDTO.serialize() )
                logging.info(f"Respeustas QUERY 3 IN GROUPER {games_order_top} 🧮🧮🧮🧮🧮🧮🧮🧮🧮🧮🧮🧮🧮🧮🧮🧮🧮🧮🧮")
            else:
                self.top_games.try_to_insert_top(result_dto)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        return handler_message

    def run(self):
        self.broker.start_consuming()
